# Báo cáo cá nhân — Hoàng Thế Duyệt - 2A202603980 (Người A — nhóm RICONs)

## 1. Thông tin thành viên

- Họ tên: Hoàng Thế Duyệt
- MSSV: 2A202603980
- Email:
- GitHub: HoangDuyet2005
- Vai trò: Nhóm trưởng — Setup, baseline v0, tối ưu prompt/tool declaration v1–v3, failure analysis

## 2. Phần việc phụ trách

| Mốc | Việc | File / sản phẩm | Rubric |
| --- | ---- | --------------- | ------ |
| Đầu giờ | Tạo repo nhóm, thêm collaborator, điền `TEAM.md`, setup `.venv` + `.env`, preflight + `pytest` | `TEAM.md`, `starter_v0/requirements.txt` | — |
| CP1 | Baseline **v0** chưa sửa artifact; gán loại lỗi cho từng case FAIL | `starter_v0/runs/v0_…json`, `version_log.csv`, bảng B2 | C1 |
| CP2 | **v1** — sửa `system_prompt.md` | `starter_v0/artifacts/system_prompt.md` | C2, C3 |
| CP2 | **v2** — convention cho param `query` trong `tools.yaml` | `starter_v0/artifacts/tools.yaml` | C2, C3 |
| CP2 | **v3** — viết lại description mọi tool (khi nào dùng / không dùng), boundary `send`, convention args | `starter_v0/artifacts/tools.yaml` | C2, C3 |
| Trước deadline | Bảng B1, B2, B6 trong `group_report.md`; checklist `SUBMISSION.md`; commit chốt | `report/team/group_report.md` | C7 |

## 3. Đóng góp cụ thể

Model dùng cho mọi run: `anthropic/claude-haiku-5.5` qua OpenRouter (nhóm chọn chung). Bộ eval: `data/eval_base.json` (20 case: 14 single turn + 6 multi turn).

| Version | Thay đổi | Giả thuyết | Metric trước → sau (case_accuracy) | Run file |
| ------- | -------- | ---------- | ------------------ | -------- |
| v0 | Baseline, không sửa | — | — → 0.70 (routing 0.85, args 0.70, multiturn 0.8333) | `starter_v0/runs/v0_B_base_openrouter_20261110T175934403647.json` |
| v1 | `system_prompt.md`: bỏ các chỉ dẫn "đoán account / đoán URL / gửi ngay / ép một bước"; thêm rule phạm vi, thiếu info → `clarify`, xác nhận trước khi `send`, gọi song song khi yêu cầu có nhiều phần | Prompt starter ra lệnh đoán và gửi ngay nên agent không `clarify` (R10, R11) và gọi `send` khi chưa xác nhận (R12) | 0.70 → 0.80 (routing 0.85 → 1.00) | `starter_v0/runs/v1_B_base_openrouter_20261110T180926543698.json` |
| v2 | `tools.yaml`: description param `query` của `lookup` và `social_search` — chỉ là từ khóa chủ đề ngắn, không thêm từ chỉ loại nội dung/thời gian | Declaration không nói `query` nên chứa gì nên model nhồi "tin tức… hôm nay" vào `query` dù đã có `topic`/`timeframe` (R03, R13, M02) | 0.80 → 0.95 (multiturn 0.8333 → 1.00) | `starter_v0/runs/v2_B_base_openrouter_20261110T181408218976.json` |
| v3 | `tools.yaml`: viết lại description mọi tool theo mẫu "làm gì · DÙNG khi · KHÔNG dùng khi"; `send` chỉ khi `confirmed=true`; `clarify` dùng `yes_no` cho yêu cầu gửi/đăng; convention `screenname`, `limit`, `topic`, `timeframe`, `search_type` | Thiếu boundary `send`/`clarify` trong declaration là lý do R12 hỏi `text` thay vì `yes_no` | 0.95 → 0.95 (không đổi, không regression) | `starter_v0/runs/v3_B_base_openrouter_20261110T182001695249.json` |

