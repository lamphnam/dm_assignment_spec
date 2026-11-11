# 0003 — Kaggle MCP chạy trong venv riêng, pin `mcp<2`

- **Trạng thái:** Accepted (đã triển khai trên một máy của nhóm, 2026-11-11). Với các sinh viên khác, đây là **hướng dẫn tùy chọn**
  để cài trên máy của mình ([integrations](../integrations/kaggle-mcp-setup.md))
- **Ngày:** 2026-11-11
- **Liên quan:** [integrations/kaggle-mcp-setup.md](../integrations/kaggle-mcp-setup.md)

## Bối cảnh
- Người dùng yêu cầu cài [Galaxy-Dawn/kaggle-mcp](https://github.com/Galaxy-Dawn/kaggle-mcp) (PyPI: `kaggle-mcp-server`).
- README của server khuyến nghị chạy bằng `uvx`, nhưng máy không có `uv`.
- `pip install kaggle-mcp-server` (0.2.0) tự kéo về `mcp` 2.3.0. Khi đó `import kaggle_mcp.server` lỗi
  `ModuleNotFoundError: No module named 'mcp.server.fastmcp'`, vì `mcp` 2.x đã đổi tên FastMCP. **[Xác minh]**

## Quyết định
- Tạo venv riêng `%USERPROFILE%\.kaggle-mcp-venv`, cài `kaggle-mcp-server` cùng `"mcp<2"` (được 1.30.0) và `six`
  (Kaggle CLI 2.2.5 thiếu package này).
- Đăng ký với Claude Code bằng `claude mcp add kaggle --scope local`. Token được truyền qua `-e KAGGLE_API_TOKEN=...`
  và được lưu trong `~/.claude.json`, **ngoài repo**.

## Phương án đã cân nhắc
- *Cài `uv` rồi dùng `uvx`:* thêm một công cụ toàn cục. Vì pip đã tự kéo về `mcp` 2.3.0, nhiều khả năng `uvx` cũng resolve
  `mcp` 2.x và gặp cùng lỗi nếu không thêm ràng buộc (`--with "mcp<2"`). **[Suy luận, chưa thử]**
- *Hạ `mcp` trong Python toàn cục:* có thể làm hỏng công cụ khác dùng `mcp` 2.x.
- *Project-scope `.mcp.json`:* tiện chia sẻ, nhưng dễ commit lộ token nếu không dùng `${VAR}`.

## Hệ quả
- Server phụ thuộc vào đường dẫn venv cụ thể của máy này. Máy khác phải cài lại theo hướng dẫn trong tài liệu tích hợp.
- Khi `kaggle-mcp-server` hỗ trợ `mcp` 2.x thì có thể bỏ pin. Cần kiểm tra lại bằng cách import `kaggle_mcp.server`.
