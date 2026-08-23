"""Seed Agent and Service into the AgentPayRegistry Smart Contract."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction

# Add contracts and backend to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "smart-contract" / "contracts"))
from teal_generator import SELECTORS

backend_env = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(backend_env)

ALGOD_SERVER = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
APP_ID = int(os.getenv("ALGORAND_APP_ID", "0"))
SELLER_MNEMONIC = os.getenv("ALGORAND_SERVER_MNEMONIC", "")

def seed():
    if APP_ID == 0:
        print("[!] ALGORAND_APP_ID is 0. Please deploy contract first using scripts/deploy_contract.py")
        return

    if not SELLER_MNEMONIC:
        print("[!] ALGORAND_SERVER_MNEMONIC is not configured in backend/.env")
        return

    client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_SERVER, {})
    private_key = mnemonic.to_private_key(SELLER_MNEMONIC)
    sender_address = account.address_from_private_key(private_key)

    params = client.suggested_params()

    # Ensure application account is funded for Box Storage Minimum Balance Requirement (MBR)
    app_addr = algosdk.logic.get_application_address(APP_ID)
    try:
        app_info = client.account_info(app_addr)
        app_balance = app_info.get("amount", 0)
    except Exception:
        app_balance = 0

    if app_balance < 300_000:
        print(f"Funding App Account {app_addr} with 0.3 ALGO for Box MBR...")
        fund_txn = transaction.PaymentTxn(
            sender=sender_address,
            sp=params,
            receiver=app_addr,
            amt=300_000,
            note=b"AgentPay: Box MBR Funding"
        )
        signed_fund = fund_txn.sign(private_key)
        fund_txid = client.send_transaction(signed_fund)
        transaction.wait_for_confirmation(client, fund_txid, 4)
        print(f"[+] App Account funded! Tx ID: {fund_txid}")

    print(f"Registering Agent '{sender_address}' on App ID {APP_ID}...")

    # 1. register_agent(agent_address, name)
    # Box key = b"ag_" + 32-byte address
    sender_pubkey_bytes = algosdk.encoding.decode_address(sender_address)
    agent_box_name = b"ag_" + sender_pubkey_bytes
    
    txn1 = transaction.ApplicationNoOpTxn(
        sender=sender_address,
        sp=params,
        index=APP_ID,
        app_args=[
            SELECTORS["register_agent"],
            sender_pubkey_bytes,
            "SummaryAgent".encode("utf-8")
        ],
        boxes=[(APP_ID, agent_box_name)]
    )

    signed_txn1 = txn1.sign(private_key)
    tx_id1 = client.send_transaction(signed_txn1)
    print(f"Agent registration Tx ID: {tx_id1}")
    transaction.wait_for_confirmation(client, tx_id1, 4)
    print("[+] Registered SummaryAgent successfully!")

    # 2. register_service(service_name, price_micro_usdc)
    service_name = "Text Summarization"
    service_price_micro = (10000).to_bytes(8, "big") # 0.01 USDC = 10,000 microUSDC
    service_box_name = b"srv_" + service_name.encode("utf-8")

    params = client.suggested_params()
    txn2 = transaction.ApplicationNoOpTxn(
        sender=sender_address,
        sp=params,
        index=APP_ID,
        app_args=[
            SELECTORS["register_service"],
            service_name.encode("utf-8"),
            service_price_micro
        ],
        boxes=[(APP_ID, service_box_name)]
    )

    signed_txn2 = txn2.sign(private_key)
    tx_id2 = client.send_transaction(signed_txn2)
    print(f"Service registration Tx ID: {tx_id2}")
    transaction.wait_for_confirmation(client, tx_id2, 4)
    print(f"[+] Registered service '{service_name}' at 0.01 USDC successfully!")

if __name__ == "__main__":
    seed()
