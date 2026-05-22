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
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS warn_bad_words BOOLEAN NOT NULL DEFAULT FALSE
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS warn_ads BOOLEAN NOT NULL DEFAULT FALSE
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS bad_words_warn_limit INTEGER NOT NULL DEFAULT 3
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS ads_warn_limit INTEGER NOT NULL DEFAULT 3
            """)
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS punish_bad_words BOOLEAN NOT NULL DEFAULT TRUE
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS punish_ads BOOLEAN NOT NULL DEFAULT TRUE
            """)
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS bad_words_punish_seconds INTEGER NOT NULL DEFAULT 86400
            """)
            
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS ads_punish_seconds INTEGER NOT NULL DEFAULT 86400
            """)
            cur.execute("""
                ALTER TABLE tizimx_groups
                ADD COLUMN IF NOT EXISTS anti_usernames BOOLEAN NOT NULL DEFAULT FALSE
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
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_ad_phrases (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    phrase TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(chat_id, phrase)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_ad_exceptions (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    exception TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(chat_id, exception)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_warnings (
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    reason TEXT NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    PRIMARY KEY (chat_id, user_id, reason)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tizimx_required_subs (
                    id BIGSERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    target_chat TEXT NOT NULL,
                    invite_link TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(chat_id, target_chat)
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
                SELECT anti_links, anti_bad_words, silent_mode, clean_service_messages, force_subscribe, warn_bad_words, warn_ads, bad_words_warn_limit, ads_warn_limit, punish_bad_words, punish_ads, bad_words_punish_seconds, ads_punish_seconds, anti_usernames
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
            "force_subscribe": False,
            "warn_bad_words": False,
            "warn_ads": False,
            "bad_words_warn_limit": 3,
            "ads_warn_limit": 3,
            "punish_bad_words": True,
            "punish_ads": True,
            "bad_words_punish_seconds": 86400,
            "ads_punish_seconds": 86400,
            "anti_usernames": False,
        }

    return {
        "anti_links": row[0],
        "anti_bad_words": row[1],
        "silent_mode": row[2],
        "clean_service_messages": row[3],
        "force_subscribe": row[4],
        "warn_bad_words": row[5],
        "warn_ads": row[6],
        "bad_words_warn_limit": row[7],
        "ads_warn_limit": row[8],
        "punish_bad_words": row[9],
        "punish_ads": row[10],
        "bad_words_punish_seconds": row[11],
        "ads_punish_seconds": row[12],
        "anti_usernames": row[13],
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
        "warn_bad_words",
        "warn_ads",
        "punish_bad_words",
        "punish_ads",
        "anti_usernames",
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

def get_ad_links_for_check(chat_id: int) -> list[str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT link FROM tizimx_ad_links WHERE chat_id = %s",
                (chat_id,)
            )
            rows = cur.fetchall()

    return [row[0].lower() for row in rows]

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

def delete_bad_word(chat_id: int, word_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM tizimx_bad_words
                WHERE chat_id = %s AND id = %s
            """, (chat_id, word_id))
        conn.commit()

def get_ad_phrases(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, phrase
                FROM tizimx_ad_phrases
                WHERE chat_id = %s
                ORDER BY id
            """, (chat_id,))
            rows = cur.fetchall()

    return rows


def add_ad_phrases(chat_id: int, phrases: list[str]):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for phrase in phrases:
                cur.execute("""
                    INSERT INTO tizimx_ad_phrases (chat_id, phrase)
                    VALUES (%s, %s)
                    ON CONFLICT (chat_id, phrase) DO NOTHING
                """, (chat_id, phrase))
        conn.commit()


def get_ad_phrases_for_check(chat_id: int) -> list[str]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT phrase FROM tizimx_ad_phrases WHERE chat_id = %s",
                (chat_id,)
            )
            rows = cur.fetchall()

    return [row[0].lower() for row in rows]

def delete_ad_link_by_index(chat_id: int, index: int) -> bool:
    rows = get_ad_links(chat_id)

    if index < 1 or index > len(rows):
        return False

    link_id = rows[index - 1][0]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tizimx_ad_links WHERE chat_id = %s AND id = %s",
                (chat_id, link_id)
            )
        conn.commit()

    return True


def delete_ad_phrase_by_index(chat_id: int, index: int) -> bool:
    rows = get_ad_phrases(chat_id)

    if index < 1 or index > len(rows):
        return False

    phrase_id = rows[index - 1][0]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tizimx_ad_phrases WHERE chat_id = %s AND id = %s",
                (chat_id, phrase_id)
            )
        conn.commit()

    return True

def get_ad_exceptions(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, exception
                FROM tizimx_ad_exceptions
                WHERE chat_id = %s
                ORDER BY id
            """, (chat_id,))
            return cur.fetchall()


def add_ad_exceptions(chat_id: int, exceptions: list[str]):
    with get_connection() as conn:
        with conn.cursor() as cur:
            for exception in exceptions:
                cur.execute("""
                    INSERT INTO tizimx_ad_exceptions (chat_id, exception)
                    VALUES (%s, %s)
                    ON CONFLICT (chat_id, exception) DO NOTHING
                """, (chat_id, exception))
        conn.commit()


def delete_ad_exception_by_index(chat_id: int, index: int) -> bool:
    rows = get_ad_exceptions(chat_id)

    if index < 1 or index > len(rows):
        return False

    exception_id = rows[index - 1][0]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tizimx_ad_exceptions WHERE chat_id = %s AND id = %s",
                (chat_id, exception_id)
            )
        conn.commit()

    return True


