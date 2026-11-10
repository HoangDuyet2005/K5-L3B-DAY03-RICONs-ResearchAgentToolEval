from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err

LANGS = ("vi", "en")
MAX_RESULTS = 5
SUMMARY_CHARS = 1200
DEFAULT_USER_AGENT = "AI20k-Day03-Research-Agent/1.0 (educational lab)"


def wiki_search(query: str = "", lang: str = "vi", max_results: int = 1) -> dict[str, Any]:
    """Search Wikipedia and return the intro of the best-matching articles.

    One MediaWiki API call does both the search and the intro extract, so the
    tool is a single request. Bad input from the model is either normalised
    (numeric strings, out-of-range counts, case of `lang`) or returned as an
    error dict; the tool never raises.
    """
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        lang = str(lang or "vi").strip().lower()
        if lang not in LANGS:
            raise ValueError(f"lang must be one of {list(LANGS)}, got {lang!r}")
        count = min(max(int(max_results or 1), 1), MAX_RESULTS)

        response = requests.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "format": "json",
                "formatversion": 2,
                "generator": "search",
                "gsrsearch": query.strip(),
                "gsrlimit": count,
                "prop": "extracts|info",
                "exintro": 1,
                "explaintext": 1,
                "exchars": SUMMARY_CHARS,
                "inprop": "url",
                "redirects": 1,
            },
            headers={"User-Agent": os.getenv("WIKI_USER_AGENT") or DEFAULT_USER_AGENT},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        pages = (response.json().get("query") or {}).get("pages") or []
        # The API returns pages unordered; `index` is the search rank.
        pages = sorted(pages, key=lambda page: page.get("index", 0))[:count]
        items = [{
            "title": page.get("title"),
            "url": page.get("fullurl"),
            "source": f"{lang}.wikipedia.org",
            "summary": (page.get("extract") or "")[:SUMMARY_CHARS],
        } for page in pages if page.get("title")]
        return {"tool": "wiki_search", "query": query.strip(), "lang": lang, "items": items}
    except Exception as exc:
        return err("wiki_search", exc)
