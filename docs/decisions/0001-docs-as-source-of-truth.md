# 0001 — `docs/` là nguồn tham chiếu; code trong bản clone là nguồn sự thật về lời giải

- **Trạng thái:** Accepted (2026-11-11; cập nhật theo ADR-0008)
- **Ngày:** 2026-11-11
- **Liên quan:** [agents/agent-working-rules.md](../agents/agent-working-rules.md)

## Bối cảnh
Mỗi sinh viên dùng AI coding agent trong bản clone riêng. Agent bắt đầu mà không có lịch sử chat.
Cần một nơi duy nhất mô tả yêu cầu, dữ liệu, metric và quy ước.

## Quyết định
- `docs/` là nguồn tham chiếu cho yêu cầu và quy ước. `AGENTS.md` là bản tóm tắt bắt buộc; `CLAUDE.md` import `AGENTS.md`.
- Thứ tự ưu tiên khi các nguồn mâu thuẫn:
  1. Trang Kaggle (bản sao ở `docs/reference/`) cho **yêu cầu**.
  2. Code trong bản clone của sinh viên cho **hành vi thực tế của lời giải**.
  3. Các tài liệu khác trong `docs/`.
- Mâu thuẫn phải được ghi lại, không được âm thầm giải quyết.

## Hệ quả
- Sinh viên cập nhật docs **cục bộ** khi lời giải của họ thay đổi hành vi đã được mô tả. Không cần gửi ngược lên repo nhóm.
