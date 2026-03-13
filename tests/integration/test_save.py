"""Integration tests for the /api/properties sheet routes."""

import os

import pytest

_has_creds = os.getenv("GOOGLE_SERVICE_ACCOUNT", "{}") not in ("", "{}")
_skip_reason = "GOOGLE_SERVICE_ACCOUNT not configured"


def test_post_returns_503_without_creds(client):
    """When sheets are not configured the endpoint returns 503."""
    from backend.config import settings
    if settings.GOOGLE_SERVICE_ACCOUNT not in ("", "{}"):
        pytest.skip("Sheets credentials are configured")
    response = client.post("/api/properties", json={"data": {"Price": "$100"}})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


def test_get_returns_503_without_creds(client):
    """When sheets are not configured the endpoint returns 503."""
    from backend.config import settings
    if settings.GOOGLE_SERVICE_ACCOUNT not in ("", "{}"):
        pytest.skip("Sheets credentials are configured")
    response = client.get("/api/properties")
    assert response.status_code == 503


@pytest.mark.skipif(not _has_creds, reason=_skip_reason)
def test_post_saves_property(client):
    """POST /api/properties returns 200 with valid data."""
    payload = {"data": {"Price": "$1,000,000", "Address": "123 Test St"}}
    response = client.post("/api/properties", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "saved"
    assert isinstance(body["row"], int)


@pytest.mark.skipif(not _has_creds, reason=_skip_reason)
def test_get_returns_list(client):
    """GET /api/properties returns a list with summary."""
    response = client.get("/api/properties")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["properties"], list)
    assert "summary" in body
