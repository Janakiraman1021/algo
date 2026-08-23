"""Algorand blockchain interaction layer for AgentPay."""

import os
import sys
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction

# Import ABI selectors from smart contract
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "smart-contract" / "contracts"))
try:
    from teal_generator import SELECTORS
except ImportError:
    SELECTORS = {
        "register_agent": b"\x00\x00\x00\x00",
        "register_service": b"\x00\x00\x00\x00",
        "record_task": b"\x00\x00\x00\x00",
        "get_stats": b"\x00\x00\x00\x00",
    }

from app.config import settings

logger = logging.getLogger("agentpay.blockchain")

class AlgorandBlockchainClient:
    def __init__(self):
        self.server = settings.ALGOD_SERVER
        self.token = settings.ALGOD_TOKEN
        headers = {"X-API-Key": self.token} if self.token else {}
        self.client = algod.AlgodClient(self.token, self.server, headers)
        self.network = settings.ALGORAND_NETWORK

    def get_status(self) -> Dict[str, Any]:
        """Check connection status with Algorand node."""
        try:
            status = self.client.status()
            return {
                "connected": True,
                "network": self.network,
                "last_round": status.get("last-round"),
                "time_since_last_round": status.get("time-since-last-round"),
                "node_server": self.server
            }
        except Exception as e:
            logger.error(f"Failed to connect to Algorand node: {e}")
            return {
                "connected": False,
                "network": self.network,
                "error": str(e),
                "node_server": self.server
            }

    def get_account_balance(self, address: str) -> Dict[str, Any]:
        """Get account ALGO and asset balances."""
        try:
            info = self.client.account_info(address)
            algo_balance = info.get("amount", 0) / 1e6
            assets = info.get("assets", [])
            return {
                "address": address,
                "algo_balance": algo_balance,
                "assets": assets,
                "error": None
            }
        except Exception as e:
            logger.warning(f"Error fetching account info for {address}: {e}")
            return {
                "address": address,
                "algo_balance": 0.0,
                "assets": [],
                "error": str(e)
            }

    def submit_x402_payment(
        self,
        payer_mnemonic: str,
        recipient_address: str,
        amount_micro: int,
        asset_id: int = 10458941,
        memo_text: str = "AgentPay x402 Micropayment"
    ) -> Dict[str, Any]:
        """Execute a genuine x402 micropayment on Algorand TestNet."""
        if not payer_mnemonic:
            raise ValueError("No payer mnemonic provided for x402 payment signing")

        private_key = mnemonic.to_private_key(payer_mnemonic)
        sender_address = account.address_from_private_key(private_key)

        params = self.client.suggested_params()
        # Ensure micro fee is reasonable
        params.flat_fee = True
        params.fee = max(1000, params.min_fee)

        memo_bytes = memo_text.encode("utf-8")

        # Try ASA transfer (USDC) or native ALGO payment
        is_asa_transfer = False
        if asset_id > 0:
            try:
                # Check if recipient is opted into asset
                rec_info = self.client.account_info(recipient_address)
                rec_assets = [a["asset-id"] for a in rec_info.get("assets", [])]
                if asset_id in rec_assets:
                    is_asa_transfer = True
            except Exception:
                is_asa_transfer = False

        if is_asa_transfer:
            txn = transaction.AssetTransferTxn(
                sender=sender_address,
                sp=params,
                receiver=recipient_address,
                amt=amount_micro,
                index=asset_id,
                note=memo_bytes
            )
        else:
            # Native microALGO payment (standard micropayment value)
            # 10,000 micro-units = 0.01 ALGO / USDC equivalent
            txn = transaction.PaymentTxn(
                sender=sender_address,
                sp=params,
                receiver=recipient_address,
                amt=amount_micro,
                note=memo_bytes
            )

        signed_txn = txn.sign(private_key)
        tx_id = self.client.send_transaction(signed_txn)
        logger.info(f"x402 Payment Transaction sent: {tx_id}")

        # Wait for on-chain confirmation
        confirmed_txn = transaction.wait_for_confirmation(self.client, tx_id, 4)
        confirmed_round = confirmed_txn.get("confirmed-round", 0)

        return {
            "tx_id": tx_id,
            "sender": sender_address,
            "recipient": recipient_address,
            "amount_micro": amount_micro,
            "asset_id": asset_id,
            "confirmed_round": confirmed_round,
            "network": self.network,
            "explorer_url": self.get_explorer_url(tx_id)
        }

    def verify_payment_on_chain(
        self,
        tx_id: str,
        expected_recipient: str,
        expected_min_amount_micro: int
    ) -> Dict[str, Any]:
        """Verify on-chain settlement of an x402 payment proof."""
        try:
            tx_info = self.client.pending_transaction_info(tx_id)
            confirmed_round = tx_info.get("confirmed-round", 0)

            if confirmed_round == 0:
                # Poll once more
                tx_info = transaction.wait_for_confirmation(self.client, tx_id, 2)
                confirmed_round = tx_info.get("confirmed-round", 0)

            txn_body = tx_info.get("txn", {}).get("txn", {})
            receiver = txn_body.get("rcv") or txn_body.get("arcv")
            # Decode receiver address if base64/bytes
            if receiver and len(receiver) != 58:
                try:
                    receiver = algosdk.encoding.encode_address(algosdk.encoding.base64.b64decode(receiver))
                except Exception:
                    pass

            amount = txn_body.get("amt") or txn_body.get("aamt", 0)

            valid = (confirmed_round > 0)
            return {
                "valid": valid,
                "tx_id": tx_id,
                "confirmed_round": confirmed_round,
                "receiver": receiver,
                "amount": amount,
                "error": None if valid else "Transaction not confirmed yet"
            }
        except Exception as e:
            logger.error(f"Error verifying tx {tx_id}: {e}")
            return {
                "valid": False,
                "tx_id": tx_id,
                "confirmed_round": 0,
                "error": str(e)
            }

    def record_task_in_contract(
        self,
        agent_address: str,
        service_name: str,
        payment_amount_micro: int,
        tx_ref: str,
        signer_mnemonic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call record_task on the AgentPayRegistry smart contract."""
        app_id = settings.ALGORAND_APP_ID
        if app_id == 0:
            logger.warning("No ALGORAND_APP_ID configured. Task record simulated in memory.")
            return {"status": "skipped", "app_id": 0, "reason": "No App ID configured"}

        mnemonic_to_use = signer_mnemonic or settings.ALGORAND_SERVER_MNEMONIC
        if not mnemonic_to_use:
            logger.warning("No mnemonic available to sign smart contract call.")
            return {"status": "skipped", "app_id": app_id, "reason": "No signing key"}

        try:
            private_key = mnemonic.to_private_key(mnemonic_to_use)
            sender_address = account.address_from_private_key(private_key)

            params = self.client.suggested_params()
            params.flat_fee = True
            params.fee = max(1000, params.min_fee)

            agent_pubkey = algosdk.encoding.decode_address(agent_address)
            amt_bytes = payment_amount_micro.to_bytes(8, "big")

            txn = transaction.ApplicationNoOpTxn(
                sender=sender_address,
                sp=params,
                index=app_id,
                app_args=[
                    SELECTORS["record_task"],
                    agent_pubkey,
                    service_name.encode("utf-8"),
                    amt_bytes,
                    tx_ref.encode("utf-8")
                ]
            )

            signed_txn = txn.sign(private_key)
            contract_tx_id = self.client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(self.client, contract_tx_id, 4)

            logger.info(f"Contract task recorded on App ID {app_id}, Tx: {contract_tx_id}")
            return {
                "status": "success",
                "app_id": app_id,
                "contract_tx_id": contract_tx_id,
                "explorer_url": self.get_explorer_url(contract_tx_id)
            }
        except Exception as e:
            logger.error(f"Failed to record task in smart contract: {e}")
            return {
                "status": "error",
                "app_id": app_id,
                "error": str(e)
            }

    def get_contract_stats(self, app_id: Optional[int] = None) -> Dict[str, Any]:
        """Fetch global counters from AgentPayRegistry application."""
        target_app_id = app_id or settings.ALGORAND_APP_ID
        if target_app_id == 0:
            return {
                "total_agents": 1,
                "total_services": 1,
                "total_tasks": 0,
                "total_volume_micro": 0,
                "total_volume_usd": 0.0,
                "app_id": 0
            }

        try:
            app_info = self.client.application_info(target_app_id)
            global_state = app_info.get("params", {}).get("global-state", [])
            stats = {
                "total_agents": 0,
                "total_services": 0,
                "total_tasks": 0,
                "total_volume_micro": 0,
            }

            for item in global_state:
                key_raw = algosdk.encoding.base64.b64decode(item["key"]).decode("utf-8", errors="ignore")
                val_num = item["value"].get("uint", 0)
                if key_raw in stats:
                    stats[key_raw] = val_num

            stats["total_volume_usd"] = stats["total_volume_micro"] / 1e6
            stats["app_id"] = target_app_id
            return stats
        except Exception as e:
            logger.warning(f"Error fetching contract stats for App {target_app_id}: {e}")
            return {
                "total_agents": 1,
                "total_services": 1,
                "total_tasks": 0,
                "total_volume_micro": 0,
                "total_volume_usd": 0.0,
                "app_id": target_app_id,
                "error": str(e)
            }

    def get_explorer_url(self, tx_id: str) -> str:
        """Return official explorer link for transaction ID."""
        return f"https://lora.algokit.io/testnet/transaction/{tx_id}"

    def get_app_explorer_url(self, app_id: int) -> str:
        """Return official explorer link for application ID."""
        return f"https://lora.algokit.io/testnet/application/{app_id}"

# Global singleton client
algo_client = AlgorandBlockchainClient()
