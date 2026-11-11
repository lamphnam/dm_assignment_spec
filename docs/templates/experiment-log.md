# Experiment log — <slug lời giải của bạn>

> Copy file này vào `experiments/EXPERIMENTS.md` trong bản clone của bạn. Mỗi thí nghiệm là một mục.
> Không xoá mục cũ, kể cả thí nghiệm thất bại. Không ghi token hay thông tin cá nhân.

## Thông tin chung
- **Hướng tiếp cận:** <mô tả ngắn hướng bạn chọn>
- **Phương pháp đã học dùng (FR-04):** <classification | regression | clustering | itemsets>
- **Dữ liệu:** SHA-256 khớp [05 §1](../05-dataset-overview.md#1-nguồn)? <có/không>
- **Validation protocol:** <mô tả protocol bạn chọn: cách chia, seed, cách chấm>
- **Scorer:** qua T1–T9 ([11 §1](../11-testing-evaluation.md#1-đặc-tả-offline-scorer))? <có/không>
- **Baseline bạn chọn để so sánh (rubric tiêu chí 6):** <mô tả> = <score±std> (cùng protocol)

---

## EXP-001 — <tiêu đề ngắn>
- **Ngày:** YYYY-MM-DD   **Commit:** <hash>   **Config:** `configs/<file>` (seed=<n>)
- **Giả thuyết:** <điều gì sẽ thay đổi và vì sao, dựa trên phân tích nào của bạn>
- **Thay đổi so với thí nghiệm trước:** <một thay đổi>
- **Kết quả:**

  | Đánh giá | Score (mean ± std) | Q | R | % bài được chọn |
  |---|---|---|---|---|
  | <protocol validation của bạn> | | | | |
  | Δ so với baseline tốt nhất | | | | |

- **Feature/ablation:** <bỏ X thì Score thay đổi bao nhiêu>
- **Lỗi điển hình:** <bài label 1 bị xếp cao hoặc bài label 5 bị loại, lý do có thể>
- **Kết luận:** <chấp nhận / bác bỏ giả thuyết; chênh lệch có vượt ~1 std không>
- **Có nộp không?** <không | có → submission id trong `submissions/LOG.md`>
- **Thời gian chạy / phần cứng:** <…>
