"""Application configuration loaded from environment variables / .env file."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Reads all required env vars; raises on startup if any are missing."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Meta / WhatsApp Cloud API
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str
    whatsapp_access_token: SecretStr
    whatsapp_graph_api_version: str = "v25.0"
    whatsapp_app_secret: SecretStr
    whatsapp_webhook_verify_token: str

    # Campaign defaults
    campaign_template_name: str = "hello_world"
    campaign_template_language: str = "en_US"

    # Application
    database_url: str = "sqlite:///./app.db"
    log_level: str = "INFO"
    port: int = 8000


settings = Settings()
