from __future__ import annotations

from typing import Any

import requests

from tools._shared import TIMEOUT, err

MAX_LIMIT = 5


def search_hf_models(query: str = "", limit: int = 3) -> dict[str, Any]:
    """Model-card facts (license, task, downloads) from the Hugging Face Hub, most downloaded first."""
    try:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query must be a non-empty string (model name or id, e.g. 'Qwen/Qwen2.5-7B-Instruct')")
        count = min(max(int(3 if limit in (None, "") else limit), 1), MAX_LIMIT)
        response = requests.get(
            "https://huggingface.co/api/models",
            params={"search": query.strip(), "sort": "downloads", "limit": count, "full": "true"},
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        items = []
        for model in (response.json() or [])[:count]:
            model_id = model.get("id") if isinstance(model, dict) else None
            if not model_id:
                continue
            licenses = [tag.split(":", 1)[1] for tag in model.get("tags", []) if tag.startswith("license:")]
            license_name = licenses[0] if licenses else None
            items.append({
                "title": model_id,
                "url": f"https://huggingface.co/{model_id}",
                "source": "huggingface.co",
                "summary": (
                    f"task {model.get('pipeline_tag')}, license {license_name}, "
                    f"downloads {model.get('downloads')}, likes {model.get('likes')}, "
                    f"gated {model.get('gated') or False}, last modified {str(model.get('lastModified') or '')[:10]}"
                ),
                "license": license_name,
                "downloads": model.get("downloads"),
            })
        return {"tool": "search_hf_models", "query": query.strip(), "items": items}
    except Exception as exc:
        return err("search_hf_models", exc)
