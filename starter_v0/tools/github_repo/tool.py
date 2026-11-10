from __future__ import annotations

import os
import re
from typing import Any

import requests

from tools._shared import TIMEOUT, err

# owner/name, optionally written as a github.com URL (with or without scheme, .git or a trailing path)
REPO_PATTERN = re.compile(
    r"^(?:https?://)?(?:www\.)?(?:github\.com/)?(?P<owner>[A-Za-z0-9-]{1,39})/(?P<name>[A-Za-z0-9._-]{1,100}?)(?:\.git)?(?:/.*)?$"
)


def parse_repo(repo: str) -> tuple[str, str]:
    match = REPO_PATTERN.match(repo.strip()) if isinstance(repo, str) else None
    if not match:
        raise ValueError(f"repo must be 'owner/name' or a github.com URL, got {repo!r}")
    return match["owner"], match["name"]


def github_repo_info(repo: str = "") -> dict[str, Any]:
    """Current state of one public GitHub repository (stars, last push, license...)."""
    try:
        owner, name = parse_repo(repo)
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI20k-Day03-Research-Agent"}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"https://api.github.com/repos/{owner}/{name}", headers=headers, timeout=TIMEOUT)
        if response.status_code == 404:
            raise LookupError(f"GitHub repo {owner}/{name} not found (or private)")
        response.raise_for_status()
        data = response.json()
        license_id = (data.get("license") or {}).get("spdx_id")
        facts = {
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "open_issues": data.get("open_issues_count"),
            "license": license_id,
            "language": data.get("language"),
            "last_push": data.get("pushed_at"),
            "archived": bool(data.get("archived")),
        }
        summary = (
            f"{data.get('description') or ''} | stars {facts['stars']}, forks {facts['forks']}, "
            f"open issues {facts['open_issues']}, license {license_id}, last push {facts['last_push']}"
            + (", ARCHIVED" if facts["archived"] else "")
        ).strip(" |")
        return {
            "tool": "github_repo_info",
            "repo": f"{owner}/{name}",
            **facts,
            "items": [{
                "title": data.get("full_name") or f"{owner}/{name}",
                "url": data.get("html_url") or f"https://github.com/{owner}/{name}",
                "source": "github.com",
                "summary": summary,
            }],
        }
    except Exception as exc:
        return err("github_repo_info", exc)
