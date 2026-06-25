import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "change-me-in-production-use-a-long-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS — update with your real frontend URL in production
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",   # React dev server (CRA)
        "http://localhost:5173",   # React dev server (Vite)
        "http://localhost:4173",   # Vite preview
    ]

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Documentation Assistant"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
