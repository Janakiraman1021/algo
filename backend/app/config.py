"""Application configuration and environment management for AgentPay Backend."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Search for .env in current or parent directories
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    # Server configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True

    # Algorand Network Configuration
    ALGORAND_NETWORK: str = "testnet"
    ALGOD_SERVER: str = "https://testnet-api.algonode.cloud"
    ALGOD_TOKEN: str = ""
    ALGORAND_APP_ID: int = 0

    # Seller / Summary Agent (Receiver of payments)
    ALGORAND_SERVER_ADDRESS: str = "K2YJ2A6V27XG7K6YWWV2C2D4J2K5T3P7W9R8Y2N4B6V8C0X1Z2A3B4C5"
    ALGORAND_SERVER_MNEMONIC: str = ""

    # Buyer / Payer Agent (Sender of payments)
    ALGORAND_PAYER_ADDRESS: str = "J3Z4X5C6V7B8N9M0A1S2D3F4G5H6J7K8L9P0Q1W2E3R4T5Y6U7I8O9P0"
    ALGORAND_PAYER_MNEMONIC: str = ""

    # x402 Micropayment Settings
    X402_FACILITATOR_URL: str = "http://localhost:4020"
    X402_PRICE_USD: float = 0.01
    X402_USDC_ASSET_ID: int = 10458941  # Algorand TestNet USDC ASA ID
    X402_MICRO_UNITS_PER_USD: int = 1_000_000 # 6 decimals (1 USDC = 1,000,000 microUSDC)

    # AI Provider Configuration
    AI_PROVIDER: str = "gemini" # 'gemini', 'groq', 'openai', or 'fallback'
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
