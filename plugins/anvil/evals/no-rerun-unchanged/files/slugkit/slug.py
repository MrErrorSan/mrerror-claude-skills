import re
import unicodedata


def slugify(text: str, max_length: int = 60) -> str:
    """Lowercase ASCII words joined by single hyphens, cut at a word boundary."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    words = re.findall(r"[a-z0-9]+", ascii_text.lower())
    slug = ""
    for word in words:
        candidate = f"{slug}-{word}" if slug else word
        if len(candidate) > max_length:
            break
        slug = candidate
    return slug
