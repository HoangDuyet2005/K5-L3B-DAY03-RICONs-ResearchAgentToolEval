---
name: wiki
track: bonus
kind: live_api
provider: Wikipedia (MediaWiki Action API)
requires_env: []
inputs: [query, lang, max_results]
outputs: [items]
side_effect: false
---
# wiki

Tool mới của nhóm RICONs.
Tìm trên Wikipedia (`vi` hoặc `en`) và trả về đoạn mở đầu của các bài khớp nhất.
Dùng cho kiến thức nền, định nghĩa, tiểu sử, lịch sử: những thứ ít thay đổi theo ngày.
Không dùng cho tin tức hoặc sự kiện mới (dùng `lookup` với `topic=news`), bài đăng mạng xã hội (`timeline` / `social_search`), hay một URL cụ thể (`fetch`).

- Không cần API key; gửi header `User-Agent` theo quy định của Wikipedia (đổi bằng env `WIKI_USER_AGENT`).
- Một request duy nhất: `generator=search` + `prop=extracts|info` trả về cả kết quả tìm kiếm lẫn intro.
- `max_results` bị kẹp vào khoảng 1-5; số dạng chuỗi (`"3"`) được ép kiểu.
- `lang` ngoài `vi`/`en`, hoặc `query` rỗng, trả về error dict thay vì raise.
- `items` có cùng dạng `title`/`url`/`source`/`summary` như `lookup`, nên đưa thẳng vào `format` được.
