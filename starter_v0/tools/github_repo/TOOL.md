---
name: github_repo
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [repo]
outputs: [items, stars, forks, open_issues, license, language, last_push, archived]
side_effect: false
---
# github_repo

Tool mới của nhóm RICONs.
Lấy trạng thái hiện tại của một repo GitHub public: số sao, fork, issue đang mở, license, ngôn ngữ, lần push cuối, có bị archive không.
Dùng khi user hỏi về một repo code cụ thể ("repo X còn được maintain không", "LangGraph bao nhiêu sao", "license của repo này").
Không dùng để đọc nội dung một trang web hay README (dùng `fetch`), hay tin tức về công ty đứng sau repo (dùng `lookup`).

- Không bắt buộc API key; nếu có env `GITHUB_TOKEN` thì gửi kèm để tăng rate limit (60 request/giờ khi không có token).
- `repo` nhận `owner/name` hoặc URL github.com (có thể kèm `.git` hay đường dẫn con); chuỗi khác trả error dict, không gọi mạng.
- Repo không tồn tại hoặc private (HTTP 404) trả error dict `LookupError`, không raise.
- `items` có dạng `title`/`url`/`source`/`summary` như các tool tra cứu khác, nên đưa thẳng vào `format` được.
