from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = "enterprise-genai-copilot"
    environment: str = "local"

    openai_api_key: str | None = None

    classifier_provider: str = "openai"
    classifier_model: str = "gpt-5-mini"

    agent_provider: str = "openai_compatible"
    agent_model: str = "qwen3:4b"

    # Generation and embeddings can evolve independently (for example, a
    # local chat model with hosted embeddings), so they have separate providers.
    embedding_provider: str = "openai"

    local_model_base_url: str = (
        "http://localhost:11434/v1"
    )

    local_model_api_key: str = "ollama"

    embedding_model: str = (
        "text-embedding-3-small"
    )

    redis_url: str = (
        "redis://localhost:6379/0"
    )

    postgres_url: str = (
        "postgresql://genai:genai@"
        "localhost:5432/genai"
    )

    operations_api_url: str = (
        "http://localhost:8001"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_host: str = "https://cloud.langfuse.com"


@lru_cache
def get_settings() -> Settings:
    # Settings are immutable for the lifetime of this process in normal use;
    # caching avoids reparsing the environment for every request and tool call.
    return Settings()
