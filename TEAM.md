# Team

## Thông tin nhóm

- Tên nhóm: RICONs
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-RICONs-ResearchAgentToolEval`
- URL repo: https://github.com/HoangDuyet2005/K5-L3B-DAY03-RICONs-ResearchAgentToolEval
- Nhánh nộp: `main`
- Commit chốt: _(điền SHA commit cuối trước deadline)_

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Hoàng Thế Duyệt | 2A202603980 | | HoangDuyet2005 | Nhóm trưởng — Setup, baseline v0, tối ưu prompt/tool declaration v1–v3, failure analysis |
|   2 | Lưu Nguyễn Chí Đức | 2A202603923 | | TheDLCrimson | Tool mới + unit test, 10 eval case nhóm, UI Streamlit + live chat, Phần A báo cáo |

## Nguyên tắc phối hợp

- Mỗi người sở hữu một nhóm file riêng để tránh conflict và để lịch sử commit thể hiện rõ đóng góp cá nhân.
- Mỗi người commit bằng tài khoản GitHub của chính mình. Làm trên nhánh riêng (`a/prompt-tuning`, `b/new-tool-ui`) rồi mở PR vào `main`; nếu commit thẳng `main` thì `git pull` trước mỗi lần push.
- `starter_v0/artifacts/tools.yaml` là file chung: Người A sửa description/convention args; Người B chỉ thêm khai báo tool mới ở **cuối file**, sau khi A đã push version gần nhất.
- Thêm tool mới vào `tools.yaml` làm đổi `tools_hash` → chạy lại base eval và ghi **một dòng riêng** trong `version_log.csv` (ví dụ `v1-newtool`), không gộp vào v2/v3, để mỗi version vẫn chỉ có một giả thuyết.
- Không commit `.env`, API key, token Telegram. Mỗi người tự dùng key của mình.

## Phân công theo checkpoint

| Mốc | Người A | Người B |
| --- | ------- | ------- |
| Đầu giờ | Thêm B làm collaborator; điền `TEAM.md`; setup `.venv` + `.env`; preflight + `pytest` | Clone fork; setup `.venv` + `.env`; preflight + `pytest` |
| 15:00 — CP1 | Chạy baseline **v0** (chưa sửa artifact), ghi `version_log.csv`, gán loại lỗi cho case FAIL (bảng B2) | Chọn ý tưởng tool mới, viết `TOOL.md` + khung `tool.py` |
| 15:30 — CP2/CP3 | **v1**: sửa `system_prompt.md` (bỏ chỉ dẫn xấu, hỏi lại khi thiếu info, xác nhận trước khi gửi, từ chối out-of-scope) | Hoàn thiện tool mới, đăng ký `tools/__init__.py`, ≥ 3 test trong `tests/test_tools_todo.py`, `pytest` xanh (bảng B5a) |
| 16:00 — CP2/CP4 | **v2**: viết lại description trong `tools.yaml` (khi nào dùng / không dùng); merge khai báo tool mới + run `v1-newtool` | Viết 10 case `data/eval_group.json` (5 single + 5 multi, ≥ 1 route tới tool mới), chạy `--suite group` (bảng B3) |
| 16:30 — Showdown | Hỗ trợ demo, ghi nhận lỗi team khác tìm ra | UI Streamlit `app.py` + `requirements.txt`, link Cloudflare Tunnel; **Phần A** của `group_report.md` |
| 17:30 — CP2 | **v3**: convention args (handle, `topic=news`, `timeframe`, `search_type=Top`, giữ `limit` qua lượt) | Chạy lại `--suite group` với v3; `chat.py` ≥ 3 lượt live (bảng B4) |
| Trước 23:59 | Bảng B1, B2, B6 trong `group_report.md`; báo cáo cá nhân | Bảng B3, B4, B5a; báo cáo cá nhân |
| Chung | Mục 5 (Khó khăn), mục 6 (Đóng góp), kiểm tra checklist `SUBMISSION.md`, ghi commit chốt | |

Bonus (chỉ làm khi phần bắt buộc đã xong): Người A — test challenge (điền hết stub skip) hoặc Small Local Model; Người B — gửi Telegram thật sau xác nhận hoặc thêm tool cho đủ ≥ 4 tool tự viết.

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/` theo dạng `MSSV_HoTen.md`:

- Người A: [`report/team/2A202603980_HoangTheDuyet.md`](report/team/2A202603980_HoangTheDuyet.md)
- Người B: [`report/team/2A202603923_LuuNguyenChiDuc.md`](report/team/2A202603923_LuuNguyenChiDuc.md)

## Người A — HoangTheDuyet-2A202603980

### Phần việc phụ trách

- Setup môi trường, repo nhóm, preflight provider.
- Baseline v0 và failure analysis (C1).
- Tối ưu `system_prompt.md` và `tools.yaml` qua v1, v2, v3; ghi `version_log.csv` (C2, C3).
- Báo cáo nhóm mục B1, B2, B6.

### Đóng góp cụ thể

- v0 (baseline, `anthropic/claude-haiku-5.5`): case_accuracy 0.70; phân tích 6 case FAIL thành 2 nhóm (chỉ dẫn xấu trong prompt; `query` dài dòng) — bảng B2.
- v1 (`system_prompt.md`): bỏ chỉ dẫn đoán/gửi ngay, thêm rule phạm vi / `clarify` / xác nhận trước `send` → 0.70 → 0.80, routing 0.85 → 1.00.
- v2 (`tools.yaml`, param `query`): `query` chỉ là từ khóa chủ đề ngắn → 0.80 → 0.95, multiturn 0.8333 → 1.00.
- v3 (`tools.yaml`): viết lại description mọi tool (khi nào dùng / không dùng), boundary `send`, convention args → 0.95 → 0.95, không regression; R12 vẫn FAIL (phân tích ở B1/B6).
- Sửa lỗi môi trường: pin `pytest<9` vì pytest 9.2.0 lỗi INTERNALERROR trên Python 3.10.

### Bằng chứng

- Commit trên `main`: `2e1a51b` (pytest), `3b0e51d` (v0), `1e32f57` (v1), `bf38c61` (v2), `e63ad79` (v3).
- Run: `starter_v0/runs/v{0,1,2,3}_B_base_openrouter_*.json`; 4 dòng v0–v3 trong `starter_v0/artifacts/version_log.csv`.

## Người B - LuuNguyenChiDuc-2A202603923

### Phần việc phụ trách

- Tool mới `starter_v0/tools/<tên>/` + unit test (C4).
- 10 eval case nhóm trong `starter_v0/data/eval_group.json` + run `--suite group` (C5).
- UI Streamlit, link dùng thử, live chat transcript (C6).
- Báo cáo nhóm Phần A và mục B3, B4, B5a.

### Đóng góp cụ thể

- _(điền sau khi làm: tool gì, test gì, case nào bắt được lỗi gì)_

### Bằng chứng

- _(link commit/PR, output `pytest`, run group, `starter_v0/transcripts/<file>.transcript.json`)_
