# 12 — Reproducibility

Rules §5 yêu cầu tái lập được submission đã chọn từ dữ liệu có sẵn. Kết quả không tái lập được thì không đạt điểm tối đa
phần implementation và evaluation (NFR-01). Hiện **chưa có gì** để tái lập. Tài liệu này là checklist và quy ước **[Đề xuất]**.

## 1. Checklist README nộp bài (FR-07)

README ở gốc repo (khác với `docs/README.md`) phải có:

- [ ] **Input:** `train.csv`, `Test.csv`, `Submission.csv`; nguồn (URL competition); **SHA-256** ([05 §1](05-dataset-overview.md#1-nguồn));
      các bước chuẩn bị (parser `Test.csv`); mọi dữ liệu ngoài hoặc pretrained model kèm nguồn và trích dẫn (NFR-06).
- [ ] **Môi trường:** phiên bản Python, `requirements.txt` đã pin, **random seed** đã dùng.
- [ ] **Lệnh chính xác** để train và sinh `id,priority`, ví dụ `python scripts/make_submission.py --config configs/final.yaml`.
- [ ] **Local validation:** protocol ([11 §2](11-testing-evaluation.md#2-local-validation)), lệnh chạy, **kết quả mong đợi**
      (Score/Q/R mean ± std).
- [ ] **Tái lập submission đã chọn:** lệnh, commit hash, SHA-256 của CSV mong đợi.
- [ ] **Phần cứng, thời gian chạy ước tính, các hạn chế** (ví dụ tính không tất định của thư viện, có cần GPU hay không).
- [ ] Công khai việc dùng metadata của test theo cách unsupervised, nếu có (NFR-05).

## 2. Quy tắc tất định

- Mọi nguồn ngẫu nhiên (`random`, `numpy`, model, CV split) đều lấy seed từ config.
- Sort phải ổn định. Nếu score bằng nhau, phá hoà theo `id`.
- Pin chính xác phiên bản thư viện. Ghi `python --version` và `pip freeze`.
- Không phụ thuộc vào thứ tự liệt kê file của hệ điều hành, và không gọi network trong lúc sinh submission
  (nếu có dữ liệu ngoài thì cache lại và ghi checksum).

## 3. Manifest cho mỗi submission

Lưu tại `submissions/manifest.json`, mỗi lần nộp thêm một entry. **[Đề xuất]**

```json
{
  "file": "submissions/20261120-2130_venue-prior.csv",
  "sha256": "<sha256 của file CSV>",
  "git_commit": "<full commit hash>",
  "command": "python scripts/make_submission.py --config configs/venue_prior.yaml",
  "seed": 42,
  "local_validation": {"score_mean": null, "score_std": null, "q_mean": null, "r_mean": null, "protocol": "A+B, 5x5 folds"},
  "kaggle_submission_id": null,
  "public_score": null,
  "selected_as_final": false,
  "experiment_id": "EXP-NNN",
  "submitted_at_utc": "2026-11-20T14:30:00Z"
}
```

- **Giữ nguyên file CSV đã nộp** (FR-09). Không sinh lại rồi ghi đè.
- Báo cáo cần có `git_commit` của bản final và `kaggle_submission_id` (FR-08).

## 4. Kiểm tra trước khi nộp báo cáo

1. Clone repo vào một thư mục sạch.
2. Làm theo README từ đầu, dùng dữ liệu tải mới.
3. So SHA-256 của CSV sinh ra với manifest. Hai giá trị phải trùng nhau (hoặc nêu rõ lý do nếu không thể tất định).
4. So kết quả local validation với con số trong README.
