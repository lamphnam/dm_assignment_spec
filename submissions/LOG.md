# Submission log — NAM PHẠM HOÀNG

> Giữ nguyên các file CSV đã nộp tại đường dẫn ghi trong bảng. Không ghi token.

## Ngân sách
- Quota: **3/ngày/team** ([Xác minh] 2026-11-11). Deadline: 2026-12-14 23:59:59 UTC. Số final submission được chọn: <Q-05 chưa rõ>
- Chỉ nộp khi có bằng chứng local tốt hơn lần trước, vượt mức nhiễu.
- Cuối kỳ gộp team: tổng lượt của cả nhóm phải dưới trần (docs/14).

## Mốc trên Public LB (quan sát 2026-11-14 từ screenshot)
- Benchmark của host (dòng riêng, icon benchmark, không có thành viên): **0.60953**. Đây nhiều khả năng là "Baseline" dùng cho mức sàn 6.5 (Q-03).
- Team sinh viên tên `baseline_submission.csv`: 0.66962. Top: 0.68281.

## Nhật ký

| # | Ngày UTC | EXP id | File | SHA-256 (12 ký tự đầu) | Commit | Local CV (mean±std) | Public | Kaggle submission id | Ghi chú |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 2026-11-14 | exp003_embed_v1 | `submissions/exp003_embed_v1.csv` | `11645f1f4e2e` | xem commit "exp003" | 0.6178 ± 0.0097 (Q 0.515, R 0.773) | <chờ nộp> | | Chọn 363/596, threshold 0.55. Embeddings MiniLM+MPNet+SPECTER + kNN + TF-IDF. Không cấu hình embedding lớn nào vượt (sweep4) |
| 1 | 2026-11-14 | exp002_logreg_text | `submissions/exp002_logreg_text.csv` | `84a1f29f739b` | chưa commit (message ghi `<commit-hash>` nguyên văn) | 0.5768 ± 0.0111 (Q 0.451, R 0.802) | **0.59467** | <chưa ghi> | Dưới benchmark host 0.60953. CV lệch LB +0.018, trong mức nhiễu |
