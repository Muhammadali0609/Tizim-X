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
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS language TEXT NOT NULL DEFAULT 'ru'
            """)
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS required_channel TEXT
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS force_subscribe BOOLEAN NOT NULL DEFAULT FALSE
            """)
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS clean_service_messages BOOLEAN NOT NULL DEFAULT TRUE
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
                SELECT anti_links, anti_bad_words, silent_mode, clean_service_messages
                FROM tizimx_groups
                WHERE chat_id = %s
            """, (chat_id,))
            row = cur.fetchone()

    if not row:
        return {
            "anti_links": True,
            "anti_bad_words": False,
            "silent_mode": True,
            "clean_service_messages": True,
        }

    return {
        "anti_links": row[0],
        "anti_bad_words": row[1],
        "silent_mode": row[2],
        "clean_service_messages": row[3],
    }

def get_group_language(chat_id: int) -> str:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT language FROM tizimx_groups WHERE chat_id = %s",
                (chat_id,)
            )
            row = cur.fetchone()

    return row[0] if row else "ru"


def save_group_language(chat_id: int, language: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_groups (chat_id, language)
                VALUES (%s, %s)
                ON CONFLICT (chat_id)
                DO UPDATE SET language = EXCLUDED.language
            """, (chat_id, language))
        conn.commit()

def set_required_channel(chat_id: int, channel: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tizimx_groups
                SET required_channel = %s,
                    force_subscribe = TRUE
                WHERE chat_id = %s
            """, (channel, chat_id))
        conn.commit()


def get_required_channel(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT required_channel, force_subscribe
                FROM tizimx_groups
                WHERE chat_id = %s
            """, (chat_id,))
            row = cur.fetchone()

    if not row:
        return None, False

    return row[0], row[1]
