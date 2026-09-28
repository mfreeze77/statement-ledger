import hashlib
import json
import re
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def stable_id(source: str, native_id: str) -> str:
    return f"{source}:{hashlib.sha256(native_id.encode()).hexdigest()[:32]}"


def canonical_url(url: str) -> str:
    """Discovery comparison only. Never replace the preserved original source URL."""
    p = urlsplit(url)
    if p.scheme not in {"http", "https"} or not p.netloc or p.username or p.password:
        raise ValueError("Expected a public HTTP(S) URL without credentials")
    pairs = [
        (k, v)
        for k, v in parse_qsl(p.query, keep_blank_values=True)
        if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}
    ]
    return urlunsplit(
        (p.scheme.lower(), p.netloc.lower(), p.path or "/", urlencode(pairs), p.fragment)
    )


def normalized_quote(text: str) -> str:
    # Candidate generation only: negation, numerals, and punctuation are not stripped.
    return re.sub(r"\s+", " ", text).strip().casefold()