def get_ad_exceptions_for_check(chat_id: int) -> list[str]:
    rows = get_ad_exceptions(chat_id)
    return [row[1].lower() for row in rows]

def set_group_number_setting(chat_id: int, key: str, value: int):
    allowed_keys = {
        "bad_words_warn_limit",
        "ads_warn_limit",
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

def add_warning(chat_id: int, user_id: int, reason: str) -> int:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_warnings (chat_id, user_id, reason, count)
                VALUES (%s, %s, %s, 1)
                ON CONFLICT (chat_id, user_id, reason)
                DO UPDATE SET
                    count = tizimx_warnings.count + 1,
                    updated_at = NOW()
                RETURNING count
            """, (chat_id, user_id, reason))

            row = cur.fetchone()

        conn.commit()

    return row[0]

def reset_warnings(chat_id: int, user_id: int, reason: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM tizimx_warnings
                WHERE chat_id = %s AND user_id = %s AND reason = %s
            """, (chat_id, user_id, reason))
        conn.commit()

def remove_group_admin(chat_id: int, user_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM tizimx_group_admins
                WHERE chat_id = %s AND user_id = %s
            """, (chat_id, user_id))
        conn.commit()

def set_punish_duration(chat_id: int, key: str, seconds: int):
    allowed_keys = {
        "bad_words_punish_seconds",
        "ads_punish_seconds",
    }

    if key not in allowed_keys:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"UPDATE tizimx_groups SET {key} = %s WHERE chat_id = %s",
                (seconds, chat_id)
            )
        conn.commit()

def get_required_subs(chat_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, target_chat, invite_link
                FROM tizimx_required_subs
                WHERE chat_id = %s
                ORDER BY id
            """, (chat_id,))
            return cur.fetchall()


def add_required_sub(chat_id: int, target_chat: str, invite_link: str | None = None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tizimx_required_subs (chat_id, target_chat, invite_link)
                VALUES (%s, %s, %s)
                ON CONFLICT (chat_id, target_chat)
                DO UPDATE SET invite_link = EXCLUDED.invite_link
            """, (chat_id, target_chat, invite_link))
        conn.commit()


def delete_required_sub_by_index(chat_id: int, index: int) -> bool:
    rows = get_required_subs(chat_id)

    if index < 1 or index > len(rows):
        return False

    sub_id = rows[index - 1][0]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tizimx_required_subs WHERE chat_id = %s AND id = %s",
                (chat_id, sub_id)
            )
        conn.commit()

    return True

def delete_required_sub_by_id(sub_id: int):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM tizimx_required_subs WHERE id = %s",
                (sub_id,)
            )
        conn.commit()

def copy_settings(source_chat_id: int, target_chat_id: int, state: dict):
    with get_connection() as conn:
        with conn.cursor() as cur:

            if state["delete_settings"]:
                cur.execute("""
                    UPDATE tizimx_groups target
                    SET anti_bad_words = source.anti_bad_words,
                        anti_links = source.anti_links,
                        anti_usernames = source.anti_usernames
                    FROM tizimx_groups source
                    WHERE source.chat_id = %s
                      AND target.chat_id = %s
                """, (source_chat_id, target_chat_id))

            if state["warnings"]:
                cur.execute("""
                    UPDATE tizimx_groups target
                    SET warn_bad_words = source.warn_bad_words,
                        warn_ads = source.warn_ads,
                        bad_words_warn_limit = source.bad_words_warn_limit,
                        ads_warn_limit = source.ads_warn_limit
                    FROM tizimx_groups source
                    WHERE source.chat_id = %s
                      AND target.chat_id = %s
                """, (source_chat_id, target_chat_id))

            if state["restrictions"]:
                cur.execute("""
                    UPDATE tizimx_groups target
                    SET punish_bad_words = source.punish_bad_words,
                        punish_ads = source.punish_ads,
                        bad_words_punish_seconds = source.bad_words_punish_seconds,
                        ads_punish_seconds = source.ads_punish_seconds
                    FROM tizimx_groups source
                    WHERE source.chat_id = %s
                      AND target.chat_id = %s
                """, (source_chat_id, target_chat_id))

            if state["bad_words"]:
                cur.execute("""
                    INSERT INTO tizimx_bad_words (chat_id, word)
                    SELECT %s, word
                    FROM tizimx_bad_words
                    WHERE chat_id = %s
                    ON CONFLICT (chat_id, word) DO NOTHING
                """, (target_chat_id, source_chat_id))

            if state["ads"]:
                cur.execute("""
                    INSERT INTO tizimx_ad_links (chat_id, link)
                    SELECT %s, link
                    FROM tizimx_ad_links
                    WHERE chat_id = %s
                    ON CONFLICT (chat_id, link) DO NOTHING
                """, (target_chat_id, source_chat_id))

                cur.execute("""
                    INSERT INTO tizimx_ad_phrases (chat_id, phrase)
                    SELECT %s, phrase
                    FROM tizimx_ad_phrases
                    WHERE chat_id = %s
                    ON CONFLICT (chat_id, phrase) DO NOTHING
                """, (target_chat_id, source_chat_id))

                cur.execute("""
                    INSERT INTO tizimx_ad_exceptions (chat_id, exception)
                    SELECT %s, exception
                    FROM tizimx_ad_exceptions
                    WHERE chat_id = %s
                    ON CONFLICT (chat_id, exception) DO NOTHING
                """, (target_chat_id, source_chat_id))

        conn.commit()
