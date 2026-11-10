"""Streamlit UI for the RICONs research agent.

Run from starter_v0/:
    streamlit run app.py

The UI reuses the tool loop and transcript writer from chat.py, so a chat in the
browser behaves exactly like `python chat.py` and is logged to
transcripts/*.transcript.json in the same format. Every tool call and its raw
result (including errors) is shown under each answer; nothing is hidden.
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import ARTIFACTS_DIR, ROOT, now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# chat.py prints tool calls with emoji; Windows' default cp1252 console cannot encode them.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROVIDER = "openrouter"
DEFAULT_MODEL = os.getenv("AGENT_MODEL", "anthropic/claude-haiku-5.5")
DEFAULT_VERSION = os.getenv("AGENT_VERSION", "ui")
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
HISTORY_WINDOW = 5
MAX_TOOL_ROUNDS = 4
MAX_TURNS_PER_SESSION = 20  # the link is public; this caps what one visitor can spend

SAMPLE_QUESTIONS = [
    "Alan Turing là ai?",
    "Tin tức AI hôm nay có gì nổi bật?",
    "Mọi người đang bàn gì về Claude trên Twitter?",
    "Tóm tắt bài này giúp mình: https://www.anthropic.com/research",
    "Tóm tắt 5 tweet mới nhất giúp mình",
    "Đăng bản tin AI hôm nay lên Telegram giúp mình",
]


@st.cache_resource
def get_provider() -> Any:
    return make_provider(PROVIDER)


def load_artifacts() -> tuple[str, list[dict[str, Any]]]:
    # Read on every turn so an edited prompt/tools.yaml is picked up without a restart.
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    tools = to_openai_tools(load_tool_declarations(TOOLS_PATH))
    return system_prompt, tools


def new_session(version: str, model: str) -> None:
    artifact_version = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    transcript_id = "_".join([safe_slug(version), "streamlit", PROVIDER, datetime.now().strftime("%Y%m%dT%H%M%S%f")])
    st.session_state.history = []
    st.session_state.turns = []
    st.session_state.transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        "source": "streamlit",
        **artifact_version_dict(artifact_version),
        "provider": PROVIDER,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": HISTORY_WINDOW,
        "max_tool_rounds": MAX_TOOL_ROUNDS,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }


def render_tool_events(events: list[dict[str, Any]]) -> None:
    if not events:
        st.caption("Không gọi tool nào.")
        return
    for event in events:
        result = event.get("result")
        failed = isinstance(result, dict) and "error" in result
        label = f"{'⚠️' if failed else '🔧'} {event.get('tool')}({event.get('args')})"
        with st.expander(label, expanded=failed):
            if failed:
                st.error(f"{result.get('error')}: {result.get('message', '')}")
            st.json(result, expanded=False)


def render_turn(turn: dict[str, Any]) -> None:
    with st.chat_message("user"):
        st.markdown(turn["user"])
    with st.chat_message("assistant"):
        if turn["status"] == "provider_error":
            st.error(f"Provider error: {turn.get('error')}")
        else:
            st.markdown(turn.get("assistant_text") or "")
        render_tool_events(turn.get("tool_events", []))
        st.caption(f"status: {turn['status']} · rounds: {len(turn.get('rounds', []))}")


def run_turn(user_text: str, model: str) -> None:
    system_prompt, tools = load_artifacts()
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, HISTORY_WINDOW),
        {"role": "user", "content": user_text},
    ]
    turn: dict[str, Any] = {
        "turn_index": len(st.session_state.turns) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    try:
        result = run_model_tool_loop(
            provider=get_provider(),
            messages=messages,
            tools=tools,
            model=model,
            max_tool_rounds=MAX_TOOL_ROUNDS,
        )
        turn.update(result)
        st.session_state.history += [
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": result["assistant_text"]},
        ]
    except Exception as exc:  # show provider failures instead of hiding them
        turn.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
    turn["ended_at"] = now_iso()
    st.session_state.turns.append(turn)
    st.session_state.transcript["turns"].append(turn)
    write_transcript(st.session_state.transcript_path, st.session_state.transcript)


def main() -> None:
    st.set_page_config(page_title="RICONs Research Agent", page_icon="🔎")

    with st.sidebar:
        st.header("RICONs Research Agent")
        model = st.text_input("Model (OpenRouter)", DEFAULT_MODEL, help="Áp dụng khi bấm 'Cuộc trò chuyện mới'.")
        version = st.text_input("Version label", DEFAULT_VERSION, help="Áp dụng khi bấm 'Cuộc trò chuyện mới'.")
        if "transcript" not in st.session_state:
            new_session(version, model)
        if st.button("Cuộc trò chuyện mới", use_container_width=True):
            new_session(version, model)
        transcript = st.session_state.transcript
        st.caption(f"model: `{transcript['model']}`")
        st.caption(f"artifact_version: `{transcript['artifact_version']}`")
        st.caption(f"transcript: `{Path(st.session_state.transcript_path).name}`")
        st.divider()
        st.subheader("Câu hỏi mẫu")
        for question in SAMPLE_QUESTIONS:
            if st.button(question, use_container_width=True):
                st.session_state.pending = question

    st.title("🔎 Research Agent")
    st.caption(
        "Agent tra web, Wikipedia, Twitter/X và đọc link. "
        "Thiếu thông tin thì hỏi lại; chỉ đăng Telegram sau khi bạn xác nhận. "
        "Mỗi câu trả lời kèm tool call và kết quả thô bên dưới."
    )

    for turn in st.session_state.turns:
        render_turn(turn)

    user_text = st.chat_input("Hỏi agent...") or st.session_state.pop("pending", None)
    if not user_text:
        return
    if len(st.session_state.turns) >= MAX_TURNS_PER_SESSION:
        st.warning(f"Đã đạt giới hạn {MAX_TURNS_PER_SESSION} lượt; bấm 'Cuộc trò chuyện mới' để tiếp tục.")
        return
    with st.spinner("Agent đang xử lý..."):
        run_turn(user_text, st.session_state.transcript["model"])
    render_turn(st.session_state.turns[-1])


main()
