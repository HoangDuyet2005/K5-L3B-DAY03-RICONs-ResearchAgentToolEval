"""TODO CP3 (student): Tool Unit Test Challenge.

Each test below is a stub. Replace `pytest.skip(...)` with a real test.
Patterns to copy are in test_tools_examples.py. Fixtures are in conftest.py.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import pytest

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools import TOOL_FUNCTIONS  # noqa: F401

TODO = "TODO CP3 (student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    pytest.skip(TODO)


# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    # Items with section "A", "B", "A" -> markdown has exactly one "## A" and one "## B".
    pytest.skip(TODO)


def test_format_thread_numbers_items() -> None:
    # template="thread" -> lines start with "1/", "2/", ...
    pytest.skip(TODO)


def test_format_empty_items_does_not_crash() -> None:
    # items=None and items=[] -> item_count == 0, no exception.
    pytest.skip(TODO)


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    # Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID, mock HTTP.
    # Assert: exactly one POST, URL contains the token, json has chat_id + text, status == "sent".
    pytest.skip(TODO)


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    pytest.skip(TODO)


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    # timeframe=None -> request body has no "time_range" key.
    pytest.skip(TODO)


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    # Mock {"data": {"markdown": "...", "metadata": {"title": "T", "sourceURL": "https://..."}}}
    # Assert title/url/source/summary in result["items"][0].
    pytest.skip(TODO)


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    pytest.skip(TODO)


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    # Mock {"timeline": [...]} with 1 item missing tweet_id and 6 valid items, limit=3.
    # Assert 3 items, and each url looks like https://x.com/<handle>/status/<id>.
    pytest.skip(TODO)


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    # Assert the request params carry the query and search_type ("Top" / "Latest").
    pytest.skip(TODO)


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    pytest.skip(TODO)


def test_policy_area_filter_only_returns_that_area() -> None:
    # policy_area="data_privacy" -> every result has policy_area == "data_privacy".
    pytest.skip(TODO)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    # One policy file contains a quoted line that tries to give the assistant orders.
    # Query that section (source_citation) and assert: that line is in untrusted_text, NOT in facts.
    pytest.skip(TODO)


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
    import requests

    fake_http(requests.Timeout("read timed out"))

    result = TOOL_FUNCTIONS["wiki"](query="AI")

    assert result["error"] == "Timeout"
