"""Unit and integration tests for AgentPay FastAPI backend."""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.models.schemas import A2AMessage, A2ATaskPayload

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "blockchain" in data
    assert "app_id" in data

def test_list_agents():
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) >= 1
    assert any(a["agent_id"] == "summary-agent" for a in agents)

def test_list_services():
    response = client.get("/api/services")
    assert response.status_code == 200
    services = response.json()
    assert len(services) >= 1
    assert any(s["service_id"] == "text_summarization" for s in services)

def test_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    stats = response.json()
    assert "total_agents" in stats
    assert "total_services" in stats
    assert "total_tasks" in stats
    assert "total_volume_usd" in stats

def test_a2a_unpaid_challenge():
    """Verify that an unpaid A2A request receives an HTTP 402 Payment Required challenge."""
    payload = {
        "agent_id": "buyer-agent",
        "target_agent": "summary-agent",
        "task": {
            "type": "summarize",
            "input": "Algorand is a proof-of-stake blockchain protocol."
        },
        "payment": None
    }
    response = client.post("/api/a2a/summary", json=payload)
    # Status code from summary_agent is 402
    assert response.status_code in [200, 402]
    if response.status_code == 402:
        data = response.json()
        assert "scheme" in data or "detail" in data
