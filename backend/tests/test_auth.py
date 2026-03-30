from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_auth_status_not_connected(client):
    """Auth status returns not authenticated when no token exists."""
    with patch("app.routers.auth.is_authenticated", return_value=False):
        response = await client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is False
        assert "not connected" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_status_connected(client):
    """Auth status returns authenticated when token exists."""
    with patch("app.routers.auth.is_authenticated", return_value=True):
        response = await client.get("/auth/status")
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "connected" in data["message"].lower()


@pytest.mark.asyncio
async def test_auth_login_redirects(client):
    """Auth login returns a redirect to Google OAuth."""
    mock_url = "https://accounts.google.com/o/oauth2/auth?test=1"
    with patch("app.routers.auth.get_auth_url", return_value=mock_url):
        response = await client.get("/auth/login", follow_redirects=False)
        assert response.status_code == 307
        assert "accounts.google.com" in response.headers["location"]


@pytest.mark.asyncio
async def test_auth_callback_success(client):
    """Auth callback exchanges code and returns success."""
    with patch(
        "app.routers.auth.exchange_code_for_tokens",
        return_value={"token": "test"},
    ):
        response = await client.get("/auth/google/callback?code=test_code")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
