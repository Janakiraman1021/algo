"""Pydantic data models and schemas for AgentPay."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class NetworkType(str, Enum):
    TESTNET = "testnet"
    MAINNET = "mainnet"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"

class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    PAYMENT_REQUIRED = "payment_required"
    PAYMENT_SUBMITTED = "payment_submitted"
    PAYMENT_SETTLED = "payment_settled"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"

# ----------------- Agent Models -----------------
class AgentInfo(BaseModel):
    agent_id: str = Field(..., description="Unique slug or address identifier")
    name: str = Field(..., description="Display name of the agent")
    description: str = Field(..., description="Agent capabilities and role")
    address: str = Field(..., description="Algorand TestNet address")
    price_usd: float = Field(default=0.01, description="Execution price in USD/USDC")
    network: str = Field(default="testnet", description="Blockchain network")
    payment_protocol: str = Field(default="x402", description="Payment scheme")
    status: AgentStatus = Field(default=AgentStatus.AVAILABLE)
    services: List[str] = Field(default_factory=list)

class AgentRegisterRequest(BaseModel):
    agent_id: str
    name: str
    description: str
    address: str
    price_usd: float = 0.01
    services: List[str] = ["text_summarization"]

# ----------------- Service Models -----------------
class ServiceInfo(BaseModel):
    service_id: str
    name: str
    description: str
    price_usd: float
    price_micro_usdc: int
    provider_agent: str
    network: str = "testnet"

class ServiceRegisterRequest(BaseModel):
    service_id: str
    name: str
    description: str
    price_usd: float
    provider_agent: str

# ----------------- A2A Message Models -----------------
class A2ATaskPayload(BaseModel):
    type: str = Field(default="summarize", description="Task type identifier")
    input: str = Field(..., description="Input text or prompt")
    options: Optional[Dict[str, Any]] = None

class A2APaymentHeader(BaseModel):
    required: bool = True
    proof: Optional[str] = None
    tx_id: Optional[str] = None
    payer: Optional[str] = None
    amount_micro: Optional[int] = None
    network: Optional[str] = "algorand:testnet"

class A2AMessage(BaseModel):
    agent_id: str = Field(..., description="Buyer agent identifier")
    target_agent: str = Field(..., description="Target seller agent identifier")
    task: A2ATaskPayload
    payment: Optional[A2APaymentHeader] = None

class A2AResponse(BaseModel):
    agent_id: str
    task_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None
    tx_id: Optional[str] = None
    app_id: Optional[int] = None

# ----------------- x402 Protocol Models -----------------
class X402PaymentRequirement(BaseModel):
    scheme: str = "x402"
    network: str = "algorand:testnet"
    asset: str = "USDC"
    asset_id: int = 10458941
    price_usd: float = 0.01
    amount_micro: int = 10000 # 0.01 USDC = 10,000 micro-units
    recipient_address: str
    facilitator_url: str
    nonce: str
    memo: str = "AgentPay: A2A Summarization Service"

class X402PaymentProof(BaseModel):
    tx_id: str
    sender_address: str
    recipient_address: str
    amount_micro: int
    asset_id: int
    signature: Optional[str] = None
    network: str = "algorand:testnet"

# ----------------- Task & Dashboard Models -----------------
class TaskStep(BaseModel):
    step_number: int
    name: str
    description: str
    status: str # 'pending', 'active', 'completed', 'failed'
    tx_id: Optional[str] = None
    timestamp: Optional[str] = None

class CreateTaskRequest(BaseModel):
    text: str = Field(..., description="Text content to be summarized by the AI Agent")
    service_id: str = Field(default="text_summarization")
    target_agent: str = Field(default="summary-agent")

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatusEnum
    input_text: str
    summary_result: Optional[str] = None
    price_usd: float = 0.01
    tx_id: Optional[str] = None
    explorer_url: Optional[str] = None
    app_id: Optional[int] = None
    created_at: str
    completed_at: Optional[str] = None
    steps: List[TaskStep] = Field(default_factory=list)
    error_message: Optional[str] = None

class StatsResponse(BaseModel):
    total_agents: int
    total_services: int
    total_tasks: int
    total_volume_usd: float
    total_volume_micro: int
    app_id: int
    network: str
    algod_status: str

class RecordTaskContractRequest(BaseModel):
    agent_address: str
    service_name: str
    payment_amount_micro: int
    tx_ref: str
