# Báo cáo cá nhân - LuuNguyenChiDuc-2A202603923 (Người B, nhóm RICONs)

## 1. Thông tin thành viên

- Họ tên: Lưu Nguyễn Chí Đức
- MSSV: 2A202603923
- GitHub: [TheDLCrimson](https://github.com/TheDLCrimson)
- Vai trò: Tool mới + unit test, eval nhóm, UI + live chat

## 2. Phần việc phụ trách

| Mốc | Việc | File / sản phẩm | Rubric |
| --- | ---- | --------------- | ------ |
| Đầu giờ | Clone fork, setup `.venv` + `.env`, preflight + `pytest` | — | — |
| 15:00 → 15:30 | Viết tool mới: `TOOL.md` (frontmatter đúng contract), `tool.py` trả error dict thay vì raise; đăng ký trong `tools/__init__.py`; gửi khai báo YAML cho A merge vào cuối `tools.yaml` | `starter_v0/tools/<tên>/` | C4 |
| 15:30 | ≥ 3 unit test cho tool mới (happy path, input xấu, nhánh lỗi), offline, `pytest` 0 failed | `starter_v0/tests/test_tools_todo.py`, bảng B5a | C4 |
| 16:00 | 10 case eval nhóm: 5 single turn + 5 multi turn, mỗi case có `failure_type`, `expect`, `metadata.what_it_tests`, ≥ 1 case route tới tool mới; chạy `--suite group` | `starter_v0/data/eval_group.json`, bảng B3 | C5 |
| Trước 16:30 | UI Streamlit + dependency trong `requirements.txt`; link dùng thử qua Cloudflare Tunnel; **Phần A** của báo cáo nhóm | `starter_v0/app.py`, `group_report.md` A1–A3 | C6, C7 |
| Sau v3 | Chạy lại `--suite group` với v3; `chat.py` ≥ 3 lượt live (yêu cầu thường / thiếu info rồi bổ sung / đăng Telegram) | `starter_v0/transcripts/*.transcript.json`, bảng B4 | C5, C6 |

## 3. Đóng góp cụ thể

_(Điền sau khi làm, dựa trên output thật — không điền trước.)_

- Tool mới: tên, làm gì, vì sao chọn:
- Unit test (tên test → hành vi kiểm tra):
  -
  -
  -
- Eval case nhóm đáng chú ý (case nào bắt được lỗi gì):
- UI: lệnh chạy, link dùng thử:
- Live chat: quan sát chính từ transcript:

## 4. Bằng chứng

- File/commit/PR:
- Output `pytest`:
- Run group JSON (`provider_error_cases == 0`, `measured_cases == total_cases`):
- Transcript:
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

- Điều làm tốt:
- Điều chưa làm được / sẽ làm khác:
- Khác biệt giữa unit test (đo code tool) và eval (đo lựa chọn của model) mà mình rút ra:
