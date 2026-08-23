"""Main FastAPI application entrypoint for AgentPay."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes.api import router as api_router
from app.blockchain.algorand_client import algo_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("agentpay.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info("  Starting AgentPay Backend (A2A + x402 + Algorand)")
    logger.info(f"  Network: {settings.ALGORAND_NETWORK}")
    logger.info(f"  Node: {settings.ALGOD_SERVER}")
    logger.info(f"  App ID: {settings.ALGORAND_APP_ID}")
    logger.info(f"  Seller: {settings.ALGORAND_SERVER_ADDRESS[:10]}...")
    logger.info(f"  Buyer:  {settings.ALGORAND_PAYER_ADDRESS[:10]}...")
    logger.info(f"  AI:     {settings.AI_PROVIDER}")
    logger.info("=" * 60)
    
    # Check node status
    status = algo_client.get_status()
    if status.get("connected"):
        logger.info(f"[+] Algorand TestNet connected! Last round: {status.get('last_round')}")
    else:
        logger.warning(f"[!] Algorand node connection check: {status.get('error')}")

    yield
    logger.info("Shutting down AgentPay backend.")

app = FastAPI(
    title="AgentPay API",
    description="A2A + x402 + Algorand AI Agent Marketplace Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "project": "AgentPay — A2A + x402 + Algorand AI Marketplace",
        "status": "operational",
        "docs": "/docs",
        "api_endpoints": [
            "/api/health",
            "/api/agents",
            "/api/services",
            "/api/tasks",
            "/api/stats"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
