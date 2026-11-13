# Submission log — NAM PHẠM HOÀNG

> Giữ nguyên các file CSV đã nộp tại đường dẫn ghi trong bảng. Không ghi token.

## Ngân sách
- Quota: **3/ngày/team** ([Xác minh] 2026-11-11). Deadline: 2026-12-14 23:59:59 UTC. Số final submission được chọn: **tối đa 3** (trang Submissions của Kaggle, 2026-11-14: "Select up to 3 submissions… If less than 3 are selected, Kaggle will automatically select from your best scoring submissions"; trả lời Q-05)
- Quota reset lúc **00:00 UTC = 07:00 sáng giờ VN** (trang Submit lúc ≈02:00 VN 14/11 báo "resets in 5 hours"). Ngày UTC 2026-11-13 đã dùng 2/3.
- Chỉ nộp khi có bằng chứng local tốt hơn lần trước, vượt mức nhiễu.
- Cuối kỳ gộp team: tổng lượt của cả nhóm phải dưới trần (docs/14).

## Mốc trên Public LB (quan sát 2026-11-14 từ screenshot)
- Benchmark của host (dòng riêng, icon benchmark, không có thành viên): **0.60953**. Đây nhiều khả năng là "Baseline" dùng cho mức sàn 6.5 (Q-03).
- Team sinh viên tên `baseline_submission.csv`: 0.66962. Top: 0.68281.

## Nhật ký

| # | Ngày UTC | EXP id | File | SHA-256 (12 ký tự đầu) | Commit | Local CV (mean±std) | Public | Kaggle submission id | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|
| 3 | **chưa nộp** (chuẩn bị 2026-11-13 22:20 UTC = 05:20 ngày 14/11 giờ VN) | exp004_ft_ens_v1 | `submissions/exp004_ft_ens_v1.csv` | `a89e78ee4b4f` | `001d413` | 0.6302 ± 0.0091 (Q 0.523, R 0.796), cùng quy trình chọn ngưỡng với EXP-003 (0.6178) | | | Δ +0.0123 (paired honest +0.0135, tốt hơn ở 15/15 fold). Dưới mức +0.015 đặt ra; sinh viên đồng ý vẫn đề cử bản tốt nhất. Chọn 353/596, threshold 0.60; trùng EXP-003 311 bài, bỏ 52, thêm 42 |
| 2 | 2026-11-13 18:50 (01:50 ngày 14/11 giờ VN) | exp003_embed_v1 | `submissions/exp003_embed_v1.csv` | `11645f1f4e2e` | `cd8f9ef` | 0.6178 ± 0.0097 (Q 0.515, R 0.773) | **0.64656** | 58318548 | Hạng 21/26 lúc nộp; CV lệch LB +0.029. Chọn 363/596, threshold 0.55. Embeddings MiniLM+MPNet+SPECTER + kNN + TF-IDF |
| 1 | 2026-11-13 17:19 (00:19 ngày 14/11 giờ VN) | exp002_logreg_text | `submissions/exp002_logreg_text.csv` | `84a1f29f739b` | chưa commit (message ghi `<commit-hash>` nguyên văn) | 0.5768 ± 0.0111 (Q 0.451, R 0.802) | **0.59467** | 58316339 | Dưới benchmark host 0.60953. CV lệch LB +0.018, trong mức nhiễu |

Submission id và giờ nộp của #1, #2 lấy từ `kaggle competitions submissions assignment-data-mining-261` (2026-11-13 22:09 UTC).
