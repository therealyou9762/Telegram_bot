import re

def enforce_https(url: str) -> str:
    if not url:
        return url
    return re.sub(r'^http://', 'https://', url, flags=re.IGNORECASE)
