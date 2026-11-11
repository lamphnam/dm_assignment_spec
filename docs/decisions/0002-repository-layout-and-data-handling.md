# 0002 — Cấu trúc repo và cách xử lý dữ liệu

- **Trạng thái:** Accepted (cập nhật ngày 2026-11-11 theo ADR-0008)
- **Ngày:** 2026-11-11
- **Liên quan:** FR-06, FR-07, FR-09, NFR-08; [04](../04-repository-structure.md)

## Quyết định
- Repo nhóm chỉ có `README.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `.claude/skills/`, `tools/`, `docs/`. Không có lời giải, dữ liệu hay kết quả.
- `data/` không bao giờ được commit. `.gitignore` loại `data/`, `*.zip`, credentials, venv, `.agents/skills`.
- Thành viên tự tổ chức bản clone của mình. Không push lên repo nhóm. Nếu cần GitHub (Rules §5), dùng repo **private** riêng.

## Hệ quả
- Ai muốn tái lập lời giải cũng cần tài khoản Kaggle để tải dữ liệu.
