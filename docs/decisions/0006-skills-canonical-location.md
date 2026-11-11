# 0006 — Vị trí chuẩn của Agent Skills

- **Trạng thái:** Proposed
- **Ngày:** 2026-11-11
- **Người đề xuất:** agent (Claude Code)
- **Liên quan:** [agents/skills.md](../agents/skills.md)

## Bối cảnh
Claude Code quét `.claude/skills/`, Codex quét `.agents/skills/`. Cả hai đều theo symlink (theo tài liệu). Yêu cầu đặt ra:
ưu tiên Claude Code, tương thích với agent khác nếu khả thi, và **chỉ có một nguồn chuẩn**.

## Quyết định (đề xuất)
- Nguồn chuẩn là `.claude/skills/<name>/`. `name` trong frontmatter trùng tên thư mục, đúng theo chuẩn Agent Skills.
- Frontmatter chỉ dùng `name` và `description`, là hai trường chung của chuẩn, Claude Code và Codex.
- Agent đọc `.agents/skills` dùng **liên kết thư mục cục bộ** tới `.claude/skills` (junction trên Windows, symlink trên Unix).
  Liên kết này không commit.

## Phương án đã cân nhắc
- *Đặt bản chính trong `.agents/skills` và liên kết `.claude/skills` sang đó:* tương đương về kỹ thuật. Không chọn vì Claude Code được ưu tiên.
- *Commit một bản sao do script sinh ra:* thêm bước đồng bộ và dễ bị lệch nếu ai đó sửa nhầm vào bản sao.
- *Commit symlink:* trên máy này không tạo được symlink nếu không có quyền admin hoặc Developer Mode **[Xác minh]**;
  git trên Windows cũng cần `core.symlinks`.

## Hệ quả
- Claude Code đã phát hiện được skill từ `.claude/skills/` ngay trong session tạo ra chúng **[Xác minh, 2026-11-11]**.
- Từ ngày 2026-11-11, skill **không kèm script** (ADR-0008, [14](../14-compliance-and-distribution.md)).
- Người dùng Codex cần chạy một lệnh sau khi clone.
- Việc Codex có đọc qua junction hay không chưa được kiểm chứng. Nếu không đọc được thì cần dùng symlink (bật Developer Mode)
  hoặc viết ADR mới.
