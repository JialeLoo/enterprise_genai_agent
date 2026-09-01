from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "enterprise-genai-copilot"
    environment: str = "local"

    model_provider: str = "openai"
    model_name: str = "gpt-5-mini"
    embedding_model: str = "text-embedding-3-small"
    openai_api_key: str | None = None

    operations_api_url: str = (
        "http://localhost:8001"
    )

    redis_url: str = (
        "redis://localhost:6379/0"
    )

    postgres_url: str = (
        "postgresql://genai:genai@localhost:5432/genai"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()