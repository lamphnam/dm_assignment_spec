# Experiment log — embedding-logreg

> Mỗi thí nghiệm là một mục. Không xoá mục cũ, kể cả thí nghiệm thất bại. Không ghi token hay thông tin cá nhân.

## Thông tin chung
- **Hướng tiếp cận:** dự đoán phân phối nhãn 1–5 và P(label>1) từ metadata + embedding của title; chọn bài theo ngưỡng P(label>1), sắp thứ tự theo gain kỳ vọng E[(y−1)/4].
- **Phương pháp đã học dùng (FR-04):** classification (logistic regression multinomial + binary).
- **Dữ liệu:** SHA-256 khớp docs/05 §1: **có** (`src/data.py::verify_checksums`, chạy mỗi lần load).
- **Validation protocol (`src/validation.py`):** StratifiedGroupKFold 5 fold theo label, group = title chuẩn hoá (duplicate cùng fold), seeds 0/1/2 → 15 fold. Train trên toàn bộ fold train (kể cả `iclp`), **chấm chỉ trên bài không thuộc `iclp`** của fold validation (test không có `iclp`); mỗi fold chấm khoảng 405 bài. Không dùng `id` làm feature (Q-10).
- **Scorer:** `tools/score.py` (qua T1–T9) được dùng lại qua `src/metric.py`.
- **Mốc tham chiếu cùng protocol:** random chọn hết 0.4957 ± 0.0156; oracle chọn hết + thứ tự đúng 0.5905; oracle bỏ label 1 + thứ tự đúng 0.7579 (không đạt được).
- **Baseline (rubric tiêu chí 6):** EXP-001 điểm trung bình theo venue = 0.5247 ± 0.0125.

Ghi chú về ngưỡng: `run_experiment.py` chọn ngưỡng trên chính 15 fold rồi báo điểm ở ngưỡng đó (hơi lạc quan). `research/analysis_exp003.py` kiểm tra lại: ngưỡng chọn "trung thực" (trên 4 fold còn lại) cho đúng 0.55 ở cả 5 fold seed 0.

---

## EXP-001 — Baseline: điểm trung bình theo venue
- **Ngày:** 2026-11-14   **Commit:** cd8f9ef   **Lệnh:** `python -m scripts.run_experiment --model venue_mean --name exp001_venue_mean`
- **Giả thuyết:** venue là tín hiệu mạnh nhất (docs/05 §4), nên baseline tối thiểu là xếp theo venue.
- **Kết quả:** CV 0.5247 ± 0.0125 (Q 0.356, R 1.000). Chọn tất cả 596/596. Gần bằng random (0.496) vì trong cùng venue priority bằng nhau → Kaggle tie-break theo `id` dạng text.
- **Có nộp không?** Không.

## EXP-002 — Logistic regression trên TF-IDF title + venue + year + authors
- **Ngày:** 2026-11-14   **Commit:** cd8f9ef (file sinh trước commit, SHA-256 `84a1f29f739b…`)   **Model:** `logreg_text`
- **Kết quả:** CV 0.5768 ± 0.0111 (Q 0.451, R 0.802), ngưỡng 0.50, chọn 416/596. **Public 0.59467**.
- **Chẩn đoán OOF (seed 0):** AUC P(y>1) = 0.70. Giữ cách chọn của model, thứ tự hoàn hảo → 0.605; chọn hoàn hảo, giữ thứ tự của model → 0.730 ⇒ **điểm mất chủ yếu ở bước chọn bài**.
- **Có nộp không?** Có, lượt #1.

## Sweep 1 (2026-11-14) — biến thể TF-IDF (15 fold, ngưỡng tối ưu trên chính fold)
| Biến thể | Score |
|---|---:|
| exp002 C=1 | 0.5780 |
| C=0.3 / C=3 | 0.5714 / 0.5774 |
| + binary head riêng | 0.5790 |
| + char n-gram (3–5) | **0.5893** |
| + one-hot venue×year | 0.5746 |
| + author target stats (LOO trong fold) | 0.5771 |
| + TE + char + binary head ("I") | **0.5931** |

