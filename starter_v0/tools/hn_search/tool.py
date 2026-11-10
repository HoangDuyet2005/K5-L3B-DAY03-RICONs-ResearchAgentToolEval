from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, domain, err

SORTS = {"relevance": "search", "latest": "search_by_date"}
MAX_LIMIT = 10


def search_hacker_news(query: str = "", sort: str = "relevance", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News stories through the public Algolia API."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string")
        sort = str(sort or "relevance").strip().lower()
        if sort not in SORTS:
            raise ValueError(f"sort must be one of {list(SORTS)}, got {sort!r}")
        count = min(max(int(5 if limit in (None, "") else limit), 1), MAX_LIMIT)
        response = requests.get(
            f"https://hn.algolia.com/api/v1/{SORTS[sort]}",
            params={"query": query.strip(), "tags": "story", "hitsPerPage": count},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = []
        for hit in (response.json().get("hits") or [])[:count]:
            story_id = hit.get("objectID")
            if not story_id or not hit.get("title"):
                continue
            discussion = f"https://news.ycombinator.com/item?id={story_id}"
            link = hit.get("url") or discussion
            items.append({
                "title": hit.get("title"),
                "url": link,
                "source": domain(link) if hit.get("url") else "news.ycombinator.com",
                "summary": (
                    f"{hit.get('points') or 0} points, {hit.get('num_comments') or 0} comments, "
                    f"{hit.get('created_at', '')[:10]}; HN discussion: {discussion}"
                ),
            })
        return {"tool": "search_hacker_news", "query": query.strip(), "sort": sort, "items": items}
    except Exception as exc:
        return err("search_hacker_news", exc)
