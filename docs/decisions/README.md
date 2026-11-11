# Architecture Decision Records (ADR)

ADR ghi lại **các quyết định của repo nhóm, lý do đưa ra và hệ quả**. Trong bản clone của mình, bạn có thể thêm ADR cho lời giải riêng.
Trạng thái: `Proposed` → `Accepted` → (`Superseded by NNNN` | `Deprecated`).

| # | Tiêu đề | Trạng thái |
|---|---|---|
| [0001](0001-docs-as-source-of-truth.md) | `docs/` là nguồn tham chiếu; code trong bản clone là nguồn sự thật về lời giải | Accepted |
| [0002](0002-repository-layout-and-data-handling.md) | Cấu trúc repo; xử lý dữ liệu | Accepted |
| [0003](0003-kaggle-mcp-isolated-venv.md) | Kaggle MCP chạy trong venv riêng, pin `mcp<2` | Accepted |
| [0004](0004-test-csv-parsing.md) | Cách đọc `Test.csv` dùng trong `tools/` (tham khảo) | Accepted, chỉ áp dụng cho tools |
| [0005](0005-metric-definition-source.md) | Trang Evaluation là định nghĩa metric tạm thời | Proposed |
| [0006](0006-skills-canonical-location.md) | Agent Skills: nguồn chuẩn ở `.claude/skills/` | Proposed |
| [0008](0008-internal-knowledge-base-model.md) | Repo là knowledge base nội bộ, trung tính, không có workflow nhóm | Accepted |

Số 0007 (gộp team) đã bị xoá và được thay bằng 0008.

## Template

```markdown
# NNNN — <Tiêu đề>
- **Trạng thái:** Proposed
- **Ngày:** YYYY-MM-DD
## Bối cảnh
## Quyết định
## Phương án đã cân nhắc
## Hệ quả
```
