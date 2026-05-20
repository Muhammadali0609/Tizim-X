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

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_groups (
                    chat_id BIGINT PRIMARY KEY,
                    title TEXT,
                    anti_links BOOLEAN NOT NULL DEFAULT TRUE,
                    anti_bad_words BOOLEAN NOT NULL DEFAULT FALSE,
                    silent_mode BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
            """)
        conn.commit()

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
        conn.commit()

def save_group(chat_id: int, title: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_groups (chat_id, title)
                VALUES (%s, %s)
                ON CONFLICT (chat_id)
                DO UPDATE SET title = EXCLUDED.title
            """, (chat_id, title))
        conn.commit()


def get_group_settings(chat_id: int) -> dict:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT anti_links, anti_bad_words, silent_mode
                FROM tizimx_groups
                WHERE chat_id = %s
            """, (chat_id,))
            row = cur.fetchone()

    if not row:
        return {
            "anti_links": True,
            "anti_bad_words": False,
            "silent_mode": True,
        }

    return {
        "anti_links": row[0],
        "anti_bad_words": row[1],
        "silent_mode": row[2],
    }
