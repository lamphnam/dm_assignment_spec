# 0004 — Cách đọc `Test.csv` dùng trong `tools/` (neo theo venue/year)

- **Trạng thái:** Accepted cho `tools/inspect_data.py`. Đây là **tham khảo**: mỗi thành viên tự chọn cách đọc cho lời giải của mình
- **Ngày:** 2026-11-11
- **Liên quan:** C-04, Q-08, R-03

## Bối cảnh
`Test.csv` không quote các field chứa dấu phẩy và đã bỏ mọi khoảng trắng sau dấu phẩy. Số field mỗi dòng từ 6 đến 16.
34 dòng có dấu phẩy trong `title`. Xem [05 §2](../05-dataset-overview.md#2-đặc-điểm-định-dạng).

## Quyết định
Tools dùng thuật toán ở [07 §2](../07-data-processing.md#2-parse-testcsv):
- `id` lấy từ field đầu, `doi` lấy từ field cuối.
- Tìm **duy nhất** vị trí `i` sao cho `f[i]` ∈ {kr, cav, lics, iclp, lpnmr} và `f[i+1]` là năm 4 chữ số.
- Phần nằm giữa `id` và venue là title; phần nằm giữa year và `doi` là authors.
- Gặp dòng mơ hồ thì **dừng hẳn**, không đoán.

Thuật toán đã được thử trên dữ liệu ngày 2026-11-11: 596/596 dòng parse được, venue và year đều hợp lệ.

## Phương án đã cân nhắc
- *Sửa tay file:* vi phạm quy tắc không sửa dữ liệu gốc và không tái lập được.
- *Heuristic dựa trên số field:* không xử lý được trường hợp title chứa dấu phẩy.

## Hệ quả
- Phụ thuộc vào tập venue cố định. Nếu host thêm venue mới, parser sẽ dừng với lỗi rõ ràng.
- Nên kiểm tra các dòng 756, 1368 (title có dấu phẩy) và 979 (nhiều tác giả) khi tự viết cách đọc khác.
