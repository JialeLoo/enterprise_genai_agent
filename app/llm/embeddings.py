from functools import lru_cache

from langchain_openai import OpenAIEmbeddings

from app.config import get_settings


@lru_cache
def get_embedding_model():
    settings = get_settings()

    if settings.model_provider == "openai":

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required"
            )

        return OpenAIEmbeddings(
            model=settings.embedding_model,
            api_key=settings.openai_api_key,
        )

    raise ValueError(
        f"Unsupported embedding provider: "
        f"{settings.model_provider}"
    )