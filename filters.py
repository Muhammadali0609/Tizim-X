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
    if not text or not phrases:
        return False

    text = " ".join(text.lower().split())

    for phrase in phrases:
        normalized_phrase = " ".join(phrase.lower().split())

        if normalized_phrase and normalized_phrase in text:
            return True

    return False

def has_custom_ad_link(text: str, links: list[str]) -> bool:
    if not text or not links:
        return False

    text = text.lower()

    return any(link.lower() in text for link in links)

def has_ad_exception(text: str, exceptions: list[str]) -> bool:
    if not text or not exceptions:
        return False

    text = text.lower()

    return any(exception in text for exception in exceptions)

USERNAME_PATTERN = re.compile(
    r"(?<!\w)@[a-zA-Z0-9_]{5,32}\b"
)

def has_username(text: str) -> bool:
    if not text:
        return False

    return bool(USERNAME_PATTERN.search(text))
