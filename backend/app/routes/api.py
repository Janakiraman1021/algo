"""API route handlers for AgentPay FastAPI backend."""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Header

from app.config import settings
from app.models.schemas import (
    AgentInfo,
    AgentRegisterRequest,
    ServiceInfo,
    ServiceRegisterRequest,
    CreateTaskRequest,
    TaskResponse,
    StatsResponse,
    RecordTaskContractRequest,
    A2AMessage,
    A2AResponse
)
from app.agents.summary_agent import summary_agent
from app.agents.buyer_agent import buyer_agent
from app.blockchain.algorand_client import algo_client

logger = logging.getLogger("agentpay.routes")

router = APIRouter(prefix="/api")

# In-memory storage for cached task history & registered items
TASKS_STORE: Dict[str, TaskResponse] = {}
AGENTS_STORE: Dict[str, AgentInfo] = {
    "summary-agent": summary_agent.get_info()
}
SERVICES_STORE: Dict[str, ServiceInfo] = {
    "text_summarization": ServiceInfo(
        service_id="text_summarization",
        name="Text Summarization",
        description="High-precision AI text summarization with x402 micropayment settlement.",
        price_usd=0.01,
        price_micro_usdc=10000,
        provider_agent="summary-agent",
        network="testnet"
    )
}

# ----------------- Health -----------------
@router.get("/health")
def get_health():
    algo_status = algo_client.get_status()
    return {
        "status": "healthy",
        "service": "AgentPay Backend",
        "version": "1.0.0",
        "blockchain": algo_status,
        "app_id": settings.ALGORAND_APP_ID,
        "ai_provider": settings.AI_PROVIDER
    }

# ----------------- Agents -----------------
@router.get("/agents", response_model=List[AgentInfo])
def list_agents():
    return list(AGENTS_STORE.values())

@router.get("/agents/{agent_id}", response_model=AgentInfo)
def get_agent(agent_id: str):
    if agent_id not in AGENTS_STORE:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AGENTS_STORE[agent_id]

@router.post("/agents/register", response_model=AgentInfo)
def register_agent(payload: AgentRegisterRequest):
    new_agent = AgentInfo(
        agent_id=payload.agent_id,
        name=payload.name,
        description=payload.description,
        address=payload.address,
        price_usd=payload.price_usd,
        network=settings.ALGORAND_NETWORK,
        payment_protocol="x402",
        services=payload.services
    )
    AGENTS_STORE[payload.agent_id] = new_agent
    return new_agent

# ----------------- Services -----------------
@router.get("/services", response_model=List[ServiceInfo])
def list_services():
    return list(SERVICES_STORE.values())

@router.get("/services/{service_id}", response_model=ServiceInfo)
def get_service(service_id: str):
    if service_id not in SERVICES_STORE:
        raise HTTPException(status_code=404, detail="Service not found")
    return SERVICES_STORE[service_id]

@router.post("/services/register", response_model=ServiceInfo)
def register_service(payload: ServiceRegisterRequest):
    new_service = ServiceInfo(
        service_id=payload.service_id,
        name=payload.name,
        description=payload.description,
        price_usd=payload.price_usd,
        price_micro_usdc=int(payload.price_usd * 1_000_000),
        provider_agent=payload.provider_agent,
        network=settings.ALGORAND_NETWORK
    )
    SERVICES_STORE[payload.service_id] = new_service
    return new_service

# ----------------- Tasks -----------------
@router.post("/tasks", response_model=TaskResponse)
async def create_task(payload: CreateTaskRequest):
    """Execute end-to-end user task: triggers BuyerAgent -> x402 payment -> SummaryAgent -> Smart Contract."""
    task_response = await buyer_agent.execute_task_flow(
        text=payload.text,
        target_agent_id=payload.target_agent
    )
    TASKS_STORE[task_response.task_id] = task_response
    return task_response

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str):
    if task_id not in TASKS_STORE:
        raise HTTPException(status_code=404, detail="Task not found")
    return TASKS_STORE[task_id]

# ----------------- Direct A2A Endpoint -----------------
@router.post("/a2a/summary")
async def handle_a2a_summary(
    a2a_msg: A2AMessage,
    payment_signature: Optional[str] = Header(None, alias="PAYMENT-SIGNATURE")
):
    """Direct A2A protocol endpoint for external AI agents."""
    if payment_signature and not a2a_msg.payment:
        a2a_msg.payment = {"tx_id": payment_signature}
    
    status_code, data = await summary_agent.execute_task(a2a_msg)
    if status_code == 402:
        return HTTPException(status_code=402, detail=data)
    return data

# ----------------- Transactions -----------------
@router.get("/transactions/{tx_id}")
def get_transaction(tx_id: str):
    ver = algo_client.verify_payment_on_chain(tx_id, "", 0)
    return {
        "tx_id": tx_id,
        "verification": ver,
        "explorer_url": algo_client.get_explorer_url(tx_id)
    }

# ----------------- Smart Contract & Stats -----------------
@router.post("/contract/record-task")
def record_contract_task(payload: RecordTaskContractRequest):
    res = algo_client.record_task_in_contract(
        agent_address=payload.agent_address,
        service_name=payload.service_name,
        payment_amount_micro=payload.payment_amount_micro,
        tx_ref=payload.tx_ref
    )
    return res

@router.get("/stats", response_model=StatsResponse)
def get_stats():
    contract_stats = algo_client.get_contract_stats()
    algo_status = algo_client.get_status()
    
    total_tasks_completed = sum(1 for t in TASKS_STORE.values() if t.status == "completed")
    total_volume_recorded = sum(t.price_usd for t in TASKS_STORE.values() if t.status == "completed")

    return StatsResponse(
        total_agents=max(len(AGENTS_STORE), contract_stats.get("total_agents", 1)),
        total_services=max(len(SERVICES_STORE), contract_stats.get("total_services", 1)),
        total_tasks=contract_stats.get("total_tasks", 0) + total_tasks_completed,
        total_volume_usd=contract_stats.get("total_volume_usd", 0.0) + total_volume_recorded,
        total_volume_micro=contract_stats.get("total_volume_micro", 0) + int(total_volume_recorded * 1_000_000),
        app_id=settings.ALGORAND_APP_ID,
        network=settings.ALGORAND_NETWORK,
        algod_status="online" if algo_status.get("connected") else "offline"
    )
