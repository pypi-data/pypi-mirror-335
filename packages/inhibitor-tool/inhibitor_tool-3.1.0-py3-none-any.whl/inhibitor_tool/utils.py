import re


def validate_content(content: str) -> bool:
    """Check if the inhibition content is valid (≥10 chars, no spaces)."""
    return len(content) >= 10 and not re.search(r"\s", content)
