# Template bàn giao giữa các phiên agent

Dùng khi một phiên agent kết thúc giữa chừng, hoặc khi chuyển sang agent hay công cụ khác, **trên cùng bản clone của một sinh viên**.
Lưu tại `docs/handoffs/YYYYMMDD-<chủ-đề>.md` trong bản clone, hoặc nơi sinh viên chọn. Chỉ ghi **sự thật**: "đã kiểm tra" nghĩa là đã chạy thật, kèm output.

```markdown
## Handoff — <chủ đề> — YYYY-MM-DD

- **Agent/công cụ:** <tên/model>   **Commit/branch:** <hash hoặc "chưa commit">
- **Trạng thái:** xong | đang dở | bị chặn (lý do)

### Mục tiêu
- <việc này nhằm đạt điều gì; tiêu chí hoàn thành>

### File liên quan
- `<đường dẫn>`: <vai trò>

### Đã thay đổi
- `<đường dẫn>`: <thay đổi gì, vì sao>

### Quyết định
- <quyết định quan trọng và lý do; ADR cục bộ nếu có>

### Thí nghiệm đã chạy (nếu có)
| EXP id | Thay đổi | Score (mean ± std) | Q | R | Kết luận |
|---|---|---|---|---|---|

### Đã kiểm tra
| Kiểm tra | Lệnh | Kết quả thật |
|---|---|---|

Chưa kiểm tra (và lý do): <...>

### Còn lại
- <việc chưa xong, bug đã biết>
- <câu hỏi mở về luật hay metric>

### Rủi ro đã biết
- <leakage, overfit, quota...>

### Bước tiếp theo đề xuất
1. <...>
```
