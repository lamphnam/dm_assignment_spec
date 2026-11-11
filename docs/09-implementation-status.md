# 09 — Trạng thái của repo

**Cập nhật:** 2026-11-11. File này mô tả **knowledge base của nhóm**. Trạng thái lời giải của **bạn** thì ghi trong bản clone của bạn.

## 1. Repo có gì

| Thành phần | Trạng thái |
|---|---|
| Đặc tả và luật (01, 02, 14, `reference/`) | ✅ Đã đối chiếu với trang Kaggle ngày 2026-11-11 |
| Dữ liệu và các phát hiện đã kiểm chứng (05–07) | ✅ Tính trên dữ liệu ngày 2026-11-11; tái lập bằng `tools/inspect_data.py` |
| Phân tích metric, mốc tham chiếu, đặc tả scorer (08, 11) | ✅ T1–T9 pass trên `tools/score.py` |
| Công cụ tham chiếu (`tools/`) | ✅ Đã kiểm thử ([tools/README.md](../tools/README.md)) |
| Hướng dẫn môi trường, Kaggle CLI và MCP (10, integrations) | ✅ Lệnh tải dữ liệu và MCP đã chạy được; lệnh nộp bài **chưa chạy** |
| Agent Skills (8) | ✅ Frontmatter hợp lệ; Claude Code đã phát hiện được skill |
| Lời giải, dữ liệu, kết quả | Không có, theo đúng thiết kế |

## 2. Môi trường dùng để kiểm chứng **[Xác minh, 2026-11-11]**

Windows 11 Pro; Python 3.14.5 (không có pandas, numpy, sklearn); git 2.45.1. Kaggle MCP được cài trong venv riêng:
kaggle-mcp-server 0.2.0, `mcp` 1.30.0, kaggle 2.2.5, kagglesdk 0.1.38, six 1.17.0.

## 3. Nhật ký thay đổi

| Ngày | Thay đổi |
|---|---|
| 2026-11-11 | Tạo tài liệu; cài và kiểm tra Kaggle MCP |
| 2026-11-11 | Audit: xác minh luật, thêm skills và tools, sửa số liệu oracle, phát hiện leakage qua `id` |
| 2026-11-11 | Bỏ toàn bộ hạ tầng làm việc nhóm (task board, tracker, gộp team, so sánh giữa thành viên) |
| 2026-11-11 | **Chốt mô hình (ADR-0008):** repo là knowledge base nội bộ của nhóm 5 người. Khôi phục phân tích dữ liệu và `tools/` (trước đó bị cách ly), gắn cảnh báo về luật chia sẻ. Bỏ các nội dung mang tính chỉ định lời giải: baseline B0/B1, protocol validation cố định, thiết kế gợi ý, kiến trúc pipeline (03), danh sách feature gợi ý |
| 2026-11-11 | Ghi câu trả lời của giảng viên cho Q-11..Q-14: được chia sẻ trong nhóm, nộp độc lập, cuối kỳ gộp vào team của người cao điểm nhất. Thêm điều kiện gộp §5c (trần tổng submission) vào 14 |
