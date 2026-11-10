---
name: hf_model
track: bonus
kind: live_api
provider: Hugging Face Hub API
requires_env: []
inputs: [query, limit]
outputs: [items]
side_effect: false
---
# hf_model

Tool mới của nhóm RICONs.
Tìm model trên Hugging Face Hub theo tên hoặc id, sắp theo lượt tải, trả license, task (`pipeline_tag`), lượt tải, lượt thích, có bị gated không và ngày cập nhật cuối.
Dùng khi user hỏi thông tin model card: "model X có license gì", "model X dùng cho task gì", "model nào tải nhiều nhất".
Không dùng cho paper nghiên cứu về model (dùng `papers`), tin tức về model (dùng `lookup` với `topic=news`), hay khái niệm chung (dùng `wiki`).

- Không cần API key; một request `GET /api/models?search=...&full=true`.
- `query` rỗng trả error dict, không gọi mạng; `limit` kẹp vào 1-5.
- License lấy từ tag `license:<tên>` của model; không có tag thì `license` là `None`.
