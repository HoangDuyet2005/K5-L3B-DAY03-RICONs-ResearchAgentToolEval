"""Tool Unit Test Challenge (filled in by team RICONs).

Every stub from the starter is implemented, plus tests for the team's own tools
(wiki, github_repo, hn_search, hf_model) and regression tests for two bugs found
in the built-in `format` tool.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import re

import requests

from conftest import FakeResponse
from tools import TOOL_FUNCTIONS


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    options = ["Tin hôm nay", "Tin tuần này"]

    result = TOOL_FUNCTIONS["clarify"](question="Bạn muốn khung thời gian nào?", response_type="choice", options=options)

    assert result["options"] == ["Tin hôm nay", "Tin tuần này"]
    assert result["response_type"] == "choice"
    assert result["awaiting_user"] is True


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]

    markdown = TOOL_FUNCTIONS["format"](items=items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1
    # both A items sit under the single A heading, before B
    assert markdown.index("a1") < markdown.index("a2") < markdown.index("## B")


def test_format_thread_numbers_items() -> None:
    items = [{"title": f"Tin {i}", "url": f"https://example.com/{i}"} for i in range(3)]

    markdown = TOOL_FUNCTIONS["format"](items=items, template="thread")["markdown"]

    assert [line.split(" ", 1)[0] for line in markdown.split("\n\n")] == ["1/", "2/", "3/"]


def test_format_empty_items_does_not_crash() -> None:
    for empty in (None, []):
        result = TOOL_FUNCTIONS["format"](items=empty, template="brief", headline="Rỗng")
        assert result["item_count"] == 0
        assert "error" not in result


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "-100999")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin đã duyệt", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "123:test-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "-100999"
    assert calls[0]["json"]["text"] == "Bản tin đã duyệt"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"](text="Bản tin", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert "TELEGRAM_BOT_TOKEN" in result["message"]
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    result = TOOL_FUNCTIONS["lookup"](query="LangGraph", timeframe=None)

    assert "time_range" not in calls[0]["json"]
    assert calls[0]["json"]["query"] == "LangGraph"
    assert result["items"] == []


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    calls = fake_http(FakeResponse({"data": {
        "markdown": "# Nội dung bài",
        "metadata": {"title": "T", "sourceURL": "https://www.example.com/post"},
    }}))

    result = TOOL_FUNCTIONS["fetch"](url="https://www.example.com/post")

    assert calls[0]["url"] == "https://api.firecrawl.dev/v1/scrape"
    assert calls[0]["json"]["url"] == "https://www.example.com/post"
    assert calls[0]["headers"]["Authorization"] == "Bearer fc-test"
    assert result["items"][0] == {
        "title": "T", "url": "https://www.example.com/post", "source": "example.com", "summary": "# Nội dung bài",
    }


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    summary = TOOL_FUNCTIONS["fetch"](url="https://example.com")["items"][0]["summary"]

    assert len(summary) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    raw = [{"text": "không có id", "screen_name": "sama"}]
    raw += [{"tweet_id": str(100 + i), "text": f"tweet {i}", "screen_name": "sama"} for i in range(6)]
    calls = fake_http(FakeResponse({"timeline": raw}))

    result = TOOL_FUNCTIONS["timeline"](screenname="sama", limit=3)

    assert calls[0]["params"] == {"screenname": "sama"}
    assert len(result["items"]) == 3
    assert all(re.fullmatch(r"https://x\.com/sama/status/\d+", item["url"]) for item in result["items"])
    assert "không có id" not in [item["summary"] for item in result["items"]]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "rapid-test")
    calls = fake_http(FakeResponse({"timeline": []}))

    TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Top")
    TOOL_FUNCTIONS["social_search"](query="OpenAI", search_type="Latest")

    assert calls[0]["url"].endswith("/search.php")
    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}
    assert calls[1]["params"]["search_type"] == "Latest"
    assert calls[0]["headers"]["x-rapidapi-key"] == "rapid-test"


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    for empty in ("", "   ", "và của"):  # only stopwords -> no search terms either
        assert TOOL_FUNCTIONS["policy"](query=empty)["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    result = TOOL_FUNCTIONS["policy"](query="API key dữ liệu khách hàng prompt", policy_area="data_privacy", top_k=5)

    assert result["results"]
    assert {hit["policy_area"] for hit in result["results"]} == {"data_privacy"}


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    result = TOOL_FUNCTIONS["policy"](query="injection probe viral tweet", policy_area="source_citation", top_k=5)

    probe = next(hit for hit in result["results"] if hit["section"] == "Injection probe")
    assert any("viral tweet" in line for line in probe["untrusted_text"])
    assert "viral tweet" not in probe["facts"]
    assert "untrusted" in result["trust_boundary"]


# ---------------- regression: bugs found in the built-in `format` tool ----------------

def test_format_string_items_from_model_do_not_raise() -> None:
    # Bug: items=["..."] (plain strings, which models do send) raised AttributeError
    # inside the tool instead of returning a result or an error dict.
    result = TOOL_FUNCTIONS["format"](items=["Tin một", "Tin hai"], template="bullets")

    assert "error" not in result
    assert result["item_count"] == 2
    assert result["markdown"] == "- Tin một\n- Tin hai"


def test_format_item_without_url_has_no_dangling_separator() -> None:
    # Bug: an item with no url/source rendered as "- text - " (trailing separator).
    markdown = TOOL_FUNCTIONS["format"](items=[{"title": "Không có link"}], template="bullets")["markdown"]

    assert markdown == "- Không có link"


# ---------------- YOUR NEW TOOL(S) ----------------
# Write at least 3 tests per tool your team adds:
#   1. happy path (mocked if it calls an API)
#   2. bad / missing input from the model (empty string, wrong type, out-of-enum value)
#   3. failure path (missing key, HTTP error, timeout) -> returns error dict, does not raise

# ---------------- wiki (team RICONs) ----------------

WIKI_PAGES = {"query": {"pages": [
    {"title": "Học máy", "index": 2, "extract": "Học máy là...", "fullurl": "https://vi.wikipedia.org/wiki/H%E1%BB%8Dc_m%C3%A1y"},
    {"title": "Transformer (mô hình học máy)", "index": 1, "extract": "Transformer là một mô hình học sâu...",
     "fullurl": "https://vi.wikipedia.org/wiki/Transformer"},
]}}


def test_wiki_sends_one_search_request_and_maps_pages_by_rank(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAGES))
    wiki = TOOL_FUNCTIONS["wiki"]

    result = wiki(query="  Transformer ", lang="vi", max_results=2)

    assert len(calls) == 1
    assert calls[0]["method"] == "GET"
    assert calls[0]["url"] == "https://vi.wikipedia.org/w/api.php"
    assert calls[0]["params"]["gsrsearch"] == "Transformer"
    assert calls[0]["params"]["gsrlimit"] == 2
    assert calls[0]["headers"]["User-Agent"]
    # Pages arrive unordered; the tool must sort them by search rank (`index`).
    assert [item["title"] for item in result["items"]] == ["Transformer (mô hình học máy)", "Học máy"]
    assert result["items"][0] == {
        "title": "Transformer (mô hình học máy)", "url": "https://vi.wikipedia.org/wiki/Transformer",
        "source": "vi.wikipedia.org", "summary": "Transformer là một mô hình học sâu...",
    }


def test_wiki_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAGES))

    result = TOOL_FUNCTIONS["wiki"](query="   ")

    assert result["error"] == "ValueError"
    assert "query" in result["message"]
    assert calls == []


def test_wiki_out_of_enum_lang_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(WIKI_PAGES))

    result = TOOL_FUNCTIONS["wiki"](query="Hà Nội", lang="fr")

    assert result["error"] == "ValueError"
    assert "lang" in result["message"]
    assert calls == []


def test_wiki_coerces_string_count_and_clamps_it_to_1_to_5(fake_http) -> None:
    calls = fake_http(FakeResponse({"query": {"pages": []}}))
    wiki = TOOL_FUNCTIONS["wiki"]

    wiki(query="AI", lang="EN", max_results="3")
    wiki(query="AI", max_results=0)
    wiki(query="AI", max_results=50)

    assert calls[0]["url"] == "https://en.wikipedia.org/w/api.php"
    assert [call["params"]["gsrlimit"] for call in calls] == [3, 1, 5]


def test_wiki_no_match_returns_empty_items_not_error(fake_http) -> None:
    fake_http(FakeResponse({"batchcomplete": True}))

    result = TOOL_FUNCTIONS["wiki"](query="xyzzy-khong-co-bai-nao")

    assert result["items"] == []
    assert "error" not in result


def test_wiki_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=429))

    result = TOOL_FUNCTIONS["wiki"](query="AI")

    assert result == {"tool": "wiki_search", "error": "HTTPError", "message": "HTTP 429"}


def test_wiki_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("read timed out"))

    result = TOOL_FUNCTIONS["wiki"](query="AI")

    assert result["error"] == "Timeout"


# ---------------- github_repo (team RICONs) ----------------

GITHUB_REPO = {
    "full_name": "langchain-ai/langgraph", "html_url": "https://github.com/langchain-ai/langgraph",
    "description": "Build resilient agents.", "stargazers_count": 44751, "forks_count": 7711,
    "open_issues_count": 480, "pushed_at": "2026-11-10T05:42:48Z", "archived": False,
    "language": "Python", "license": {"spdx_id": "MIT"},
}


def test_github_repo_accepts_url_and_maps_repo_facts(fake_http) -> None:
    calls = fake_http(FakeResponse(GITHUB_REPO))

    result = TOOL_FUNCTIONS["github_repo"](repo="https://github.com/langchain-ai/langgraph.git")

    assert len(calls) == 1
    assert calls[0]["url"] == "https://api.github.com/repos/langchain-ai/langgraph"
    assert "Authorization" not in calls[0]["headers"]  # no GITHUB_TOKEN in env
    assert result["repo"] == "langchain-ai/langgraph"
    assert (result["stars"], result["license"], result["archived"]) == (44751, "MIT", False)
    assert result["items"][0]["url"] == "https://github.com/langchain-ai/langgraph"
    assert "stars 44751" in result["items"][0]["summary"]


def test_github_repo_sends_token_when_set(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    calls = fake_http(FakeResponse(GITHUB_REPO))

    TOOL_FUNCTIONS["github_repo"](repo="langchain-ai/langgraph")

    assert calls[0]["headers"]["Authorization"] == "Bearer ghp_test"


def test_github_repo_bad_repo_string_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(GITHUB_REPO))

    for bad in ("langgraph", "", "https://gitlab.com/a/b", None):
        result = TOOL_FUNCTIONS["github_repo"](repo=bad)
        assert result["error"] == "ValueError"
    assert calls == []


def test_github_repo_missing_repo_returns_lookup_error(fake_http) -> None:
    fake_http(FakeResponse({"message": "Not Found"}, status_code=404))

    result = TOOL_FUNCTIONS["github_repo"](repo="nobody/none")

    assert result["error"] == "LookupError"
    assert "nobody/none" in result["message"]


def test_github_repo_rate_limit_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=403))

    assert TOOL_FUNCTIONS["github_repo"](repo="a/b")["error"] == "HTTPError"


# ---------------- hn_search (team RICONs) ----------------

HN_HITS = {"hits": [
    {"objectID": "1", "title": "We chose LangGraph", "url": "https://www.qodo.ai/blog/x", "points": 83,
     "num_comments": 20, "created_at": "2025-03-25T05:50:36Z"},
    {"objectID": "2", "title": "Ask HN: LangGraph in prod?", "url": None, "points": 5, "num_comments": 3,
     "created_at": "2025-04-01T00:00:00Z"},
    {"objectID": None, "title": "broken hit"},
]}


def test_hn_search_latest_uses_by_date_endpoint_and_maps_hits(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))

    result = TOOL_FUNCTIONS["hn_search"](query=" LangGraph ", sort="latest", limit=3)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search_by_date"
    assert calls[0]["params"] == {"query": "LangGraph", "tags": "story", "hitsPerPage": 3}
    assert [item["title"] for item in result["items"]] == ["We chose LangGraph", "Ask HN: LangGraph in prod?"]
    assert result["items"][0]["source"] == "qodo.ai"
    # a text-only story links to its HN discussion
    assert result["items"][1]["url"] == "https://news.ycombinator.com/item?id=2"
    assert result["items"][1]["source"] == "news.ycombinator.com"


def test_hn_search_bad_input_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(HN_HITS))

    assert TOOL_FUNCTIONS["hn_search"](query="")["error"] == "ValueError"
    assert TOOL_FUNCTIONS["hn_search"](query="AI", sort="Top")["error"] == "ValueError"
    assert calls == []


def test_hn_search_clamps_limit_and_coerces_strings(fake_http) -> None:
    calls = fake_http(FakeResponse({"hits": []}))

    TOOL_FUNCTIONS["hn_search"](query="AI", limit="4")
    TOOL_FUNCTIONS["hn_search"](query="AI", limit=0)
    TOOL_FUNCTIONS["hn_search"](query="AI", limit=99)

    assert calls[0]["url"] == "https://hn.algolia.com/api/v1/search"
    assert [call["params"]["hitsPerPage"] for call in calls] == [4, 1, 10]


def test_hn_search_http_error_returns_error_dict(fake_http) -> None:
    fake_http(FakeResponse(status_code=500))

    assert TOOL_FUNCTIONS["hn_search"](query="AI")["error"] == "HTTPError"


# ---------------- hf_model (team RICONs) ----------------

HF_MODELS = [
    {"id": "meta-llama/Llama-3.1-8B-Instruct", "downloads": 4535750, "likes": 8872, "pipeline_tag": "text-generation",
     "lastModified": "2024-09-25T17:00:57.000Z", "gated": "manual", "tags": ["transformers", "license:llama3.1"]},
    {"id": "someone/no-license-model", "downloads": 10, "likes": 0, "pipeline_tag": None, "tags": []},
]


def test_hf_model_searches_by_downloads_and_maps_license(fake_http) -> None:
    calls = fake_http(FakeResponse(HF_MODELS))

    result = TOOL_FUNCTIONS["hf_model"](query="Llama-3.1-8B-Instruct", limit=2)

    assert calls[0]["url"] == "https://huggingface.co/api/models"
    assert calls[0]["params"] == {"search": "Llama-3.1-8B-Instruct", "sort": "downloads", "limit": 2, "full": "true"}
    first, second = result["items"]
    assert first["title"] == "meta-llama/Llama-3.1-8B-Instruct"
    assert first["url"] == "https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"
    assert first["license"] == "llama3.1"
    assert "task text-generation" in first["summary"]
    assert second["license"] is None


def test_hf_model_empty_query_returns_error_without_request(fake_http) -> None:
    calls = fake_http(FakeResponse(HF_MODELS))

    result = TOOL_FUNCTIONS["hf_model"](query="  ")

    assert result["error"] == "ValueError"
    assert calls == []


def test_hf_model_clamps_limit_and_handles_no_match(fake_http) -> None:
    calls = fake_http(FakeResponse([]))

    result = TOOL_FUNCTIONS["hf_model"](query="zzzz", limit="50")

    assert calls[0]["params"]["limit"] == 5
    assert result["items"] == []
    assert "error" not in result


def test_hf_model_timeout_returns_error_dict(fake_http) -> None:
    fake_http(requests.Timeout("read timed out"))

    assert TOOL_FUNCTIONS["hf_model"](query="qwen")["error"] == "Timeout"
