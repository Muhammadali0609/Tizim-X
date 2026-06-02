import re

URL_PATTERN = re.compile(
    r"("
    r"https?://"
    r"|www\."
    r"|[a-zA-Z0-9-]+\.(com|ru|uz|net|org|io|app|dev|info|site|shop|xyz|link|tv|gg|ai|tech)\b"
    r")",
    re.IGNORECASE
)

def has_link(text: str) -> bool:
    if not text:
        return False

    return bool(URL_PATTERN.search(text))

DEFAULT_BAD_WORDS = [
    "taqiqsoz1",
    "taqiqsoz2",
    "taqiqsoz3",
]


def has_bad_word(text: str, bad_words: list[str]) -> bool:
    if not text or not bad_words:
        return False

    text = text.lower()

    words = re.findall(r"[^\s,.;:!?()\[\]{}\"“”]+", text)

    bad_words_set = set(word.lower() for word in bad_words)

    return any(word in bad_words_set for word in words)

def has_ad_phrase(text: str, phrases: list[str]) -> bool:
    for phrase in phrases:
        if has_phrase(text, phrase):
            return True

    return False

def has_custom_ad_link(text: str, links: list[str]) -> bool:
    if not text or not links:
        return False

    text = text.lower()

    return any(link.lower() in text for link in links)

def has_ad_exception(text: str, exceptions: list[str]) -> bool:
    for exception in exceptions:
        if has_phrase(text, exception):
            return True

    return False

USERNAME_PATTERN = re.compile(
    r"(?<!\w)@[a-zA-Z0-9_]{5,32}\b"
)

def has_username(text: str) -> bool:
    if not text:
        return False

    return bool(USERNAME_PATTERN.search(text))

def has_phrase(text: str, keyword: str) -> bool:
    text = text.lower()
    keyword = keyword.lower().strip()

    pattern = r'(?<!\w)' + re.escape(keyword) + r'(?!\w)'

    return re.search(pattern, text, flags=re.IGNORECASE) is not None