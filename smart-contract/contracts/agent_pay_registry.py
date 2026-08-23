"""AgentPayRegistry - Algorand Python Smart Contract (ARC-4 / ARC-56 compatible)

This contract acts as an on-chain registry for AI Agents and their services,
recording verified task completions and payment volume on the Algorand blockchain.
"""

from typing import Tuple

try:
    from algopy import (
        ARC4Contract,
        Account,
        Bytes,
        Global,
        String,
        Txn,
        UInt64,
        arc4,
        subroutine,
    )
    from algopy.op import Box
    HAS_ALGOPY = True
except ImportError:
    HAS_ALGOPY = False


if HAS_ALGOPY:
    class AgentPayRegistry(ARC4Contract):
        """On-chain Agent Marketplace and Task Settlement Registry for AgentPay."""

        def __init__(self) -> None:
            self.total_agents = UInt64(0)
            self.total_services = UInt64(0)
            self.total_tasks = UInt64(0)
            self.total_volume = UInt64(0)

        @arc4.abimethod(create="require")
        def create_application(self) -> None:
            """Initialize the global statistics counters upon contract creation."""
            self.total_agents = UInt64(0)
            self.total_services = UInt64(0)
            self.total_tasks = UInt64(0)
            self.total_volume = UInt64(0)

        @arc4.abimethod
        def register_agent(self, agent: arc4.Address, name: arc4.String) -> None:
            """Register an AI agent on-chain.
            
            Args:
                agent: The Algorand address of the AI agent.
                name: The human-readable name of the agent (e.g., 'SummaryAgent').
            """
            box_key = Bytes(b"ag_") + agent.bytes
            # Store agent name in box storage
            Box.put(box_key, name.bytes)
            self.total_agents += 1

        @arc4.abimethod
        def register_service(self, service_name: arc4.String, price_micro_usdc: arc4.UInt64) -> None:
            """Register a priced AI service.
            
            Args:
                service_name: Unique identifier of the service (e.g., 'text_summarization').
                price_micro_usdc: Price per execution in micro-units (e.g. 10000 = 0.01 USDC).
            """
            box_key = Bytes(b"srv_") + service_name.bytes
            Box.put(box_key, price_micro_usdc.bytes)
            self.total_services += 1

        @arc4.abimethod
        def record_task(
            self,
            agent: arc4.Address,
            service_name: arc4.String,
            payment_amount: arc4.UInt64,
            tx_ref: arc4.String,
        ) -> None:
            """Record a completed A2A task with verified x402 payment proof.
            
            Args:
                agent: The seller agent that executed the task.
                service_name: The service performed.
                payment_amount: Settled payment in micro-units.
                tx_ref: Transaction reference hash from Algorand.
            """
            self.total_tasks += 1
            self.total_volume += payment_amount.native

        @arc4.abimethod(readonly=True)
        def get_agent(self, agent: arc4.Address) -> arc4.String:
            """Retrieve the registered agent name."""
            box_key = Bytes(b"ag_") + agent.bytes
            val, exists = Box.get(box_key)
            assert exists, "Agent not found"
            return arc4.String.from_bytes(val)

        @arc4.abimethod(readonly=True)
        def get_service(self, service_name: arc4.String) -> arc4.UInt64:
            """Retrieve the price for a service."""
            box_key = Bytes(b"srv_") + service_name.bytes
            val, exists = Box.get(box_key)
            assert exists, "Service not found"
            return arc4.UInt64.from_bytes(val)

        @arc4.abimethod(readonly=True)
        def get_stats(self) -> arc4.Tuple[arc4.UInt64, arc4.UInt64, arc4.UInt64, arc4.UInt64]:
            """Return (total_agents, total_services, total_tasks, total_volume)."""
            return arc4.Tuple((
                arc4.UInt64(self.total_agents),
                arc4.UInt64(self.total_services),
                arc4.UInt64(self.total_tasks),
                arc4.UInt64(self.total_volume),
            ))
