---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Search (Algolia)
requires_env: []
inputs: [query, sort, limit]
outputs: [items]
side_effect: false
---
# hn_search

Tool mới của nhóm RICONs.
Tìm bài (story) trên Hacker News qua API Algolia công khai, trả tiêu đề, link, số điểm, số bình luận và link thảo luận HN.
Dùng khi user hỏi cộng đồng Hacker News / dân kỹ thuật đang bàn gì về một chủ đề.
Không dùng cho Twitter/X (dùng `social_search`), tin tức báo chí (dùng `lookup` với `topic=news`), hay paper (dùng `papers`).

- Không cần API key.
- `sort`: `relevance` (mặc định, endpoint `search`) hoặc `latest` (endpoint `search_by_date`); giá trị khác trả error dict.
- `limit` kẹp vào 1-10; số dạng chuỗi được ép kiểu.
- Bài không có link ngoài (Ask HN, Show HN dạng text) dùng link thảo luận HN làm `url`.
