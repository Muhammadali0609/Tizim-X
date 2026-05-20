import re

URL_PATTERN = re.compile(
    r"("
    r"https?://"
    r"|www\."
    r"|t\.me/"
    r"|telegram\.me/"
    r"|@\w+"
    r"|[a-zA-Z0-9-]+\.(com|ru|uz|net|org|io|app|dev|co|me|info|biz|site|online|shop|xyz|link|tv|gg|ai|tech)\b"
    r")",
    re.IGNORECASE
)

def has_link(text: str) -> bool:
    if not text:
        return False

    return bool(URL_PATTERN.search(text))
