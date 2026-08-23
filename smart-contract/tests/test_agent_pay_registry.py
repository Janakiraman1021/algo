"""Unit tests for AgentPayRegistry Smart Contract."""

import sys
import os
from pathlib import Path

# Add project roots to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "contracts"))

from teal_generator import (
    generate_approval_teal,
    CLEAR_STATE_TEAL,
    generate_arc56_spec,
    SELECTORS,
    get_method_selector,
    SIG_REGISTER_AGENT,
    SIG_REGISTER_SERVICE,
    SIG_RECORD_TASK,
    SIG_GET_STATS,
    SIG_GET_AGENT,
    SIG_GET_SERVICE,
)

def test_abi_selectors():
    """Verify ABI method selectors are 4 bytes and correctly computed."""
    assert len(SELECTORS["register_agent"]) == 4
    assert len(SELECTORS["register_service"]) == 4
    assert len(SELECTORS["record_task"]) == 4
    assert len(SELECTORS["get_stats"]) == 4
    assert len(SELECTORS["get_agent"]) == 4
    assert len(SELECTORS["get_service"]) == 4

    # Verify deterministic calculation
    assert SELECTORS["register_agent"] == get_method_selector(SIG_REGISTER_AGENT)
    assert SELECTORS["register_service"] == get_method_selector(SIG_REGISTER_SERVICE)
    assert SELECTORS["record_task"] == get_method_selector(SIG_RECORD_TASK)
    assert SELECTORS["get_stats"] == get_method_selector(SIG_GET_STATS)
    assert SELECTORS["get_agent"] == get_method_selector(SIG_GET_AGENT)
    assert SELECTORS["get_service"] == get_method_selector(SIG_GET_SERVICE)

def test_teal_generation():
    """Verify TEAL approval program contains necessary opcodes and router branches."""
    approval_teal = generate_approval_teal()
    assert "#pragma version 8" in approval_teal
    assert "handle_create:" in approval_teal
    assert "handle_noop:" in approval_teal
    assert "route_register_agent:" in approval_teal
    assert "route_register_service:" in approval_teal
    assert "route_record_task:" in approval_teal
    assert "route_get_stats:" in approval_teal
    assert "route_get_agent:" in approval_teal
    assert "route_get_service:" in approval_teal
    assert "total_agents" in approval_teal
    assert "total_services" in approval_teal
    assert "total_tasks" in approval_teal
    assert "total_volume" in approval_teal

    assert "#pragma version 8" in CLEAR_STATE_TEAL

def test_arc56_spec():
    """Verify ARC-56 application specification is valid."""
    spec = generate_arc56_spec()
    assert spec["name"] == "AgentPayRegistry"
    assert len(spec["methods"]) == 6
    method_names = [m["name"] for m in spec["methods"]]
    assert "register_agent" in method_names
    assert "register_service" in method_names
    assert "record_task" in method_names
    assert "get_agent" in method_names
    assert "get_service" in method_names
    assert "get_stats" in method_names
    assert spec["state"]["global"]["numUint"] == 4
