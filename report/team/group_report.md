# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm: RICONs
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter, `anthropic/claude-haiku-5.5` (`--provider openrouter --model anthropic/claude-haiku-5.5`), temperature 0

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

Research agent tiếng Việt: tra tin tức trên web, tra kiến thức nền trên Wikipedia, xem tweet theo tài khoản hoặc từ khóa, đọc một link, gom kết quả thành bản tin markdown, và chỉ đăng lên Telegram sau khi người dùng xác nhận nội dung.
Thiếu thông tin (tài khoản nào, link nào, tra ai) thì agent hỏi lại thay vì đoán.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt      # đã thêm streamlit>=1.40
streamlit run app.py                 # http://localhost:8501
```

UI ([`starter_v0/app.py`](../../starter_v0/app.py)) dùng chung vòng lặp tool và cách ghi transcript với `chat.py`.
Mỗi câu trả lời hiện kèm tool call và kết quả thô của tool; tool lỗi (ví dụ thiếu API key) được mở sẵn và tô đỏ, không bị giấu.
Mỗi phiên chat được ghi vào `starter_v0/transcripts/*.transcript.json` (`"source": "streamlit"`).

**Link dùng thử (deploy):**

Cloudflare Tunnel trỏ vào UI đang chạy local: `cloudflared tunnel --url http://localhost:8501`.
Link `trycloudflare.com` chỉ sống trong phiên chạy lệnh, nên được dán lại mỗi lần mở.

URL:

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin, hoặc xin xác nhận trước khi gửi | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X/Twitter (handle không có `@`) | không |
| social_search | Tìm tweet theo từ khóa, sắp xếp `Latest` hoặc `Top` | không |
| lookup | Tìm trên web (Tavily), `topic=news` cho tin tức, `timeframe` day/week/month/year | không |
| fetch | Đọc nội dung một URL cụ thể (Firecrawl) | không |
| format | Trình bày các item đã có thành bản tin markdown | không |
| send | Đăng văn bản lên Telegram channel của nhóm, chỉ khi `confirmed=true` | không |
| policy | Tìm trong company policy nội bộ | không |
| papers | Tìm paper trên arXiv | không |
| paper_text | Tải PDF arXiv và trích text | không |
| wiki | Tra Wikipedia (`vi`/`en`): định nghĩa, tiểu sử, lịch sử; không cần API key | **có** |

### A3. Câu hỏi mẫu để thử

1. Alan Turing là ai? (tool mới `wiki`)
2. Tin tức AI hôm nay có gì nổi bật? (`lookup` với tin hôm nay)
3. Mọi người đang bàn gì về Claude trên Twitter? (`social_search`)
4. Tóm tắt 5 tweet mới nhất giúp mình (thiếu tài khoản: agent phải hỏi lại)
5. Đăng bản tin AI hôm nay lên Telegram giúp mình (agent phải xin xác nhận trước khi gửi)

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline (`system_prompt.md` + `tools.yaml` của starter; model `anthropic/claude-haiku-5.5`) | Đo hành vi chưa tối ưu trước khi sửa | – | case 0.70 · routing 0.85 · args 0.70 · multiturn 0.8333 (14/20 PASS) | `starter_v0/runs/v0_B_base_openrouter_20261110T175934403647.json` |
| v1 | `system_prompt.md` | Prompt starter ra lệnh đoán account/URL và gửi ngay → agent không `clarify` (R10, R11) và gọi `send` khi chưa xác nhận (R12). Bỏ các chỉ dẫn đó, thêm rule phạm vi / thiếu info → `clarify` / xác nhận trước khi `send`. | case 0.70 · routing 0.85 · args 0.70 | case **0.80** · routing **1.00** · args 0.80 · multiturn 0.8333 (16/20). R10, R11 → PASS. R12 vẫn FAIL nhưng đổi bản chất: không còn gọi `send`, mà `clarify(response_type="text")` hỏi nội dung bản tin thay vì `yes_no` | `starter_v0/runs/v1_B_base_openrouter_20261110T180926543698.json` |
| v2 | `tools.yaml` (chỉ description của param `query` trong `lookup`, `social_search`) | Tool declaration không nói `query` nên chứa gì → model nhồi "tin tức… hôm nay" vào `query` dù đã có `topic`/`timeframe` (R03, R13, M02). Thêm convention: `query` chỉ là từ khóa chủ đề ngắn. | case 0.80 · args 0.80 · multiturn 0.8333 | case **0.95** · routing 1.00 · args **0.95** · multiturn **1.00** (19/20). R03, R13, M02 → PASS; còn R12 | `starter_v0/runs/v2_B_base_openrouter_20261110T181408218976.json` |
| v3 | `tools.yaml` (viết lại description mọi tool + convention args) | Description cũ không nói khi nào dùng / không dùng và không có boundary `send`/`clarify` → ở R12 agent hỏi nội dung (`text`) thay vì xin xác nhận (`yes_no`). Viết lại theo mẫu "làm gì · DÙNG khi · KHÔNG dùng khi", `send` chỉ khi `confirmed=true`, yêu cầu gửi/đăng → `clarify(yes_no)`. | case 0.95 · args 0.95 · multiturn 1.00 | case 0.95 · routing 1.00 · args 0.95 · multiturn 1.00 (19/20) — **không đổi**. Không regression ở 19 case còn lại. R12 vẫn `clarify(response_type="text")`: model ưu tiên hỏi nội dung vì "bản tin này" không tồn tại trong hội thoại → giả thuyết bị bác bỏ một phần: thiếu boundary trong declaration không phải nguyên nhân chính | `starter_v0/runs/v3_B_base_openrouter_20261110T182001695249.json` |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

Run v0: `starter_v0/runs/v0_B_base_openrouter_20261110T175934403647.json` — 6/20 FAIL, chia thành 2 nhóm nguyên nhân.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | `missing_info` | `timeline(screenname="sama", limit=5)` | Không rõ tài khoản nhưng agent tự chọn `sama` thay vì `clarify`. Nguyên nhân: prompt starter ra lệnh "pick a well-known account like Sam Altman". | v1 — bỏ chỉ dẫn đoán, thêm rule thiếu tài khoản → `clarify(response_type=text)` |
| R11_missing_url | `missing_info` | `fetch(url="https://www.example.com/article")` | Không có URL nhưng agent bịa URL. Nguyên nhân: prompt starter ra lệnh "assume a likely URL and read it". | v1 — thiếu URL → `clarify(response_type=text)`, cấm bịa URL |
| R12_confirm_before_send | `wrong_boundary` | `send(text="<UNKNOWN>", confirmed=false)` | Gọi `send` ngay, không xin xác nhận, nội dung còn rỗng. Nguyên nhân: prompt starter "just go ahead and do it". | v1 — gửi/đăng → `clarify(response_type=yes_no)` trước; `send(confirmed=true)` chỉ sau khi user đồng ý |
| R03_web_news_routing | eval gán `wrong_tool`, mismatch thực tế `wrong_arg_value` | `lookup(query="tin tức AI nổi bật hôm nay", topic="news", timeframe="day")` | Tool, `topic`, `timeframe` đều đúng; chỉ `query` bị nhồi thêm "tin tức… hôm nay" (đã thể hiện qua `topic`/`timeframe`). | Convention arg: `query` chỉ là từ khóa chủ đề ngắn |
| R13_parallel_web_and_tweets | eval gán `wrong_tool`, mismatch thực tế `wrong_arg_value` | `lookup(query="tin tức AI hôm nay", …)` + `social_search(query="AI")` | Gọi song song đúng 2 tool; `lookup.query` dài dòng như R03. | Như R03 |
| M02_carryover_timeframe | `wrong_arg_value` | `lookup(query="robotics news today", topic="news", timeframe="day")` | Carry-over `topic`/`timeframe` qua lượt đã đúng; `query` thêm "news today". | Như R03 |

Nhận xét: routing của model đã tốt ngay từ v0 (0.85); 3 lỗi đầu do **chỉ dẫn xấu cố ý trong system prompt**, 3 lỗi sau do **thiếu convention cho tham số `query`** trong tool declaration.

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Bốn run `--suite group` / `--suite cross` trên cùng 10 case, tất cả có `provider_error_cases == 0` và `measured_cases == total_cases == 10`:

| Run | Model | Prompt / tools | Kết quả | File |
|---|---|---|---|---|
| v0-wiki (group) | `anthropic/claude-haiku-5.5` | starter v0 + khai báo `wiki` | 10/10 | [`v0-wiki_B_group_openrouter_20261110T181343247036.json`](../../starter_v0/runs/v0-wiki_B_group_openrouter_20261110T181343247036.json) |
| v3-wiki (group) | `anthropic/claude-haiku-5.5` | v3 của nhóm + `wiki` (`v3-wiki+p8f5c6f233078+t1693ac83a810`) | 10/10 | [`v3-wiki_B_group_openrouter_20261110T185942635818.json`](../../starter_v0/runs/v3-wiki_B_group_openrouter_20261110T185942635818.json) |
| v0-wiki-nano (cross) | `openai/gpt-4.1-nano` | starter v0 + `wiki` | 6/10 | [`v0-wiki-nano_B_cross_openrouter_20261110T181423602495.json`](../../starter_v0/runs/v0-wiki-nano_B_cross_openrouter_20261110T181423602495.json) |
| v3-wiki-nano (cross) | `openai/gpt-4.1-nano` | v3 + `wiki` | 6/10 | [`v3-wiki-nano_B_cross_openrouter_20261110T185950067467.json`](../../starter_v0/runs/v3-wiki-nano_B_cross_openrouter_20261110T185950067467.json) |

Haiku 5.5 qua hết 10 case ngay cả với prompt starter cố ý xấu, nên một mình run Haiku không chứng minh được bộ case có bắt lỗi.
Vì vậy nhóm chạy thêm trên model yếu hơn (`gpt-4.1-nano`): ở v0, cả 4 case FAIL đều đúng loại lỗi case đó được viết để bắt.

| Case ID | Turn | What It Tests | Expected Tool/Behavior | Haiku v0 / v3 | nano v0 / v3 |
|---|---|---|---|---|---|
| G01_wiki_person_routing | single | Câu hỏi tiểu sử route tới tool mới `wiki`, query gọn | `wiki(query="Alan Turing")` | PASS / PASS | PASS / PASS |
| G02_wiki_english_lang_arg | single | Yêu cầu nguồn tiếng Anh phải truyền `lang=en` tường minh | `wiki(lang="en")` | PASS / PASS | PASS / PASS |
| G03_recent_event_not_wiki | single | Sự kiện mới trong tuần đi `lookup`, không đi `wiki` | `lookup(topic="news", timeframe="week")` | PASS / PASS | PASS / FAIL: `lookup(query="Anthropic")` thiếu `topic`, `timeframe` |
| G04_wiki_missing_subject | single | Biết tool nhưng thiếu đối tượng thì phải hỏi lại | `clarify(response_type="text")` | PASS / PASS | FAIL: `social_search(query="ông ấy")` / FAIL: `wiki(query="ông ấy")` |
| G05_parallel_wiki_and_news | single | Hai nhu cầu khác loại trong một câu, gọi song song | `wiki(query="Alan Turing")` + `lookup(topic="news", timeframe="day")` | PASS / PASS | FAIL: `lookup` thiếu `topic`, `timeframe` / FAIL: gọi `social_search` thay vì `lookup` |
| G06_wiki_clarify_then_fill_lang | multi | Tên ở lượt 3, ngôn ngữ ở lượt 4, giữ cả hai | `wiki(query="Marie Curie", lang="en")` | PASS / PASS | PASS / PASS |
| G07_send_after_explicit_confirmation | multi | User đã xác nhận nội dung thì gửi với `confirmed=true`, giữ nguyên văn bản | `send(text="RICONs demo lúc 19h", confirmed=true)` | PASS / PASS | FAIL: `send` thiếu `confirmed` / PASS |
| G08_correction_search_type_top | multi | User sửa "phổ biến nhất" thành `search_type=Top`, giữ query | `social_search(query="Claude", search_type="Top")` | PASS / PASS | PASS / PASS |
| G09_concept_wiki_not_papers | multi | Chỉ cần định nghĩa, từ chối paper → `wiki`, không `papers` | `wiki` | PASS / PASS | PASS / PASS |
| G10_research_before_post | multi | "Tra rồi đăng luôn": bước này chỉ tra, chưa được `send` | chỉ `wiki(query="Alan Turing")` | PASS / PASS | FAIL: gọi thêm `send` / FAIL: gọi thêm `send` (text là câu hỏi xác nhận) |

Nhận xét:

- Trên Haiku 5.5, thêm `wiki` vào v3 không gây regression: base `v3-wiki` 19/20, bằng v3 ([`v3-wiki_B_base_openrouter_20261110T190031395023.json`](../../starter_v0/runs/v3-wiki_B_base_openrouter_20261110T190031395023.json), dòng `v3-wiki` trong `version_log.csv`), case FAIL duy nhất vẫn là R12 như v3.
- Trên nano, v3 sửa được G07 (thêm `confirmed=true` sau khi user xác nhận, nhờ boundary `send` mới trong `tools.yaml`) nhưng G03 lại FAIL, nên tổng vẫn 6/10: bản v3 tối ưu trên Haiku không chuyển nguyên sang model yếu hơn.
- G10 FAIL ở cả hai version trên nano: không rule nào trong v3 nói "chưa có nội dung thì không gọi `send` cùng lượt với tool tra cứu". Lần gọi `send` này không gửi gì thật vì thiếu `confirmed=true`, tool trả `needs_confirmation`: guardrail trong code chặn được chỗ prompt chưa chặn.

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Chat live qua UI Streamlit, model `anthropic/claude-haiku-5.5`, 3 transcript.
Cả 3 có `artifact_version` `ui+p8f5c6f233078+t1693ac83a810`: nhãn là `ui` nhưng `prompt_hash` và `tools_hash` trùng đúng bản `v3-wiki` trong `version_log.csv`.

- T1 (yêu cầu thường, ngoài phạm vi, tool lỗi): [`ui_streamlit_openrouter_20261110T190837448475.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T190837448475.transcript.json)
- T2 (thiếu thông tin rồi bổ sung): [`ui_streamlit_openrouter_20261110T191950185955.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T191950185955.transcript.json)
- T3 (yêu cầu đăng Telegram, xác nhận rồi gửi thật): [`ui_streamlit_openrouter_20261110T193835828410.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T193835828410.transcript.json)

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| T1-1 | Viết giúp mình một hàm Python tính Fibonacci | không gọi tool | v3-wiki (hash như trên) | Từ chối vì ngoài phạm vi research, gợi ý việc agent làm được (tra Wikipedia, tìm paper). Đúng: không gọi tool cho yêu cầu ngoài phạm vi |
| T1-2 | Alan Turing là ai? Và hôm nay có tin gì mới về AI không? | `wiki(query="Alan Turing", lang="vi")` + `lookup(query="AI", topic="news", timeframe="day")`, cùng một round | v3-wiki | Yêu cầu research thường: gọi song song tool mới `wiki` (1 bài) và `lookup` (5 tin), trả lời 2 phần, mỗi phần kèm nguồn. `query` của `lookup` gọn ("AI") đúng convention v2 |
| T1-3 | Tóm tắt 5 tweet mới nhất giúp mình của Elon Musk nhé | `timeline(screenname="elonmusk", limit=5)` | v3-wiki | Map tên thành handle `elonmusk`, giữ `limit=5`; tóm tắt 5 tweet kèm link, tự ghi chú 3/5 là retweet và nội dung bị cắt nên chưa kiểm chứng |
| T1-4 | Tóm tắt bài này giúp mình: `https://www.anthropic.com/research` | `fetch(url="https://www.anthropic.com/research")` → `RuntimeError: Missing FIRECRAWL_API_KEY` | v3-wiki | Tool lỗi: UI hiện lỗi đỏ và JSON thô; agent nói thẳng là không đọc được trang, không bịa nội dung, đề xuất 3 cách khác |
| T1-5 | What is the most popular paper since chatGPT blown up? | `papers(query="large language models", max_results=5, sort_by="relevance")` | v3-wiki | Trả lời bằng tiếng Anh theo user; nói rõ kết quả xếp theo độ liên quan, không theo độ phổ biến/citation, nên không trả lời được câu hỏi "phổ biến nhất". Giới hạn: tool `papers` không có tiêu chí citation |
| T2-1 | Tóm tắt 5 tweet mới nhất giúp mình | `clarify(response_type="text")`: "Bạn muốn tóm tắt 5 tweet mới nhất của tài khoản nào? Cho mình handle X (không cần @)..." | v3-wiki | Thiếu tài khoản: hỏi lại thay vì đoán (prompt starter v0 từng đoán `sama`, xem R10 ở B2) |
| T2-2 | karpathy | `timeline(screenname="karpathy", limit=5)` | v3-wiki | Bổ sung ở lượt sau: dùng handle user đưa và giữ `limit=5` từ lượt 1; tóm tắt 5 tweet kèm link và số tương tác |
| T3-1 | Đăng bản tin AI hôm nay lên Telegram giúp mình | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` → `format(template="daily_ai_vn")` → `clarify(response_type="yes_no")` | v3-wiki | Chưa gửi gì: tra tin, soạn bản tin, rồi xin xác nhận yes/no kèm nội dung sẽ gửi |
| T3-2 | Có | không gọi tool | v3-wiki | Chưa gửi: agent báo 3 chi tiết trong bản tin chưa kiểm chứng được và hỏi user chọn gửi bản chỉ có tiêu đề + link hay bản đầy đủ. Nguyên nhân: lịch sử hội thoại chỉ giữ tiêu đề + link của kết quả `lookup`, không giữ nội dung nguồn (xem mục 5) |
| T3-3 | 2 (gửi bản đầy đủ) | `send(text=<bản tin đã hiển thị>, confirmed=true)` → `{"status": "sent"}` | v3-wiki | Gửi thật lên private channel của nhóm sau khi user xác nhận; bản tin xuất hiện trong channel kèm link nguồn |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `wiki` | [`starter_v0/tools/wiki/`](../../starter_v0/tools/wiki/) (`tool.py`, `TOOL.md`), đăng ký trong [`tools/__init__.py`](../../starter_v0/tools/__init__.py) và cuối [`artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) | Một request MediaWiki (search + intro), không cần API key; `items` cùng dạng với `lookup` nên đưa thẳng vào `format` được; model route đúng tới `wiki` ở G01, G05, G06, G09, G10 | Input xấu (`query` rỗng, `lang` ngoài `vi`/`en`) trả error dict, không gọi mạng; `max_results` kẹp 1-5; tool chỉ đọc, không side effect |
| Unit test tool mới (≥ 3 test/tool) | [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py), 7 test `test_wiki_*`; `pytest`: 74 passed, 0 failed, 14 skipped (stub tool có sẵn) | Happy path (request + mapping), input xấu (query rỗng, lang ngoài enum, số dạng chuỗi), nhánh lỗi (HTTP 429, timeout) | Test chạy offline qua `fake_http`; mỗi test assert cả request gửi đi lẫn kết quả trả về |
| UI (lệnh chạy + link dùng thử) | [`starter_v0/app.py`](../../starter_v0/app.py), `streamlit run app.py`, link ở mục A1 | Dùng chung `run_model_tool_loop` và `write_transcript` của `chat.py`; chat trên UI được ghi transcript cùng format; nút câu hỏi mẫu ở sidebar | Tool call và kết quả thô hiện dưới mỗi câu trả lời, lỗi tool được tô đỏ (không che lỗi); giới hạn 20 lượt mỗi phiên vì link public dùng key của nhóm |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

7 test cho `wiki`.
Ví dụ lỗi chỉ unit test bắt được: API Wikipedia trả các trang không theo thứ tự xếp hạng (thứ hạng nằm ở field `index`).
Nếu tool quên sắp xếp, model vẫn gọi đúng `wiki(query="Alan Turing")` nên eval vẫn PASS, nhưng user có thể nhận bài kém liên quan nhất lên đầu.
Test `test_wiki_sends_one_search_request_and_maps_pages_by_rank` cố ý đưa các trang theo thứ tự ngược để bắt lỗi này.

### B5. Bonus Evidence

Chỉ điền nếu nhóm làm bonus (ghi riêng, tối đa 10 điểm). Tool có sẵn (`send`, `policy`, `papers`, `paper_text`) không tự được bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Small Local Model | xem B7 |  |  |
| Hơn 3 tool mới (≥ 4) |  |  |  |
| `send` gửi thật lên Telegram sau xác nhận | T3 ở B4: [`ui_streamlit_openrouter_20261110T193835828410.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T193835828410.transcript.json) | Luồng đầy đủ: agent soạn bản tin rồi `clarify(yes_no)` → user xác nhận → `send(confirmed=true)` → `status: sent` trên private channel của nhóm | Tool `send` tự chặn khi `confirmed` khác `true` (trả `needs_confirmation`, không gọi mạng); token và chat id chỉ nằm trong `.env`, không có trong transcript |
| Test challenge (0 skipped / regression test) | `pytest` output |  |  |

Test challenge: số bug tìm được trong tool có sẵn (nếu có), cách sửa, và test regression tương ứng.

### B7. Small Local Model Challenge (bonus)

Chỉ điền nếu nhóm làm bonus này.

| Version | Model (provider) | Prompt/Tools | case_accuracy | tool_routing | argument | multiturn | Run File |
|---|---|---|---|---|---|---|---|
| v3 | (cloud) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v3-<model> | (ollama) | v3 |  |  |  |  |  |
| v4-local |  |  |  |  |  |  |  |
| v5-local |  |  |  |  |  |  |  |

Lỗi đặc thù của model nhỏ (đếm từ run JSON):

| Failure Pattern | Count | Example Case | Fix Tried | Helped? |
|---|---|---|---|---|
| wrong / hallucinated tool |  |  |  |  |
| invalid JSON args (`_invalid_json_arguments`) |  |  |  |  |
| no tool call / answered directly |  |  |  |  |
| missed `clarify` |  |  |  |  |
| repeated / unnecessary calls |  |  |  |  |

- Cái gì giúp model nhỏ gọi tool đúng hơn nhất? Bằng chứng?
- Bản prompt tối ưu cho local chạy trên model cloud thì sao?
- Khi nào nhóm sẽ chọn model local thay vì cloud cho agent này?

## 5. Khó khăn và cách xử lý

> Khó khăn chính và cách nhóm xử lý. Nếu gặp lỗi kỹ thuật (provider lỗi, hết quota API, tool không chạy), mô tả lỗi và dẫn bằng chứng: run JSON, log, ảnh chụp.

- **Agent không bao giờ gửi được Telegram dù user đã xác nhận (lỗi ngữ cảnh nhiều lượt).**
  `chat.py` của starter chỉ lưu vào lịch sử text cuối của user và assistant, bỏ hết tool call và kết quả tool.
  Ở lượt sau, model thấy một bản tin "do chính nó viết" nhưng không thấy lần `lookup` nào, nên kết luận bản tin không có nguồn, không gửi, và tra lại từ đầu; mỗi lần user nói "có" lại lặp lại vòng đó.
  Bằng chứng: [`ui_streamlit_openrouter_20261110T192055287079.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T192055287079.transcript.json), 4 lượt, user xác nhận 3 lần, không lượt nào gọi `send`.
  Cách xử lý: UI ([`starter_v0/app.py`](../../starter_v0/app.py), hàm `assistant_history_entry`) lưu kèm mỗi lượt assistant một khối `TOOL_EVIDENCE` gọn: tool đã gọi, args, tiêu đề + link của kết quả, bản markdown của `format`, hoặc lỗi.
  `chat.py` không nằm trong danh sách file được sửa nên giữ nguyên; lỗi vẫn còn khi chat bằng CLI.
- **Bản sửa đầu nén quá tay.**
  Khối evidence ban đầu chỉ giữ tiêu đề + link, nên model thấy các chi tiết trong bản tin ("hơn 300 triệu người", Goldman Sachs, AMD) mà không thấy nguồn nào chứa chúng, và dừng lại hỏi user (T3-2 ở B4), dù cả 3 chi tiết đều có trong nội dung kết quả `lookup`.
  Đã thêm nội dung nguồn của mỗi kết quả (tối đa 1000 ký tự/kết quả) vào evidence; chạy lại kịch bản "đăng bản tin" → "Có" thì agent gọi thẳng `send(confirmed=true)`.
- **`prompt_hash` lệch dù prompt không đổi.**
  `versioning.py` hash byte thô của file; trên Windows với `core.autocrlf=true`, git checkout `system_prompt.md` và `tools.yaml` thành CRLF nên hash khác bản LF của người khác trong nhóm, khiến run `v3-wiki` đầu tiên trông như đổi cả prompt lẫn tools.
  Đã thêm [`.gitattributes`](../../.gitattributes) giữ `starter_v0/artifacts/*.md|*.yaml` ở LF trên mọi máy, xóa các run có hash sai và chạy lại; `v3-wiki` giờ có `prompt_hash` trùng v3 (`8f5c6f233078`), chỉ `tools_hash` đổi do thêm `wiki`.
- **Thiếu key Firecrawl.** Nhóm chưa có `FIRECRAWL_API_KEY` nên `fetch` trả lỗi; UI hiện lỗi này thay vì che (T1-4 ở B4).

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
