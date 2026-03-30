from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_env: str = "development"
    app_secret_key: str = "change-me-in-production"

    # Database
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/control_gastos"
    )

    # Frontend
    frontend_url: str = "http://localhost:3000"

    # Google OAuth (Gmail API)
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # Anthropic (Claude API)
    anthropic_api_key: str = ""

    model_config = {"env_file": "../.env", "extra": "ignore"}


settings = Settings()
