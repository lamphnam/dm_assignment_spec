# Diễn giải điểm số

## Phân loại con số (luôn ghi rõ con số thuộc loại nào)

| Loại | Ví dụ | Dùng làm gì |
|---|---|---|
| **Đo được (measured)** | Score của model trên fold validation lấy từ train | Ra quyết định |
| **Ước lượng (estimate)** | Mốc "chọn tất cả" tính trên các subset label của train | Mốc so sánh. Không phải điểm test |
| **Giả thuyết (hypothesis)** | "Thay đổi X sẽ tăng Q" | Cần thí nghiệm để kiểm chứng |
| **Oracle** | Dùng nhãn thật để sắp xếp | **Cận trên không đạt được.** Chỉ để hiểu metric, **không phải baseline** |
| **Public LB** | 298 bài ẩn | Quan sát có nhiễu. Không dùng để tune |

## Các mốc tham chiếu

Lệnh: `python tools/score.py bounds --train data/raw/train.csv` (seed 0, 200 subset × 298, label của train, chạy ngày 2026-11-11):

| Chiến lược | Loại | Score | Q | R |
|---|---|---|---|---|
| Chọn tất cả, thứ tự ngẫu nhiên | estimate (đạt được) | 0.526 ± 0.023 | 0.357 | 1.000 |
| Chọn tất cả, priority hằng số (tie-break theo id dạng text) | estimate (đạt được) | 0.532 ± 0.023 | 0.363 | 1.000 |
| Chọn tất cả, sắp theo nhãn thật | ORACLE | 0.623 ± 0.017 | 0.452 | 1.000 |
| Bỏ hết label 1, sắp theo nhãn thật | ORACLE | 0.780 ± 0.014 | 0.639 | 1.000 |

- Std khoảng 0.014–0.023 giữa các subset 298 bài là **thước đo mức nhiễu** khi so sánh lời giải, và khi đọc Public LB
  (cũng có 298 bài) **[Suy luận]**.
- Baseline trên Public LB (0.60953 / 0.66962, chưa rõ cái nào, Q-03) và top 0.68281 (snapshot 2026-11-11) là quan sát công khai,
  không phải con số tái lập được.

## Local và Public lệch nhau

| Triệu chứng | Nguyên nhân khả dĩ | Kiểm tra |
|---|---|---|
| Public thấp hơn nhiều so với local | Distribution shift (test không có `iclp`, nhiều `cav`/`lics` hơn; [05 §5](../../../../docs/05-dataset-overview.md#5-distribution-shift-giữa-train-và-test)) | Xem validation của bạn có phản ánh phân phối test không |
| Public thấp hơn local, và không giải thích được bằng shift | Leakage trong CV (target encoding ngoài fold, duplicate nằm khác fold) | Leakage checklist ở [07 §5](../../../../docs/07-data-processing.md#5-leakage-checklist) |
| Public dao động ±0.02 giữa các biến thể gần giống nhau | Nhiễu của 298 bài | Đừng chọn theo Public |
| Tỷ lệ bài được chọn trên test khác xa trên validation | Ngưỡng chọn bị shift | So sánh phân phối score giữa test và validation (unsupervised; phải công khai theo NFR-05) |
