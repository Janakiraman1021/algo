"""BuyerAgent - Client AI Agent initiating A2A tasks and settling x402 micropayments."""

import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List

from app.config import settings
from app.models.schemas import (
    A2AMessage,
    A2ATaskPayload,
    A2APaymentHeader,
    TaskResponse,
    TaskStatusEnum,
    TaskStep
)
from app.agents.summary_agent import summary_agent
from app.blockchain.algorand_client import algo_client

logger = logging.getLogger("agentpay.buyer_agent")

class BuyerAgent:
    def __init__(self):
        self.agent_id = "buyer-agent"
        self.name = "Buyer Agent"
        self.address = settings.ALGORAND_PAYER_ADDRESS
        self.payer_mnemonic = settings.ALGORAND_PAYER_MNEMONIC

    async def execute_task_flow(self, text: str, target_agent_id: str = "summary-agent") -> TaskResponse:
        """Execute the full A2A + x402 + Algorand workflow step-by-step."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        created_at = datetime.now(timezone.utc).isoformat()
        steps: List[TaskStep] = []

        # ----------------------------------------------------
        # Step 1: User Task Initiation
        # ----------------------------------------------------
        steps.append(TaskStep(
            step_number=1,
            name="User Task Intake",
            description="BuyerAgent accepted user prompt and discovered target service.",
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # ----------------------------------------------------
        # Step 2: Send Initial A2A Request
        # ----------------------------------------------------
        a2a_initial = A2AMessage(
            agent_id=self.agent_id,
            target_agent=target_agent_id,
            task=A2ATaskPayload(type="summarize", input=text),
            payment=None
        )

        steps.append(TaskStep(
            step_number=2,
            name="A2A Request Dispatch",
            description=f"BuyerAgent sent A2A request to {target_agent_id}.",
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # ----------------------------------------------------
        # Step 3: Handle HTTP 402 Payment Required
        # ----------------------------------------------------
        status_code, response_data = await summary_agent.execute_task(a2a_initial)

        if status_code != 402:
            return TaskResponse(
                task_id=task_id,
                status=TaskStatusEnum.FAILED,
                input_text=text,
                created_at=created_at,
                steps=steps,
                error_message=f"Unexpected initial response status: {status_code}"
            )

        amount_micro = response_data.get("amount_micro", 10000)
        recipient = response_data.get("recipient_address", summary_agent.address)
        asset_id = response_data.get("asset_id", settings.X402_USDC_ASSET_ID)

        steps.append(TaskStep(
            step_number=3,
            name="HTTP 402 Payment Required",
            description=f"Seller requested {amount_micro / 1e6} USDC via x402 on Algorand.",
            status="completed",
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # ----------------------------------------------------
        # Step 4: Settle x402 Micropayment on Algorand TestNet
        # ----------------------------------------------------
        payment_result = None
        try:
            logger.info(f"BuyerAgent signing and submitting x402 payment to {recipient}...")
            payment_result = algo_client.submit_x402_payment(
                payer_mnemonic=self.payer_mnemonic,
                recipient_address=recipient,
                amount_micro=amount_micro,
                asset_id=asset_id,
                memo_text=f"AgentPay A2A: {task_id}"
            )
            tx_id = payment_result["tx_id"]
            explorer_url = payment_result["explorer_url"]

            steps.append(TaskStep(
                step_number=4,
                name="x402 Payment Broadcast & Settlement",
                description=f"Signed and confirmed on Algorand TestNet (Tx: {tx_id[:8]}...)",
                status="completed",
                tx_id=tx_id,
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
        except Exception as e:
            logger.error(f"Payment submission error: {e}")
            steps.append(TaskStep(
                step_number=4,
                name="x402 Payment Broadcast",
                description=f"Payment execution failed: {str(e)}",
                status="failed",
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
            return TaskResponse(
                task_id=task_id,
                status=TaskStatusEnum.FAILED,
                input_text=text,
                created_at=created_at,
                steps=steps,
                error_message=f"Blockchain payment failed: {str(e)}"
            )

        # ----------------------------------------------------
        # Step 5: Retry A2A Request with Payment Proof
        # ----------------------------------------------------
        a2a_paid = A2AMessage(
            agent_id=self.agent_id,
            target_agent=target_agent_id,
            task=A2ATaskPayload(type="summarize", input=text),
            payment=A2APaymentHeader(
                required=False,
                proof=tx_id,
                tx_id=tx_id,
                payer=self.address,
                amount_micro=amount_micro,
                network=f"algorand:{settings.ALGORAND_NETWORK}"
            )
        )

        steps.append(TaskStep(
            step_number=5,
            name="Retry A2A with Payment Proof",
            description=f"Sent verified payment proof header to {target_agent_id}.",
            status="completed",
            tx_id=tx_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        # ----------------------------------------------------
        # Step 6: Seller Executes AI Task & Updates Smart Contract
        # ----------------------------------------------------
        status_code2, response_data2 = await summary_agent.execute_task(a2a_paid)

        if status_code2 != 200:
            steps.append(TaskStep(
                step_number=6,
                name="AI Execution & Contract Registry",
                description=f"Seller failed to complete task: {response_data2}",
                status="failed",
                timestamp=datetime.now(timezone.utc).isoformat()
            ))
            return TaskResponse(
                task_id=task_id,
                status=TaskStatusEnum.FAILED,
                input_text=text,
                price_usd=amount_micro / 1e6,
                tx_id=tx_id,
                explorer_url=explorer_url,
                created_at=created_at,
                steps=steps,
                error_message=f"Execution error: {response_data2}"
            )

        summary_result = response_data2.get("result", "")
        app_id = response_data2.get("app_id", settings.ALGORAND_APP_ID)

        steps.append(TaskStep(
            step_number=6,
            name="AI Summary Generated & Smart Contract Updated",
            description=f"Summary delivered. On-chain task counter updated on App #{app_id}.",
            status="completed",
            tx_id=tx_id,
            timestamp=datetime.now(timezone.utc).isoformat()
        ))

        return TaskResponse(
            task_id=task_id,
            status=TaskStatusEnum.COMPLETED,
            input_text=text,
            summary_result=summary_result,
            price_usd=amount_micro / 1e6,
            tx_id=tx_id,
            explorer_url=explorer_url,
            app_id=app_id,
            created_at=created_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            steps=steps,
            error_message=None
        )

# Global Buyer Agent instance
buyer_agent = BuyerAgent()
