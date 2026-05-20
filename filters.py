import re

URL_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/|@\w+)",
    re.IGNORECASE
)


def has_link(text: str) -> bool:
    if not text:
        return False

    return bool(URL_PATTERN.search(text))
