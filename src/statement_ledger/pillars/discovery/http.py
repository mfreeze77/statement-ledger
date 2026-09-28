"""Explicit, bounded HTTPS clients. No credentials or upstream bodies in errors.

Endpoint hosts/paths are hard-coded. Redirects are rejected; these clients do not
fetch source URLs discovered in results. Acquiring media is a separate operation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx

from statement_ledger.core.errors import TransientFailure


class SourceError(RuntimeError):
    pass


class SourceUnavailable(SourceError, TransientFailure):
    pass


@dataclass(frozen=True)
class Page:
    payload: dict[str, Any]
    next_cursor: str | None


class JSONClient:
    def __init__(
        self,
        base_url: str,
        *,
        transport=None,
        max_bytes: int = 16 * 1024 * 1024,
        retries: int = 2,
        sleeper=time.sleep,
    ):
        self.client = httpx.Client(
            base_url=base_url,
            transport=transport,
            timeout=30,
            follow_redirects=False,
            trust_env=False,
        )
        self.max_bytes = max_bytes
        self.retries = retries
        self.sleep = sleeper

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def get(self, path: str, params: dict) -> dict:
        for attempt in range(self.retries + 1):
            try:
                with self.client.stream("GET", path, params=params) as response:
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < self.retries:
                            self.sleep(min(2**attempt, 8))
                            continue
                        raise SourceUnavailable(
                            f"Upstream temporarily unavailable ({response.status_code})"
                        )
                    if not 200 <= response.status_code < 300:
                        raise SourceError(
                            f"Upstream request rejected ({response.status_code}); check access settings"
                        )
                    raw = bytearray()
                    for chunk in response.iter_bytes():
                        raw.extend(chunk)
                        if len(raw) > self.max_bytes:
                            raise SourceError("Response exceeds configured bound")
                    import json

                    try:
                        data = json.loads(raw)
                    except (ValueError, UnicodeError):
                        raise SourceError("Upstream returned invalid JSON") from None
                    if not isinstance(data, dict):
                        raise SourceError("Upstream JSON is not an object")
                    return data
            except httpx.TransportError:
                if attempt == self.retries:
                    raise SourceUnavailable("Upstream transport failed") from None
                self.sleep(min(2**attempt, 8))
        raise SourceUnavailable("Retry budget exhausted")


class YouTubeClient(JSONClient):
    def __init__(self, api_key: str, **kw):
        if not api_key:
            raise ValueError("YOUTUBE_API_KEY is required")
        super().__init__("https://www.googleapis.com/youtube/v3/", **kw)
        self.client.headers["X-goog-api-key"] = api_key

    def search(
        self,
        query: str,
        *,
        cursor: str | None = None,
        page_size: int = 50,
        published_after: str | None = None,
        published_before: str | None = None,
    ) -> Page:
        if not query.strip() or not 1 <= page_size <= 50:
            raise ValueError("Query and page size 1..50 required")
        params = {
            "part": "snippet",
            "type": "video",
            "q": query,
            "maxResults": page_size,
        }
        for k, v in (
            ("pageToken", cursor),
            ("publishedAfter", published_after),
            ("publishedBefore", published_before),
        ):
            if v:
                params[k] = v
        data = self.get("search", params)
        return Page(data, data.get("nextPageToken"))

    def uploads_playlist(self, channel_id: str) -> str:
        data = self.get("channels", {"part": "contentDetails", "id": channel_id})
        try:
            return data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        except (KeyError, IndexError, TypeError):
            raise SourceError("Uploads playlist not found") from None

    def playlist(self, playlist_id: str, *, cursor: str | None = None) -> Page:
        p = {
            "part": "snippet,contentDetails",
            "playlistId": playlist_id,
            "maxResults": 50,
        }
        if cursor:
            p["pageToken"] = cursor
        d = self.get("playlistItems", p)
        return Page(d, d.get("nextPageToken"))

    def videos(self, ids: list[str]) -> Page:
        if not 1 <= len(ids) <= 50:
            raise ValueError("Supply 1..50 video IDs")
        return Page(
            self.get(
                "videos",
                {"part": "snippet,contentDetails,status", "id": ",".join(ids)},
            ),
            None,
        )


class FactCheckClient(JSONClient):
    def __init__(self, api_key: str, **kw):
        if not api_key:
            raise ValueError("FACTCHECK_API_KEY is required")
        super().__init__("https://factchecktools.googleapis.com/v1alpha1/", **kw)
        self.client.headers["X-goog-api-key"] = api_key

    def search(
        self, query: str, *, cursor: str | None = None, page_size: int = 20, language: str = "en"
    ) -> Page:
        if not query.strip() or not 1 <= page_size <= 100:
            raise ValueError("Query and bounded page size required")
        p = {"query": query, "languageCode": language, "pageSize": page_size}
        if cursor:
            p["pageToken"] = cursor
        d = self.get("./claims:search", p)
        return Page(d, d.get("nextPageToken"))


class ArchiveClient(JSONClient):
    def __init__(self, **kw):
        super().__init__("https://archive.org/", **kw)

    def search(self, query: str, *, page: int = 1, rows: int = 50) -> Page:
        if not query.strip() or page < 1 or not 1 <= rows <= 100:
            raise ValueError("Invalid search bounds")
        d = self.get(
            "advancedsearch.php",
            {
                "q": query,
                "output": "json",
                "rows": rows,
                "page": page,
                "fl[]": ["identifier", "title", "date", "mediatype"],
            },
        )
        count = d.get("response", {}).get("numFound", 0)
        return Page(d, str(page + 1) if page * rows < count else None)

    def metadata(self, identifier: str) -> dict:
        if not identifier or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"
            for c in identifier
        ):
            raise ValueError("Invalid archive identifier")
        return self.get(f"metadata/{quote(identifier, safe='')}", {})


class AAPBClient(JSONClient):
    def __init__(self, **kw):
        super().__init__("https://americanarchive.org/", **kw)

    def search(self, query: str, *, start: int = 0, rows: int = 50) -> Page:
        if not query.strip() or start < 0 or not 1 <= rows <= 100:
            raise ValueError("Invalid search bounds")
        d = self.get("api.json", {"q": query, "fl": "id,title", "rows": rows, "start": start})
        total = d.get("response", {}).get("numFound")
        cursor = str(start + rows) if isinstance(total, int) and start + rows < total else None
        return Page(d, cursor)
