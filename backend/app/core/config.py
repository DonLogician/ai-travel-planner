from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "AI Travel Planner"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    # iFlytek API
    IFLYTEK_APP_ID: Optional[str] = None
    IFLYTEK_API_KEY: Optional[str] = None
    IFLYTEK_API_SECRET: Optional[str] = None

    # Amap API
    AMAP_API_KEY: Optional[str] = None

    # LLM Configuration
    QWEN_API_KEY: Optional[str] = None
    QWEN_MODEL: str = "qwen-turbo"
    DOUBAO_API_KEY: Optional[str] = None
    DOUBAO_MODEL: str = "doubao-pro"
    LLM_PROVIDER: str = "qwen"  # qwen or doubao

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
