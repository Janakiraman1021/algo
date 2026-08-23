"""Deployment script for AgentPayRegistry on Algorand TestNet."""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

import algosdk
from algosdk.v2client import algod
from algosdk import account, mnemonic, transaction

# Add contracts to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "smart-contract" / "contracts"))
from teal_generator import generate_approval_teal, CLEAR_STATE_TEAL, generate_arc56_spec

# Load environment variables
backend_env = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(backend_env)

ALGOD_ADDRESS = os.getenv("ALGOD_SERVER", "https://testnet-api.algonode.cloud")
ALGOD_TOKEN = os.getenv("ALGOD_TOKEN", "")
DEPLOYER_MNEMONIC = os.getenv("ALGORAND_SERVER_MNEMONIC", "")

def get_algod_client() -> algod.AlgodClient:
    headers = {"X-API-Key": ALGOD_TOKEN} if ALGOD_TOKEN else {}
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, headers)

def compile_program(client: algod.AlgodClient, source_code: str) -> bytes:
    compile_response = client.compile(source_code)
    return algosdk.encoding.base64.b64decode(compile_response["result"])

def deploy_agent_pay_registry(deployer_mnemonic: str = "") -> dict:
    """Deploy AgentPayRegistry smart contract to Algorand TestNet."""
    client = get_algod_client()

    if not deployer_mnemonic:
        deployer_mnemonic = DEPLOYER_MNEMONIC

    if not deployer_mnemonic:
        print("[!] No ALGORAND_SERVER_MNEMONIC provided. Generating new temporary deployer key.")
        private_key, sender_address = account.generate_account()
        generated_mnemonic = mnemonic.from_private_key(private_key)
        print(f"Deployer Address: {sender_address}")
        print(f"Deployer Mnemonic: {generated_mnemonic}")
        print(f"Fund this account on TestNet: https://bank.testnet.algorand.network/?account={sender_address}")
        return {
            "status": "funding_required",
            "address": sender_address,
            "mnemonic": generated_mnemonic,
            "faucet_url": f"https://bank.testnet.algorand.network/?account={sender_address}"
        }

    private_key = mnemonic.to_private_key(deployer_mnemonic)
    sender_address = account.address_from_private_key(private_key)
    print(f"Deploying with address: {sender_address}")

    # Check account balance
    acct_info = client.account_info(sender_address)
    algo_balance = acct_info.get("amount", 0) / 1e6
    print(f"Account ALGO balance: {algo_balance} ALGO")
    if algo_balance < 0.2:
        raise ValueError(f"Insufficient ALGO balance ({algo_balance} ALGO). Need at least 0.2 ALGO to deploy.")

    # Generate and compile TEAL
    approval_source = generate_approval_teal()
    clear_source = CLEAR_STATE_TEAL

    print("Compiling TEAL Approval Program...")
    approval_bytes = compile_program(client, approval_source)
    print("Compiling TEAL Clear State Program...")
    clear_bytes = compile_program(client, clear_source)

    # Global schema: 4 uints (total_agents, total_services, total_tasks, total_volume), 0 byteslices
    # Local schema: 0 uints, 0 byteslices
    global_schema = transaction.StateSchema(num_uints=4, num_byte_slices=0)
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    params = client.suggested_params()

    txn = transaction.ApplicationCreateTxn(
        sender=sender_address,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=approval_bytes,
        clear_program=clear_bytes,
        global_schema=global_schema,
        local_schema=local_schema,
    )

    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)
    print(f"Transaction sent with ID: {tx_id}")

    confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
    app_id = confirmed_txn["application-index"]
    print(f"[+] AgentPayRegistry successfully deployed! App ID: {app_id}")
    print(f"[+] Explorer: https://lora.algokit.io/testnet/application/{app_id}")

    # Save artifact spec
    artifacts_dir = Path(__file__).resolve().parent.parent / "smart-contract" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    with open(artifacts_dir / "AgentPayRegistry.arc56.json", "w") as f:
        json.dump(generate_arc56_spec(), f, indent=2)

    with open(artifacts_dir / "deployment.json", "w") as f:
        json.dump({
            "app_id": app_id,
            "creator": sender_address,
            "tx_id": tx_id,
            "network": "testnet"
        }, f, indent=2)

    return {
        "status": "deployed",
        "app_id": app_id,
        "tx_id": tx_id,
        "creator": sender_address
    }

if __name__ == "__main__":
    deploy_agent_pay_registry()
