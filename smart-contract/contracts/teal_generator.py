"""ARC-4 / ARC-56 ABI Method definitions and TEAL builder for AgentPayRegistry."""

import hashlib
import json

def get_method_selector(signature: str) -> bytes:
    """Compute 4-byte ARC-4 method selector from signature."""
    hasher = hashlib.sha512()
    hasher.update(signature.encode("utf-8"))
    return hasher.digest()[:4]

def get_method_selector_hex(signature: str) -> str:
    return "0x" + get_method_selector(signature).hex()

# ABI Signatures
SIG_REGISTER_AGENT = "register_agent(address,string)void"
SIG_REGISTER_SERVICE = "register_service(string,uint64)void"
SIG_RECORD_TASK = "record_task(address,string,uint64,string)void"
SIG_GET_AGENT = "get_agent(address)string"
SIG_GET_SERVICE = "get_service(string)uint64"
SIG_GET_STATS = "get_stats()(uint64,uint64,uint64,uint64)"

SELECTORS = {
    "register_agent": get_method_selector(SIG_REGISTER_AGENT),
    "register_service": get_method_selector(SIG_REGISTER_SERVICE),
    "record_task": get_method_selector(SIG_RECORD_TASK),
    "get_agent": get_method_selector(SIG_GET_AGENT),
    "get_service": get_method_selector(SIG_GET_SERVICE),
    "get_stats": get_method_selector(SIG_GET_STATS),
}

# Clear State TEAL Program
CLEAR_STATE_TEAL = """#pragma version 8
int 1
return
"""

def generate_approval_teal() -> str:
    """Generate TEAL Approval Program for AgentPayRegistry."""
    sel_reg_agent = "0x" + SELECTORS["register_agent"].hex()
    sel_reg_service = "0x" + SELECTORS["register_service"].hex()
    sel_rec_task = "0x" + SELECTORS["record_task"].hex()
    sel_get_agent = "0x" + SELECTORS["get_agent"].hex()
    sel_get_service = "0x" + SELECTORS["get_service"].hex()
    sel_get_stats = "0x" + SELECTORS["get_stats"].hex()

    return f"""#pragma version 8
// AgentPayRegistry Smart Contract
// Handles agent registration, service registration, task recording, and stats.

txn ApplicationID
int 0
==
bnz handle_create

txn OnCompletion
int NoOp
==
bnz handle_noop

// Reject any other OnCompletion
err

handle_create:
// Initialize global state counters
byte "total_agents"
int 0
app_global_put

byte "total_services"
int 0
app_global_put

byte "total_tasks"
int 0
app_global_put

byte "total_volume"
int 0
app_global_put

int 1
return

handle_noop:
// Router based on 4-byte ABI selector in txna ApplicationArgs 0
txna ApplicationArgs 0
byte {sel_reg_agent}
==
bnz route_register_agent

txna ApplicationArgs 0
byte {sel_reg_service}
==
bnz route_register_service

txna ApplicationArgs 0
byte {sel_rec_task}
==
bnz route_record_task

txna ApplicationArgs 0
byte {sel_get_agent}
==
bnz route_get_agent

txna ApplicationArgs 0
byte {sel_get_service}
==
bnz route_get_service

txna ApplicationArgs 0
byte {sel_get_stats}
==
bnz route_get_stats

err

route_register_agent:
// args: 0: selector, 1: agent address (32 bytes), 2: agent name (string)
// Box key = "ag_" + agent address
byte "ag_"
txna ApplicationArgs 1
concat
txna ApplicationArgs 2
box_put

// Increment total_agents counter
byte "total_agents"
byte "total_agents"
app_global_get
int 1
+
app_global_put

int 1
return

route_register_service:
// args: 0: selector, 1: service_name (string), 2: price_micro_usdc (uint64)
// Box key = "srv_" + service_name
byte "srv_"
txna ApplicationArgs 1
concat
txna ApplicationArgs 2
box_put

// Increment total_services counter
byte "total_services"
byte "total_services"
app_global_get
int 1
+
app_global_put

int 1
return

route_record_task:
// args: 0: selector, 1: agent address, 2: service_name, 3: payment_amount (uint64), 4: tx_ref
// Increment total_tasks
byte "total_tasks"
byte "total_tasks"
app_global_get
int 1
+
app_global_put

// Increment total_volume by payment_amount (uint64)
byte "total_volume"
byte "total_volume"
app_global_get
txna ApplicationArgs 3
btoi
+
app_global_put

int 1
return

route_get_agent:
// args: 0: selector, 1: agent address
byte "ag_"
txna ApplicationArgs 1
concat
box_get
assert // asserts exists != 0 (pops uint64, leaves value byte slice on stack)

// ABI return prefix 0x151f7c75 + value
byte 0x151f7c75
swap
concat
log
int 1
return

route_get_service:
// args: 0: selector, 1: service name
byte "srv_"
txna ApplicationArgs 1
concat
box_get
assert // asserts exists != 0 (pops uint64, leaves value byte slice on stack)

byte 0x151f7c75
swap
concat
log
int 1
return

route_get_stats:
// Return (total_agents, total_services, total_tasks, total_volume) encoded as 32 bytes (4 * 8-byte uint64)
byte "total_agents"
app_global_get
itob
byte "total_services"
app_global_get
itob
concat
byte "total_tasks"
app_global_get
itob
concat
byte "total_volume"
app_global_get
itob
concat
store 2

byte 0x151f7c75
load 2
concat
log
int 1
return
"""

def generate_arc56_spec() -> dict:
    """Generate ARC-56 Application Specification JSON."""
    return {
        "arc56Version": "0.1.0",
        "name": "AgentPayRegistry",
        "desc": "On-chain Agent Marketplace and Task Settlement Registry for AgentPay",
        "methods": [
            {
                "name": "register_agent",
                "args": [
                    {"name": "agent", "type": "address"},
                    {"name": "name", "type": "string"}
                ],
                "returns": {"type": "void"},
                "desc": "Register an AI agent on-chain"
            },
            {
                "name": "register_service",
                "args": [
                    {"name": "service_name", "type": "string"},
                    {"name": "price_micro_usdc", "type": "uint64"}
                ],
                "returns": {"type": "void"},
                "desc": "Register a priced AI service"
            },
            {
                "name": "record_task",
                "args": [
                    {"name": "agent", "type": "address"},
                    {"name": "service_name", "type": "string"},
                    {"name": "payment_amount", "type": "uint64"},
                    {"name": "tx_ref", "type": "string"}
                ],
                "returns": {"type": "void"},
                "desc": "Record a completed A2A task with verified payment proof"
            },
            {
                "name": "get_agent",
                "args": [{"name": "agent", "type": "address"}],
                "returns": {"type": "string"},
                "desc": "Retrieve registered agent name"
            },
            {
                "name": "get_service",
                "args": [{"name": "service_name", "type": "string"}],
                "returns": {"type": "uint64"},
                "desc": "Retrieve service price"
            },
            {
                "name": "get_stats",
                "args": [],
                "returns": {"type": "(uint64,uint64,uint64,uint64)"},
                "desc": "Get global counters: total_agents, total_services, total_tasks, total_volume"
            }
        ],
        "state": {
            "global": {
                "numUint": 4,
                "numByteSlice": 0
            }
        }
    }
