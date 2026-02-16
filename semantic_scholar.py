"""Semantic Scholar API helper functions."""
from __future__ import annotations

import json
import os
import time
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.semanticscholar.org/graph/v1"


def _get_api_key(api_key: Optional[str] = None) -> Optional[str]:
    return api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")


def _request_json(
    path: str,
    params: dict[str, Any] | None = None,
    api_key: Optional[str] = None,
    max_retries: int = 2,
    timeout: int = 10,
) -> dict[str, Any]:
    query = f"?{urlencode(params)}" if params else ""
    url = f"{BASE_URL}{path}{query}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "paper-to-notebook/1.0",
    }
    key = _get_api_key(api_key)
    if key:
        headers["x-api-key"] = key

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            req = Request(url, headers=headers)
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body)
        except HTTPError as e:
            last_error = e
            if e.code in (429, 500, 502, 503, 504) and attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            raise
        except URLError as e:
            last_error = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue
            raise
    if last_error:
        raise last_error
    raise RuntimeError("Semantic Scholar request failed unexpectedly.")


def search_papers(query: str, limit: int = 8, api_key: Optional[str] = None) -> dict[str, Any]:
    fields = ",".join(
        [
            "title",
            "authors",
            "year",
            "venue",
            "citationCount",
            "openAccessPdf",
            "externalIds",
            "url",
        ]
    )
    return _request_json(
        "/paper/search",
        params={"query": query, "limit": limit, "fields": fields},
        api_key=api_key,
    )


def get_paper(paper_id: str, api_key: Optional[str] = None) -> dict[str, Any]:
    fields = ",".join(
        [
            "title",
            "authors",
            "year",
            "venue",
            "citationCount",
            "openAccessPdf",
            "externalIds",
            "url",
        ]
    )
    return _request_json(
        f"/paper/{paper_id}",
        params={"fields": fields},
        api_key=api_key,
    )
