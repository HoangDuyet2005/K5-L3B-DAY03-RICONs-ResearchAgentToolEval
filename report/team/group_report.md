# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3:

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì (cho team khác hiểu nhanh).

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, và gửi lên Telegram khi được xác nhận."

**Cách chạy UI:**

> Lệnh chạy UI (ví dụ `streamlit run app.py`) và dependency đã thêm vào `starter_v0/requirements.txt`.

**Link dùng thử (deploy):**

> Dán link public để team khác mở thử ngay. Cách deploy nhanh bằng Cloudflare Tunnel xem README. Nếu deploy Vercel/Streamlit Cloud thì dán link đó.
>
> URL:

### A2. Tool agent có

> Liệt kê các tool agent đang dùng (gồm tool mới nhóm tự thêm). Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

### A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## 3. Giải pháp

> Tóm tắt các thay đổi chính trong `starter_v0/artifacts/system_prompt.md` và `starter_v0/artifacts/tools.yaml`, và tool mới nhóm viết (tên, làm gì, khi nào agent nên gọi).

-

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Lấy từ `starter_v0/artifacts/version_log.csv` và `starter_v0/runs/*.json`. Chỉ dùng run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline |  |  |  |  |
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |
| v3 |  |  |  |  |  |

### B2. Failure Analysis

Lấy từ `results[*].result.failures` trong run JSON.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
|  |  |  |  |  |

### B3. Team Eval Cases

Liệt kê đúng 10 case trong `starter_v0/data/eval_group.json` (5 single turn + 5 multi turn).

Run `--suite group` (Haiku 5.5, prompt/tools v0 + khai báo `wiki`): [`v0-wiki_B_group_openrouter_20261110T181343247036.json`](../../starter_v0/runs/v0-wiki_B_group_openrouter_20261110T181343247036.json), 10/10 PASS, `provider_error_cases == 0`, `measured_cases == total_cases == 10`.
Vì Haiku 5.5 qua hết cả với prompt starter cố ý xấu, nhóm chạy thêm cùng bộ case trên model yếu hơn (`openai/gpt-4.1-nano`, `--suite cross`) để kiểm tra bộ case có bắt được lỗi không: [`v0-wiki-nano_B_cross_openrouter_20261110T181423602495.json`](../../starter_v0/runs/v0-wiki-nano_B_cross_openrouter_20261110T181423602495.json), 6/10, và cả 4 case FAIL đều đúng loại lỗi case đó được viết để bắt.

| Case ID | Turn | What It Tests | Expected Tool/Behavior | Result (Haiku v0+wiki / nano) |
|---|---|---|---|---|
| G01_wiki_person_routing | single | Câu hỏi tiểu sử route tới tool mới `wiki`, query gọn | `wiki(query="Alan Turing")` | PASS / PASS |
| G02_wiki_english_lang_arg | single | Yêu cầu nguồn tiếng Anh phải truyền `lang=en` tường minh | `wiki(lang="en")` | PASS / PASS |
| G03_recent_event_not_wiki | single | Sự kiện mới trong tuần đi `lookup`, không đi `wiki` | `lookup(topic="news", timeframe="week")` | PASS / PASS |
| G04_wiki_missing_subject | single | Biết tool nhưng thiếu đối tượng thì phải hỏi lại | `clarify(response_type="text")` | PASS / FAIL: gọi `social_search(query="ông ấy")` |
| G05_parallel_wiki_and_news | single | Hai nhu cầu khác loại trong một câu, gọi song song | `wiki(query="Alan Turing")` + `lookup(topic="news", timeframe="day")` | PASS / FAIL: `lookup` thiếu `topic`, `timeframe` |
| G06_wiki_clarify_then_fill_lang | multi | Tên ở lượt 3, ngôn ngữ ở lượt 4, giữ cả hai | `wiki(query="Marie Curie", lang="en")` | PASS / PASS |
| G07_send_after_explicit_confirmation | multi | User đã xác nhận nội dung thì gửi với `confirmed=true`, giữ nguyên văn bản | `send(text="RICONs demo lúc 19h", confirmed=true)` | PASS / FAIL: `send` thiếu `confirmed` |
| G08_correction_search_type_top | multi | User sửa "phổ biến nhất" thành `search_type=Top`, giữ query | `social_search(query="Claude", search_type="Top")` | PASS / PASS |
| G09_concept_wiki_not_papers | multi | Chỉ cần định nghĩa, từ chối paper → `wiki`, không `papers` | `wiki` | PASS / PASS |
| G10_research_before_post | multi | "Tra rồi đăng luôn": bước này chỉ tra, chưa được `send` | chỉ `wiki(query="Alan Turing")` | PASS / FAIL: gọi thêm `send` khi chưa có nội dung |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `wiki` | [`starter_v0/tools/wiki/`](../../starter_v0/tools/wiki/) (`tool.py`, `TOOL.md`), đăng ký trong [`tools/__init__.py`](../../starter_v0/tools/__init__.py) và cuối [`artifacts/tools.yaml`](../../starter_v0/artifacts/tools.yaml) | Một request MediaWiki (search + intro), không cần API key; `items` cùng dạng với `lookup` nên đưa thẳng vào `format` được; model route đúng tới `wiki` ở G01, G05, G06, G09, G10 | Input xấu (`query` rỗng, `lang` ngoài `vi`/`en`) trả error dict, không gọi mạng; `max_results` kẹp 1-5; tool chỉ đọc, không side effect |
| Unit test tool mới (≥ 3 test/tool) | [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py), 7 test `test_wiki_*`; `pytest`: 74 passed, 0 failed, 14 skipped (stub tool có sẵn) | Happy path (request + mapping), input xấu (query rỗng, lang ngoài enum, số dạng chuỗi), nhánh lỗi (HTTP 429, timeout) | Test chạy offline qua `fake_http`; mỗi test assert cả request gửi đi lẫn kết quả trả về |
| UI (lệnh chạy + link dùng thử) |  |  |  |

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
| `send` gửi thật lên Telegram sau xác nhận | transcript |  |  |
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

-

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- Fix nào thuộc `system_prompt.md`?
- Fix nào thuộc `tools.yaml`?
- Failure nào cần review thủ công thay vì chấm tự động?
- Nếu có thêm một vòng, nhóm sẽ thử giả thuyết nào?

## 8. Tài liệu tham khảo

-
