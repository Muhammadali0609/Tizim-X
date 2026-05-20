import psycopg
from config import DATABASE_URL


def get_connection():
    return psycopg.connect(DATABASE_URL)


def setup_database():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_users (
                    user_id BIGINT PRIMARY KEY,
                    language TEXT NOT NULL DEFAULT 'ru',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)


def get_user_language(user_id: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT language FROM tizimx_users WHERE user_id = %s",
                (user_id,)
            )
            row = cur.fetchone()

    return row[0] if row else "ru"


def save_user_language(user_id: int, language: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_users (user_id, language)
                VALUES (%s, %s)
                ON CONFLICT (user_id)
                DO UPDATE SET language = EXCLUDED.language
            """, (user_id, language))
