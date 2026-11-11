# 0005 — Trang Evaluation là định nghĩa metric tạm thời

- **Trạng thái:** Proposed
- **Ngày:** 2026-11-11
- **Người đề xuất:** agent khởi tạo docs
- **Liên quan:** C-01, Q-01, R-07; task T-003, T-012

## Bối cảnh
Abstract nói Coverage được đo "through title similarity across all reading-list lengths". Trang Evaluation lại định nghĩa
Coverage là recall của các bài có rating > 1, và nói rõ *"title similarity is not part of the metric"*.

## Quyết định (đề xuất)
Tạm dùng **công thức trên trang Evaluation** cho offline scorer, vì trang này có công thức đầy đủ, ví dụ số và mô tả
từng trường hợp biên. Đồng thời giữ câu hỏi Q-01 mở và hỏi giảng viên.

## Hệ quả
- Không đầu tư vào diversification theo title cho đến khi Q-01 được trả lời.
- Nếu câu trả lời khác, cần viết ADR mới thay thế ADR này và cập nhật [08](../08-methodology.md) và [11](../11-testing-evaluation.md).
