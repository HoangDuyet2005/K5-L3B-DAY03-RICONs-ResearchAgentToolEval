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

- Tool mới: `wiki` ([`starter_v0/tools/wiki/`](../../starter_v0/tools/wiki/)) tra Wikipedia `vi`/`en` và trả đoạn mở đầu của bài khớp nhất kèm link.
  Chọn vì các tool có sẵn thiếu kiến thức nền ổn định (định nghĩa, tiểu sử, lịch sử), và ranh giới với `lookup` rõ: `lookup` cho tin mới, `wiki` cho thứ ít đổi theo ngày, nên viết được eval case routing.
  Không cần API key, một request MediaWiki duy nhất, `items` cùng dạng với `lookup` nên đưa thẳng vào `format` được.
- Unit test (tên test → hành vi kiểm tra), trong [`tests/test_tools_todo.py`](../../starter_v0/tests/test_tools_todo.py):
  - `test_wiki_sends_one_search_request_and_maps_pages_by_rank` → đúng request (URL, query, limit, User-Agent) và sắp kết quả theo thứ hạng `index`, vì API trả các trang không theo thứ tự.
  - `test_wiki_empty_query_returns_error_without_request` → `query` rỗng trả error dict, không gọi mạng.
  - `test_wiki_out_of_enum_lang_returns_error_without_request` → `lang` ngoài `vi`/`en` trả error dict, không gọi mạng.
  - `test_wiki_coerces_string_count_and_clamps_it_to_1_to_5` → `"3"` thành 3, 0 thành 1, 50 thành 5, `"EN"` thành `en`.
  - `test_wiki_no_match_returns_empty_items_not_error` → không có bài khớp thì `items` rỗng, không phải lỗi.
  - `test_wiki_http_error_returns_error_dict`, `test_wiki_timeout_returns_error_dict` → HTTP 429 và timeout trả error dict, không raise.
- Eval case nhóm đáng chú ý: trên Haiku 5.5 cả 10 case PASS ngay ở v0, nên mình chạy thêm trên `gpt-4.1-nano` để kiểm tra bộ case có bắt được lỗi không.
  Ở v0, 4 case FAIL đúng loại lỗi đã thiết kế: G04 đoán `social_search(query="ông ấy")` thay vì hỏi lại, G05 thiếu `topic`/`timeframe`, G07 thiếu `confirmed=true`, G10 gọi `send` khi chưa có nội dung.
  G10 vẫn FAIL ở v3 trên nano, nhưng lần gọi `send` đó không gửi gì vì thiếu `confirmed=true`: guardrail trong code chặn được chỗ prompt chưa chặn.
- UI: `cd starter_v0` rồi `streamlit run app.py` ([`starter_v0/app.py`](../../starter_v0/app.py)); link dùng thử qua Cloudflare Tunnel ở mục A1 của báo cáo nhóm.
  UI hiện mọi tool call và kết quả thô, lỗi tool được tô đỏ, mỗi phiên ghi transcript cùng format với `chat.py`.
- Live chat: agent hỏi lại khi thiếu tài khoản (T2), xin xác nhận yes/no trước khi đăng Telegram và chỉ gửi sau khi user đồng ý (T3).
  Khi test live, mình phát hiện agent không bao giờ gửi được Telegram dù user xác nhận nhiều lần: lịch sử hội thoại của `chat.py` bỏ hết kết quả tool, nên ở lượt sau model nghĩ bản tin của chính nó không có nguồn.
  Mình sửa trong UI bằng cách lưu kèm bằng chứng tool vào lịch sử (chi tiết ở mục 5 báo cáo nhóm).

## 4. Bằng chứng

- File/commit/PR: PR [#1](https://github.com/HoangDuyet2005/K5-L3B-DAY03-RICONs-ResearchAgentToolEval/pull/1); commit `2c00871` (tool `wiki` + 7 test), `1cdfc92` (10 case eval nhóm, khai báo `wiki`), `69874d4` (UI + Phần A), `8c9eac2` (run v3-wiki, `version_log`, `.gitattributes`), `cb88930` (sửa lịch sử hội thoại, B4, Telegram).
- Output `pytest`: `74 passed, 14 skipped` (0 failed; 14 skipped là stub của tool có sẵn, không phải test của `wiki`).
- Run group JSON (`provider_error_cases == 0`, `measured_cases == total_cases`): [`v0-wiki_B_group_…181343247036.json`](../../starter_v0/runs/v0-wiki_B_group_openrouter_20261110T181343247036.json), [`v3-wiki_B_group_…185942635818.json`](../../starter_v0/runs/v3-wiki_B_group_openrouter_20261110T185942635818.json), cùng 2 run cross trên nano (bảng B3).
- Transcript: [`…193835828410.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T193835828410.transcript.json) (gửi Telegram sau xác nhận), [`…191950185955.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T191950185955.transcript.json) (thiếu tài khoản rồi bổ sung), [`…190837448475.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T190837448475.transcript.json) (yêu cầu thường, tool lỗi), [`…192055287079.transcript.json`](../../starter_v0/transcripts/ui_streamlit_openrouter_20261110T192055287079.transcript.json) (lỗi trước khi sửa).
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:

## 5. Tự đánh giá

- Điều làm tốt:
- Điều chưa làm được / sẽ làm khác:
- Khác biệt giữa unit test (đo code tool) và eval (đo lựa chọn của model) mà mình rút ra:
