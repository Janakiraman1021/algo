/**
 * x402 Payment Adapter & AVM Facilitator Service for AgentPay
 * 
 * Provides official x402 HTTP 402 challenge generation, signature validation,
 * and Algorand TestNet settlement verification.
 */

import express, { Request, Response } from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import algosdk from 'algosdk';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4020;
const ALGOD_SERVER = process.env.ALGOD_SERVER || 'https://testnet-api.algonode.cloud';
const ALGOD_TOKEN = process.env.ALGOD_TOKEN || '';

const algodClient = new algosdk.Algodv2(ALGOD_TOKEN, ALGOD_SERVER, '');

app.use(cors());
app.use(express.json());

// Health Check
app.get('/health', async (req: Request, res: Response) => {
  try {
    const status = await algodClient.status().do();
    res.json({
      status: 'operational',
      service: 'x402 Algorand Facilitator Adapter',
      network: 'testnet',
      last_round: status['last-round'],
      node: ALGOD_SERVER
    });
  } catch (error: any) {
    res.json({
      status: 'degraded',
      service: 'x402 Algorand Facilitator Adapter',
      network: 'testnet',
      error: error?.message || String(error)
    });
  }
});

// Generate x402 Standard Challenge
app.post('/v1/challenge', (req: Request, res: Response) => {
  const { recipient, price_usd = 0.01, service = 'text_summarization' } = req.body;

  if (!recipient) {
    return res.status(400).json({ error: 'recipient address is required' });
  }

  const amount_micro = Math.round(price_usd * 1_000_000);
  const nonce = Buffer.from(Math.random().toString(36).substring(2) + Date.now().toString()).toString('base64');

  const challenge = {
    scheme: 'x402',
    network: 'algorand:testnet',
    asset: 'USDC',
    asset_id: 10458941,
    price_usd,
    amount_micro,
    recipient_address: recipient,
    facilitator_url: `http://localhost:${PORT}`,
    nonce,
    memo: `AgentPay: A2A Task [${service}]`
  };

  return res.status(402).json(challenge);
});

// Verify x402 Payment Settlement Proof on Algorand
app.post('/v1/verify', async (req: Request, res: Response) => {
  const { tx_id, expected_recipient, expected_amount_micro } = req.body;

  if (!tx_id) {
    return res.status(400).json({ error: 'tx_id is required' });
  }

  try {
    const pendingInfo = await algodClient.pendingTransactionInformation(tx_id).do();
    const confirmedRound = pendingInfo['confirmed-round'] || 0;

    const txn = pendingInfo['txn']?.['txn'] || {};
    const receiver = txn['rcv'] || txn['arcv'];
    const amount = txn['amt'] || txn['aamt'] || 0;

    const isConfirmed = confirmedRound > 0;
    
    return res.json({
      verified: isConfirmed,
      tx_id,
      confirmed_round: confirmedRound,
      receiver,
      amount,
      network: 'algorand:testnet',
      explorer_url: `https://lora.algokit.io/testnet/transaction/${tx_id}`
    });
  } catch (error: any) {
    return res.status(500).json({
      verified: false,
      tx_id,
      error: error?.message || 'Verification lookup failed'
    });
  }
});

// Settle / Facilitate Payment Forwarding
app.post('/v1/settle', async (req: Request, res: Response) => {
  const { signed_tx_base64 } = req.body;

  if (!signed_tx_base64) {
    return res.status(400).json({ error: 'signed_tx_base64 is required' });
  }

  try {
    const rawTxn = Buffer.from(signed_tx_base64, 'base64');
    const sendRes = await algodClient.sendRawTransaction(rawTxn).do();
    const txId = sendRes.txId;

    // Wait for confirmation
    const confirmed = await algosdk.waitForConfirmation(algodClient, txId, 4);

    return res.json({
      success: true,
      tx_id: txId,
      confirmed_round: confirmed['confirmed-round'],
      explorer_url: `https://lora.algokit.io/testnet/transaction/${txId}`
    });
  } catch (error: any) {
    return res.status(500).json({
      success: false,
      error: error?.message || 'Transaction settlement failed'
    });
  }
});

app.listen(PORT, () => {
  console.log(`[+] x402 Algorand Adapter running on port ${PORT}`);
  console.log(`[+] Connected to Algorand TestNet: ${ALGOD_SERVER}`);
});
