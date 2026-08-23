"""TestNet wallet generator, balance checker, and environment config helper."""

import os
import sys
from pathlib import Path
from algosdk import account, mnemonic
from algosdk.v2client import algod
from dotenv import load_dotenv

ALGOD_SERVER = "https://testnet-api.algonode.cloud"

def get_balance(address: str) -> dict:
    try:
        client = algod.AlgodClient("", ALGOD_SERVER, {})
        info = client.account_info(address)
        algo_balance = info.get("amount", 0) / 1e6
        assets = info.get("assets", [])
        return {
            "address": address,
            "algo_balance": algo_balance,
            "assets": assets,
            "error": None
        }
    except Exception as e:
        return {
            "address": address,
            "algo_balance": 0.0,
            "assets": [],
            "error": str(e)
        }

def setup_wallets():
    print("=" * 60)
    print("   AgentPay — Algorand TestNet Wallet Setup")
    print("=" * 60)

    # Generate Seller/Server Account
    seller_sk, seller_addr = account.generate_account()
    seller_mn = mnemonic.from_private_key(seller_sk)

    # Generate Buyer/Payer Account
    buyer_sk, buyer_addr = account.generate_account()
    buyer_mn = mnemonic.from_private_key(buyer_sk)

    print(f"\n[1] SELLER / SERVER AGENT (SummaryAgent):")
    print(f"    Address : {seller_addr}")
    print(f"    Mnemonic: {seller_mn}")
    print(f"    Faucet  : https://bank.testnet.algorand.network/?account={seller_addr}")

    print(f"\n[2] BUYER / PAYER AGENT (BuyerAgent):")
    print(f"    Address : {buyer_addr}")
    print(f"    Mnemonic: {buyer_mn}")
    print(f"    Faucet  : https://bank.testnet.algorand.network/?account={buyer_addr}")

    print("\n" + "=" * 60)
    print("To fund these accounts:")
    print("1. Visit the Algorand TestNet Dispenser:")
    print("   https://bank.testnet.algorand.network/")
    print("2. Paste each address and request TestNet ALGO.")
    print("=" * 60)

    # Save to backend/.env.example and create .env if not exists
    backend_env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
    if not backend_env_path.exists():
        with open(backend_env_path, "w") as f:
            f.write(f"""# AgentPay Backend Configuration
PORT=8000
HOST=0.0.0.0
ALGORAND_NETWORK=testnet
ALGOD_SERVER=https://testnet-api.algonode.cloud
ALGOD_TOKEN=
ALGORAND_APP_ID=0

# Seller / Summary Agent
ALGORAND_SERVER_ADDRESS={seller_addr}
ALGORAND_SERVER_MNEMONIC={seller_mn}

# Buyer / Payer Agent
ALGORAND_PAYER_ADDRESS={buyer_addr}
ALGORAND_PAYER_MNEMONIC={buyer_mn}

# x402 Micropayment Settings
X402_FACILITATOR_URL=http://localhost:4020
X402_PRICE_USD=0.01
X402_USDC_ASSET_ID=10458941

# AI Provider: 'gemini', 'groq', 'openai', or 'fallback'
AI_PROVIDER=gemini
GEMINI_API_KEY=
GROQ_API_KEY=
OPENAI_API_KEY=
""")
        print(f"\n[+] Created default config at: {backend_env_path}")

    return {
        "seller": {"address": seller_addr, "mnemonic": seller_mn},
        "buyer": {"address": buyer_addr, "mnemonic": buyer_mn}
    }

if __name__ == "__main__":
    setup_wallets()
