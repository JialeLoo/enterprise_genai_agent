import psycopg

from app.config import get_settings


def get_connection():
    settings = get_settings()

    return psycopg.connect(
        settings.postgres_url
    )