## Sweep 2–3 — embedding pretrained của title
| Biến thể | Score |
|---|---:|
| Chỉ MiniLM / MPNet / SPECTER (không TF-IDF, không venue) | 0.5949 / 0.5960 / 0.5958 |
| I + MPNet / I + SPECTER | 0.6082 / 0.6082 |
| I + MPNet + kNN feature | 0.6114 |
| I + gộp 3 embedding + kNN | 0.6157 |
| I + gộp 3 embedding (trọng số 2) + kNN ("V") | **0.6178** |
| Ensemble trung bình xác suất của 3 model 1-embedding | 0.6163 |

## EXP-003 — embed_v1 = cấu hình V
- **Ngày:** 2026-11-14   **Commit:** cd8f9ef   **Model:** `embed_v1` (`src/models.py::EmbedLogReg`)
- **Kết quả:** CV 0.6178 ± 0.0097 (Q 0.515, R 0.773), ngưỡng 0.55, chọn 363/596. **Public 0.64656** (+0.052 so với EXP-002; CV +0.041).
- **Tái lập:** chạy 2 lần cho file giống hệt từng byte (SHA-256 `11645f1f4e2e…`) sau khi sửa thứ tự duyệt `set` tác giả (hash randomization) và khoá BLAS 1 luồng.
- **Có nộp không?** Có, lượt #2.

## Sweep 4 — embedding lớn hơn (cấu hình V, 15 fold)
| Embedding | Score |
|---|---:|
| bge-large / e5-large / gte-large / SciNCL | 0.6090 / 0.6142 / 0.6067 / 0.6132 |
| 4 model lớn gộp | 0.6146 |
| cả 7 model gộp | 0.6158 |
| **3 model cũ (= EXP-003)** | **0.6178** |
→ Model lớn hơn không giúp; title quá ngắn.

## Sweep 5 — ablation phía dữ liệu (15 fold)
| Thay đổi | Score | Δ |
|---|---:|---:|
| TF-IDF, text gốc không clean (so với đã clean 0.5931) | 0.5919 | −0.001 |
| V, bỏ `iclp` khỏi train | 0.6139 | −0.004 |
| V, bỏ 4 dòng trùng title có nhãn mâu thuẫn | 0.6176 | −0.000 |
| V, dùng authors điền thêm của nhóm trưởng | 0.6172 | −0.001 |
→ Mọi thay đổi phía dữ liệu đều trong nhiễu (std ≈ 0.01).

## Sweep 6 — cải thiện bước chọn (ensemble head, ngưỡng theo venue, HGB)
- **Bị dừng** theo yêu cầu trước khi có kết quả. Script: `research/sweeps/sweep6.py`.

## Research 2026-11-14 — `research/analysis_exp003.py` (OOF seed 0)
Tóm tắt trong `handoff/claude/20261114-score-research.md`. Kết quả máy đọc được: `outputs/research/summary_exp003.json`.

## Research — abstract (chỉ train, 5 fold seed 0, ngưỡng trung thực) — `research/abstract_cv.py`
| Biến thể | Score | AUC |
|---|---:|---:|
| A exp003 (title) | 0.6157 ± 0.0078 | 0.788 |
| B + embedding title+abstract (MiniLM) | 0.6117 ± 0.0113 | 0.781 |
| C abstract thay embedding title (MiniLM) | 0.5920 ± 0.0131 | 0.746 |
| + title[SEP]abstract (SPECTER) | 0.6078 ± 0.0136 | 0.788 |
| SPECTER abstract thay embedding title | 0.5967 ± 0.0100 | 0.764 |
| + title+TLDR (MiniLM) | 0.6105 ± 0.0092 | 0.783 |
| TLDR thay embedding title | 0.5996 ± 0.0091 | 0.754 |
→ Abstract/TLDR không giúp.

## Research — tương tác embedding × venue — `research/venue_interaction_cv.py`
| Biến thể | Score | AUC |
|---|---:|---:|
| A exp003 | 0.6157 ± 0.0078 | 0.788 |
| + emb × venue w=1 | 0.6164 ± 0.0053 | 0.787 |
| + emb × venue w=2 | 0.6105 ± 0.0088 | 0.782 |
→ Không giúp (trong nhiễu).
