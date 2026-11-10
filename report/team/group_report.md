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
| v0 | baseline (`system_prompt.md` + `tools.yaml` của starter; model `anthropic/claude-haiku-5.5`) | Đo hành vi chưa tối ưu trước khi sửa | – | case 0.70 · routing 0.85 · args 0.70 · multiturn 0.8333 (14/20 PASS) | `starter_v0/runs/v0_B_base_openrouter_20261110T175934403647.json` |
| v1 | `system_prompt.md` | Prompt starter ra lệnh đoán account/URL và gửi ngay → agent không `clarify` (R10, R11) và gọi `send` khi chưa xác nhận (R12). Bỏ các chỉ dẫn đó, thêm rule phạm vi / thiếu info → `clarify` / xác nhận trước khi `send`. | case 0.70 · routing 0.85 · args 0.70 | case **0.80** · routing **1.00** · args 0.80 · multiturn 0.8333 (16/20). R10, R11 → PASS. R12 vẫn FAIL nhưng đổi bản chất: không còn gọi `send`, mà `clarify(response_type="text")` hỏi nội dung bản tin thay vì `yes_no` | `starter_v0/runs/v1_B_base_openrouter_20261110T180926543698.json` |
| v2 | `tools.yaml` (chỉ description của param `query` trong `lookup`, `social_search`) | Tool declaration không nói `query` nên chứa gì → model nhồi "tin tức… hôm nay" vào `query` dù đã có `topic`/`timeframe` (R03, R13, M02). Thêm convention: `query` chỉ là từ khóa chủ đề ngắn. | case 0.80 · args 0.80 · multiturn 0.8333 | case **0.95** · routing 1.00 · args **0.95** · multiturn **1.00** (19/20). R03, R13, M02 → PASS; còn R12 | `starter_v0/runs/v2_B_base_openrouter_20261110T181408218976.json` |
| v3 |  |  |  |  |  |

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

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
|  |  |  |  |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới (`tools/<tên>/`) |  |  |  |
| Unit test tool mới (≥ 3 test/tool) | `pytest` output (0 failed) |  |  |
| UI (lệnh chạy + link dùng thử) |  |  |  |

Tool unit tests: số test đã viết, và một ví dụ lỗi mà unit test bắt được nhưng eval không bắt được.

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
