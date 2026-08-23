"""SummaryAgent - Seller AI Agent implementing A2A Protocol and x402 Payment Challenges."""

import uuid
import logging
from typing import Dict, Any, Tuple
from fastapi import HTTPException

from app.config import settings
from app.models.schemas import (
    A2AMessage,
    A2AResponse,
    X402PaymentRequirement,
    AgentInfo,
    AgentStatus
)
from app.blockchain.algorand_client import algo_client
from app.ai.summarizer import ai_summarizer

logger = logging.getLogger("agentpay.summary_agent")

class SummaryAgent:
    def __init__(self):
        self.agent_id = "summary-agent"
        self.name = "Summary Agent"
        self.description = "AI-powered text summarization agent with on-chain x402 settlement on Algorand TestNet."
        self.address = settings.ALGORAND_SERVER_ADDRESS
        self.price_usd = settings.X402_PRICE_USD
        self.amount_micro = int(self.price_usd * 1_000_000) # 10,000 micro-units for $0.01
        self.service_name = "text_summarization"

    def get_info(self) -> AgentInfo:
        return AgentInfo(
            agent_id=self.agent_id,
            name=self.name,
            description=self.description,
            address=self.address,
            price_usd=self.price_usd,
            network=settings.ALGORAND_NETWORK,
            payment_protocol="x402",
            status=AgentStatus.AVAILABLE,
            services=[self.service_name]
        )

    def create_402_challenge(self) -> X402PaymentRequirement:
        """Construct a standard x402 payment challenge."""
        return X402PaymentRequirement(
            scheme="x402",
            network=f"algorand:{settings.ALGORAND_NETWORK}",
            asset="USDC",
            asset_id=settings.X402_USDC_ASSET_ID,
            price_usd=self.price_usd,
            amount_micro=self.amount_micro,
            recipient_address=self.address,
            facilitator_url=settings.X402_FACILITATOR_URL,
            nonce=uuid.uuid4().hex,
            memo=f"AgentPay: Summarization ({self.agent_id})"
        )

    async def execute_task(self, a2a_msg: A2AMessage) -> Tuple[int, Any]:
        """Process an A2A message following x402 protocol.
        
        Returns: (http_status_code, response_data)
        """
        # Step 1: Check for payment proof
        payment_header = a2a_msg.payment
        if not payment_header or not payment_header.tx_id:
            logger.info(f"Unpaid A2A request from {a2a_msg.agent_id}. Issuing HTTP 402 Payment Required challenge.")
            challenge = self.create_402_challenge()
            return 402, challenge.model_dump()

        # Step 2: Verify on-chain payment proof
        tx_id = payment_header.tx_id
        logger.info(f"Verifying payment proof tx {tx_id} from {a2a_msg.agent_id}...")
        
        verification = algo_client.verify_payment_on_chain(
            tx_id=tx_id,
            expected_recipient=self.address,
            expected_min_amount_micro=self.amount_micro
        )

        if not verification.get("valid"):
            logger.warning(f"Payment verification failed for tx {tx_id}: {verification.get('error')}")
            return 402, {
                "error": "Payment verification failed or unconfirmed",
                "details": verification,
                "challenge": self.create_402_challenge().model_dump()
            }

        # Step 3: Execute the AI Task (Text Summarization)
        task_input = a2a_msg.task.input
        logger.info(f"Payment verified for tx {tx_id}! Running AI summarization...")
        summary_result = await ai_summarizer.summarize(task_input)

        # Step 4: Record completed task on Algorand Smart Contract
        contract_res = algo_client.record_task_in_contract(
            agent_address=self.address,
            service_name=self.service_name,
            payment_amount_micro=self.amount_micro,
            tx_ref=tx_id
        )

        task_id = f"task_{uuid.uuid4().hex[:8]}"
        response = A2AResponse(
            agent_id=self.agent_id,
            task_id=task_id,
            status="completed",
            result=summary_result,
            tx_id=tx_id,
            app_id=contract_res.get("app_id", settings.ALGORAND_APP_ID)
        )

        return 200, response.model_dump()

# Global Seller Agent instance
summary_agent = SummaryAgent()
