# Báo cáo cá nhân — HoVaTen-MSSV (Người A — nhóm RICONs)

> Đổi tên file thành `<MSSV>_<HoTen>.md` (ví dụ `20241234_NguyenVanAn.md`) và thay tiêu đề trước khi nộp.

## 1. Thông tin thành viên

- Họ tên:
- MSSV:
- Email:
- GitHub: HoangDuyet2005
- Vai trò: Nhóm trưởng — Setup, baseline v0, tối ưu prompt/tool declaration v1–v3

## 2. Phần việc phụ trách

| Mốc | Việc | File / sản phẩm | Rubric |
| --- | ---- | --------------- | ------ |
| Đầu giờ | Tạo repo nhóm, thêm collaborator, điền `TEAM.md`, setup `.venv` + `.env`, preflight + `pytest` | `TEAM.md` | — |
| 15:00 | Baseline **v0** chưa sửa artifact; gán loại lỗi cho từng case FAIL | `starter_v0/runs/<v0>.json`, `version_log.csv`, bảng B2 | C1 |
| 15:30 | **v1** — sửa `system_prompt.md`: bỏ chỉ dẫn xấu (đoán thay vì hỏi, gửi không xác nhận, ép một bước); thêm rule hỏi lại / xác nhận / từ chối out-of-scope | `starter_v0/artifacts/system_prompt.md` | C2, C3 |
| 16:00 | **v2** — viết lại description trong `tools.yaml` (khi nào dùng / không dùng); merge khai báo tool mới của B + run `v1-newtool` | `starter_v0/artifacts/tools.yaml` | C2, C3 |
| 17:30 | **v3** — convention args (handle không `@`, `topic=news`, `timeframe`, `search_type=Top`, giữ `limit` qua lượt) | `tools.yaml` / `system_prompt.md` | C2, C3 |
| Trước deadline | Bảng B1, B2, B6 trong `group_report.md`; kiểm tra checklist `SUBMISSION.md`; ghi commit chốt | `report/team/group_report.md` | C7 |

## 3. Đóng góp cụ thể

_(Điền sau khi làm, dựa trên run thật — không điền trước.)_

| Version | Thay đổi | Giả thuyết | Metric trước → sau | Run file |
| ------- | -------- | ---------- | ------------------ | -------- |
| v0 | Baseline, không sửa | — | — → | |
| v1 | | | | |
| v2 | | | | |
| v3 | | | | |

Nhận xét chính từ failure analysis:

-

## 4. Bằng chứng

- File/commit/PR:
- Run JSON (`provider_error_cases == 0`, `measured_cases == total_cases`):
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

- Điều làm tốt:
- Điều chưa làm được / sẽ làm khác:
- Điều học được về vòng lặp evidence-driven:
