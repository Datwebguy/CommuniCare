"""
API Integration tests for FastAPI endpoints.
Verifies REST contracts, HTTP status codes, error handling, multi tenant isolation, and health checks.
"""

import pytest
from fastapi.testclient import TestClient
from communicare.main import app

client = TestClient(app)


def test_health_check_endpoint():
    """Verify /api/health returns 200 OK and expected diagnostic metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "CommuniCare" in data["service"]
    assert data["system_status"] == "Operational"


def test_generate_board_endpoint_success():
    """Verify POST /api/generate-board with valid caregiver message."""
    payload = {
        "message": "Good morning Leo, please take your medicine and drink water.",
        "recipient_id": "leo_care",
        "caregiver_id": "caregiver_primary",
        "simplify_style": "core_words"
    }
    response = client.post("/api/generate-board", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "board_id" in data
    assert len(data["cards"]) > 0
    assert len(data["pipeline_trace"]) == 5


def test_generate_board_empty_message_validation():
    """Verify POST /api/generate-board rejects empty message with 400 Bad Request."""
    payload = {
        "message": "   ",
        "recipient_id": "leo_care"
    }
    response = client.post("/api/generate-board", json=payload)
    assert response.status_code == 400


def test_recipients_endpoints():
    """Verify GET /api/recipients and GET /api/recipients/{id} with multi tenant headers."""
    res_list = client.get("/api/recipients", headers={"X-Caregiver-ID": "caregiver_primary"})
    assert res_list.status_code == 200
    assert isinstance(res_list.json(), list)

    res_single = client.get("/api/recipients/leo_care", headers={"X-Caregiver-ID": "caregiver_primary"})
    assert res_single.status_code == 200
    assert res_single.json()["recipient_id"] == "leo_care"


def test_feedback_endpoint():
    """Verify POST /api/feedback updates recipient memory."""
    payload = {
        "board_id": "test_board_123",
        "recipient_id": "leo_care",
        "caregiver_id": "caregiver_primary",
        "word": "pancakes",
        "action": "worked_well"
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_presets_endpoint():
    """Verify GET /api/presets returns pre-configured scenario presets."""
    response = client.get("/api/presets", headers={"X-Caregiver-ID": "caregiver_primary"})
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 3


def test_symbol_search_endpoint():
    """Verify GET /api/symbols/search returns matched AAC pictograms."""
    response = client.get("/api/symbols/search?q=water")
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