Nhận xét chính từ failure analysis:

- Với model này, **routing đã tốt ngay từ v0 (0.85)**. Lỗi tập trung ở 2 nhóm: (1) chỉ dẫn xấu cố ý trong system prompt (R10, R11, R12) và (2) thiếu convention cho tham số `query` (R03, R13, M02).
- Hai nhóm lỗi được sửa ở hai nơi khác nhau: lỗi **hành vi** (hỏi lại, xác nhận, phạm vi) sửa trong `system_prompt.md` (v1); lỗi **giá trị tham số** sửa trong description của param trong `tools.yaml` (v2). Một dòng description cho `query` đã sửa được cả 3 case, kể cả case multi turn M02.
- R03 và R13 được eval gán nhãn `wrong_tool` nhưng `observed_mismatch` thực tế là `wrong_arg_value` (tool đúng, chỉ `query` sai) — phải đọc `failures` + `actual_tool_calls` mới thấy, không thể chỉ nhìn nhãn.
- R12 không sửa được qua v1 (prompt) và v3 (declaration): agent đã ngừng gọi `send` bừa (v0 gọi `send(text="<UNKNOWN>")`), nhưng vì "bản tin này" không tồn tại trong hội thoại nên luôn hỏi nội dung (`clarify(text)`) thay vì xin xác nhận (`yes_no`). Hành vi này an toàn và có thể hợp lý hơn đáp án — là case cần review thủ công.

## 4. Bằng chứng

- File/commit (nhánh `main`):
  - `2e1a51b` — fix: pin `pytest<9` (pytest 9.2.0 lỗi INTERNALERROR trên Python 3.10)
  - `3b0e51d` — v0: baseline run + failure analysis B2
  - `1e32f57` — v1: system prompt (0.70 → 0.80)
  - `bf38c61` — v2: query convention (0.80 → 0.95)
  - `e63ad79` — v3: rewrite tool descriptions + send boundary + arg conventions
- Run JSON (`provider_error_cases == 0`, `measured_cases == total_cases == 20`): 4 file `starter_v0/runs/v0…v3_B_base_openrouter_*.json` ở bảng trên; mỗi version có `prompt_hash`/`tools_hash` khác version trước (ghi trong `starter_v0/artifacts/version_log.csv`).
- `pytest tests/test_tool_contract.py`: 55 passed sau mỗi lần sửa `tools.yaml`.
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: dùng trợ lý AI (Claude Code) để đọc code eval, gợi ý nội dung prompt/description và tóm tắt run JSON. Tự kiểm tra bằng cách: chạy lại eval thật sau mỗi thay đổi và chỉ ghi metric lấy từ `summary` của run JSON; đọc `actual_tool_calls` của từng case FAIL để xác nhận nguyên nhân; chạy `pytest tests/test_tool_contract.py` sau mỗi lần sửa `tools.yaml`; kiểm tra run JSON không chứa API key trước khi commit.

## 5. Tự đánh giá

- Điều làm tốt: mỗi version chỉ một giả thuyết và có run hợp lệ đi kèm; đọc kỹ `failures` nên phát hiện R03/R13 bị gán nhãn `wrong_tool` nhưng thực chất là lỗi tham số; ghi trung thực v3 không tăng điểm.
- Điều chưa làm được / sẽ làm khác: chưa sửa được R12; v3 gộp nhiều thay đổi trong `tools.yaml` (description + convention args) nên khó tách tác động của từng phần — nếu làm lại sẽ tách thành 2 version.
- Điều học được về vòng lặp evidence-driven: nhãn lỗi tự động chỉ là điểm bắt đầu, phải đọc tool call thực tế mới đặt đúng giả thuyết; cùng một ý (vd. "phải xin xác nhận") đặt ở prompt hay ở tool declaration có thể cho kết quả như nhau, và có hành vi model ưu tiên mạnh đến mức cả hai chỗ đều không đổi được.
