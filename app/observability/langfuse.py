from langfuse.langchain import CallbackHandler

from app.config import get_settings


def get_langfuse_handler():
    settings = get_settings()

    return CallbackHandler(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
    )