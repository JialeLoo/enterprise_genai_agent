from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config import get_settings


@lru_cache
def get_chat_model():
    settings = get_settings()

    if settings.model_provider == "openai":

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "when MODEL_PROVIDER=openai"
            )

        return ChatOpenAI(
            model=settings.model_name,
            api_key=settings.openai_api_key,
            temperature=0,
            timeout=30,
            max_retries=2,
        )

    raise ValueError(
        f"Unsupported model provider: "
        f"{settings.model_provider}"
    )