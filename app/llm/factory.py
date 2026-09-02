from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config import get_settings


def build_model(
    *,
    provider: str,
    model_name: str,
):
    settings = get_settings()

    if provider == "openai":

        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "when provider=openai"
            )

        return ChatOpenAI(
            model=model_name,
            api_key=settings.openai_api_key,
            temperature=0,
            timeout=30,
            max_retries=2,
        )

    if provider == "openai_compatible":

        return ChatOpenAI(
            model=model_name,
            base_url=(
                settings.local_model_base_url
            ),
            api_key=(
                settings.local_model_api_key
            ),
            temperature=0,
            timeout=120,
            max_retries=1,
        )

    raise ValueError(
        f"Unsupported model provider: {provider}"
    )


@lru_cache
def get_classifier_model():

    settings = get_settings()

    return build_model(
        provider=(
            settings.classifier_provider
        ),
        model_name=(
            settings.classifier_model
        ),
    )


@lru_cache
def get_agent_model():

    settings = get_settings()

    return build_model(
        provider=(
            settings.agent_provider
        ),
        model_name=(
            settings.agent_model
        ),
    )