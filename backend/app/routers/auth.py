from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.services.gmail import exchange_code_for_tokens, get_auth_url, is_authenticated

router = APIRouter()


@router.get("/status")
async def auth_status():
    """Check if Gmail is authenticated."""
    return {
        "authenticated": is_authenticated(),
        "message": ("Gmail connected" if is_authenticated() else "Gmail not connected"),
    }


@router.get("/login")
async def auth_login():
    """Redirect to Google OAuth consent screen."""
    auth_url = get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def auth_callback(code: str):
    """Handle Google OAuth callback and store tokens."""
    exchange_code_for_tokens(code)
    return {
        "status": "success",
        "message": "Gmail authenticated successfully. You can close this window.",
    }
