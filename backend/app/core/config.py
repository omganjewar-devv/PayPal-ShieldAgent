from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # PayPal Sandbox Configuration
    PAYPAL_ENV: str = "sandbox"
    PAYPAL_CLIENT_ID: str = "mock_client_id"
    PAYPAL_CLIENT_SECRET: str = "mock_client_secret"
    PAYPAL_WEBHOOK_ID: Optional[str] = None

    @property
    def paypal_base_url(self) -> str:
        if self.PAYPAL_ENV.lower() == "live":
            return "https://api-m.paypal.com"
        return "https://api-m.sandbox.paypal.com"

    # AI Configuration
    AI_PROVIDER: str = "gemini"
    AI_API_KEY: Optional[str] = None
    AI_MODEL_NAME: str = "gemini-1.5-pro"

    # Decision Engine Thresholds
    MIN_WIN_PROBABILITY_TO_DEFEND: float = 60.0
    MAX_DISPUTE_AMOUNT_FOR_AUTO_CONCEDE: float = 25.0
    ENABLE_AUTONOMOUS_SUBMISSION: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
