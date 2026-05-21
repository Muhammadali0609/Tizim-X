import psycopg
from config import DATABASE_URL
from filters import DEFAULT_BAD_WORDS

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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_group_admins (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'admin',
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (chat_id, user_id)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_bad_words (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    word TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(chat_id, word)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_ad_links (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    link TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(chat_id, link)
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

def save_group_admin(chat_id: int, user_id: int, role: str = "admin"):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_group_admins (chat_id, user_id, role)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id, user_id)
                DO UPDATE SET role = EXCLUDED.role
            """, (chat_id, user_id, role))
        conn.commit()


def get_user_groups(user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT g.chat_id, g.title
                FROM tizimx_group_admins a
                JOIN tizimx_groups g ON g.chat_id = a.chat_id
                WHERE a.user_id = %s
                ORDER BY g.title
            """, (user_id,))
            rows = cur.fetchall()

    return rows

BAD_WORDS_PER_PAGE = 30

def get_bad_words_count(chat_id: int) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM tizimx_bad_words WHERE chat_id = %s",
                (chat_id,)
            )
            row = cur.fetchone()

    return row[0]


def get_bad_words_page(chat_id: int, page: int):
    offset = page * BAD_WORDS_PER_PAGE

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, word
                FROM tizimx_bad_words
                WHERE chat_id = %s
                ORDER BY word
                LIMIT %s OFFSET %s
            """, (chat_id, BAD_WORDS_PER_PAGE, offset))
            rows = cur.fetchall()

    return rows

def seed_default_bad_words(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*)
                FROM tizimx_bad_words
                WHERE chat_id = %s
            """, (chat_id,))

            count = cur.fetchone()[0]

            if count > 0:
                return

            for word in DEFAULT_BAD_WORDS:
                cur.execute("""
                    INSERT INTO tizimx_bad_words (chat_id, word)
                    VALUES (%s, %s)
                    ON CONFLICT (chat_id, word) DO NOTHING
                """, (chat_id, word))

        conn.commit()

def add_bad_words(chat_id: int, words: list[str]):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for word in words:
                cur.execute("""
                    INSERT INTO tizimx_bad_words (chat_id, word)
                    VALUES (%s, %s)
                    ON CONFLICT (chat_id, word) DO NOTHING
                """, (chat_id, word))
        conn.commit()

def get_bad_words_for_check(chat_id: int) -> list[str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT word FROM tizimx_bad_words WHERE chat_id = %s",
                (chat_id,)
            )
            rows = cur.fetchall()

    return [row[0].lower() for row in rows]

def set_group_setting(chat_id: int, key: str, value: bool):
    allowed_keys = {
        "anti_links",
        "anti_bad_words",
        "force_subscribe",
        "clean_service_messages",
    }

    if key not in allowed_keys:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE tizimx_groups SET {key} = %s WHERE chat_id = %s",
                (value, chat_id)
            )
        conn.commit()

AD_LINKS_MAX_TEXT_LENGTH = 3200


def get_ad_links(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, link
                FROM tizimx_ad_links
                WHERE chat_id = %s
                ORDER BY id
            """, (chat_id,))
            rows = cur.fetchall()

    return rows


def add_ad_links(chat_id: int, links: list[str]):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for link in links:
                cur.execute("""
                    INSERT INTO tizimx_ad_links (chat_id, link)
                    VALUES (%s, %s)
                    ON CONFLICT (chat_id, link) DO NOTHING
                """, (chat_id, link))
        conn.commit()

def find_bad_word(chat_id: int, query: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, word
                FROM tizimx_bad_words
                WHERE chat_id = %s
                ORDER BY word
            """, (chat_id,))
            rows = cur.fetchall()

    if not rows:
        return None

    query = query.strip().lower().split()[0]

    if query.isdigit():
        index = int(query)

        if 1 <= index <= len(rows):
            word_id, word = rows[index - 1]
            return {
                "index": index,
                "id": word_id,
                "word": word,
            }

        return None

    for index, (word_id, word) in enumerate(rows, start=1):
        if word.lower() == query:
            return {
                "index": index,
                "id": word_id,
                "word": word,
            }

    return None
