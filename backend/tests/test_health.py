import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Health check returns healthy status."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "control-gastos-api"
    assert data["version"] == "0.1.0"
