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

## EXP-004 (research) — fine-tune encoder TRONG từng fold — `research/finetune_cv.py`, `research/finetune_combine.py`
- **Ngày:** 2026-11-14 (đêm, 03:30–05:00 giờ VN). **Môi trường:** `.venv-gpu` (torch 2.15.0+cu132, RTX 3050 Laptop 4 GB),
  các gói khác cùng phiên bản `requirements.txt`. `.venv` (CPU) giữ nguyên để tái lập EXP-003.
- **Giả thuyết:** điểm mất ở bước chọn (AUC 0.788) và model tuyến tính trên embedding đóng băng đã bão hoà;
  fine-tune encoder có giám sát sẽ tăng AUC P(y>1).
- **Chống leak:** mỗi fold load lại checkpoint pretrained và fine-tune **chỉ trên phần train của fold**; fold validation đóng vai test.
- **Protocol:** folds của `src/validation.py`, chấm bài không thuộc `iclp`, ngưỡng chọn trung thực (chọn trên các fold còn lại cùng seed,
  lưới 0.30–0.80 bước 0.025). Δ là chênh lệch **ghép cặp** từng fold so với A = exp003 (cùng fold, cùng cách chọn ngưỡng).
- **Phương pháp:** input `"<venue> <year>: <title>"`; CE = encoder + head tuyến tính, BCE trên y>1, 4 epoch, lr 2e-5 (head 1e-3), batch 32;
  CE5 = head 5 lớp, softmax CE trên nhãn 1..5 (cho cả P(y>1) và E[gain]); SF = SetFit (cặp contrastive theo y>1, CosineSimilarityLoss) + logistic head.
  Ghép: P(y>1) = sigmoid(trung bình logit); thứ tự = trung bình E[gain].
- **Tốc độ:** GPU nhanh hơn CPU ~15–30 lần (SetFit 1.6 → 0.054 s/bước; CE 0.69 → 0.046 s/bước). Một fold MiniLM (SF+CE) ~95 s.

### Seed 0 (5 fold) — từng thành phần (A = 0.6157 ± 0.0078, AUC 0.788)
| Biến thể | AUC | Score | Δ |
|---|---:|---:|---:|
| F0 MiniLM đóng băng + logistic head (tham chiếu) | 0.732 | 0.5940 | −0.022 |
| SF MiniLM 10 vòng / A+SF | 0.755 / 0.796 | 0.6191 / 0.6199 | +0.003 / +0.004 |
| SF 1 vòng, 2 vòng (A+SF) | 0.790 / 0.792 | 0.6155 / 0.6164 | −0.000 / +0.001 |
| CE MiniLM 2 / 4 / 8 epoch (A+CE) | 0.796 / 0.800 / 0.801 | 0.6180 / 0.6214 / 0.6232 | +0.002 / +0.006 / +0.008 |
| CE MiniLM không tiền tố venue/year (A+CE) | 0.802 | 0.6215 | +0.006 |
| CE riêng MiniLM / MPNet / SPECTER / SciNCL | 0.788 / 0.795 / 0.786 / 0.786 | 0.6216 / 0.6216 / 0.6155 / 0.6144 | +0.006 / +0.006 / −0.000 / −0.001 |
| A+CE MiniLM / MPNet / SPECTER / SciNCL | 0.800 / 0.805 / 0.801 / 0.801 | 0.6214 / 0.6222 / 0.6186 / 0.6241 | +0.006 / +0.007 / +0.003 / +0.008 |
| A+CE5 MiniLM / MPNet | 0.801 / 0.800 | 0.6137 / 0.6237 | −0.002 / +0.008 |
| Chỉ đổi thứ tự: eg trung bình A + CE5 (MiniLM / MPNet) | 0.788 | 0.6180 / 0.6178 | +0.002 / +0.002 |
| A[CE] / A[SF]: thay khối embedding trong exp003 bằng embedding đã fine-tune | 0.76–0.79 | 0.611–0.619 | −0.004…+0.003 |
→ CE tốt hơn SetFit; SetFit nhiễu và không ổn định theo số vòng. Thay embedding trong exp003 không giúp (feature train bị tách quá mức).
→ Score theo fold nhiễu hơn AUC nhiều: hai biến thể cùng AUC 0.801 có thể lệch 0.008 Score.

### Seed 0 — tổ hợp (`research/finetune_combine.py`)
| Tổ hợp | AUC | Score | Δ (SE), số fold tốt hơn |
|---|---:|---:|---:|
| A + 3 CE (MiniLM, MPNet, SPECTER) | 0.808 | 0.6228 | +0.007 (0.001), 5/5 |
| 3 CE, không A | 0.805 | 0.6260 | +0.010 (0.001), 5/5 |
| Chỉ thứ tự: eg = trung bình A + CE5 MiniLM + CE5 MPNet | 0.788 | 0.6183 | +0.003 (0.0005), 5/5 |
| **C1:** A + 3 CE, eg trung bình | 0.808 | 0.6253 | +0.010 (0.002), 5/5 |
| **C2:** 3 CE (không A), eg trung bình | 0.805 | 0.6305 | +0.015 (0.002), 5/5 |
| C1 với 4 CE (+SciNCL) | 0.809 | 0.6312 | +0.016 (0.003), 5/5 |
| C2 với 4 CE (+SciNCL) | 0.806 | 0.6276 | +0.012 (0.003), 5/5 |
→ C1 và C2 đổi chỗ cho nhau khi thêm/bớt một encoder: chênh lệch giữa chúng là nhiễu (±0.005). Đây là tổ hợp tốt nhất trong nhiều
tổ hợp thử trên seed 0, nên **lạc quan**; C1/C2 được chốt trước khi chạy seed 1–2 để xác nhận.

### Xác nhận seed 1–2 (10 fold mới), cấu hình chốt trước: CE 4 epoch cho 4 encoder, CE5 cho MiniLM/MPNet
A (seed 1–2) = 0.6179, AUC 0.791.
| Thành phần | A+CE AUC | A+CE Δ (seed 1–2) | Δ seed 0 |
|---|---:|---:|---:|
| MiniLM | 0.807 | +0.0060 | +0.0057 |
| MPNet | 0.802 | +0.0064 | +0.0065 |
| SPECTER | 0.802 | +0.0088 | +0.0029 |
| SciNCL | 0.807 | +0.0071 | +0.0084 |
| Chỉ thứ tự (eg + CE5 MiniLM / MPNet) | 0.791 | +0.0000 / +0.0009 | +0.0023 / +0.0021 |
→ Bước chọn: cải thiện **lặp lại** trên seed mới. Bước thứ tự (CE5): gần 0, không xác nhận được.

### 15 fold (seed 0, 1, 2) — `research/finetune_combine.py`, A = 0.6172 (ngưỡng trung thực), AUC 0.790
| Tổ hợp | AUC | Score | Δ paired (SE), fold tốt hơn |
|---|---:|---:|---:|
| A + 4 CE | 0.810 | 0.6296 | +0.0124 (0.0021), 15/15 |
| **C1 = A + 4 CE, eg trung bình A + CE5 MiniLM + CE5 MPNet** | **0.810** | **0.6307** | **+0.0135 (0.0022), 15/15** |
| C2 = 4 CE (không A), eg trung bình | 0.808 | 0.6280 | +0.0108 (0.0023), 13/15 |
| Chỉ thứ tự (eg trung bình) | 0.790 | 0.6183 | +0.0011 (0.0004), 12/15 |
| C1 + bagging (mỗi encoder thêm 1 lần fine-tune seed khác) | 0.8105 | 0.6277 | +0.0105 (0.0018), 14/15 |
→ Bagging không giúp (AUC bão hoà ~0.81). Chọn **C1 không bagging = model `ft_ens_v1`**.

Theo đúng quy trình của `run_experiment.py` (ngưỡng chọn trên chính 15 fold, lưới 0.05) áp lên OOF research
(`scripts/finalize_from_oof.py`): **A = 0.6178 ± 0.0097 (trùng khít EXP-003)**; `ft_ens_v1` = **0.6302 ± 0.0091** (Q 0.523, R 0.796),
ngưỡng 0.60, **Δ +0.0123**; bản bagging 0.6306 ± 0.0084. Chưa đạt mức +0.015 đặt ra ban đầu; sinh viên đồng ý vẫn đề cử bản tốt nhất.

## EXP-004 — `ft_ens_v1` = C1 (model production)
- **Ngày:** 2026-11-14 (05:20 giờ VN)   **Model:** `ft_ens_v1` (`src/models.py::FineTuneEnsemble`, huấn luyện ở `src/finetune.py`)
- **Lệnh:** `.venv-gpu\Scripts\python.exe -m scripts.finalize_from_oof --model ft_ens_v1 --name exp004_ft_ens_v1 --parity`
  (CV lấy từ OOF research 15 fold, chọn ngưỡng đúng như `run_experiment.py`; fit cuối trên toàn train bằng code production).
- **Thành phần:** chọn bài = sigmoid(trung bình logit) của exp003 (binary head) + CE fine-tune của MiniLM, MPNet, SPECTER, SciNCL;
  thứ tự = trung bình E[gain] của exp003 + CE5 MiniLM + CE5 MPNet. Mỗi fit = 1 logistic exp003 + 6 lần fine-tune (~4 phút trên RTX 3050).
- **Kết quả:** CV **0.6302 ± 0.0091** (Q 0.523, R 0.796), ngưỡng 0.60; EXP-003 cùng quy trình 0.6178 ± 0.0097 → **+0.0123**.
  AUC P(y>1) 0.790 → 0.810. Paired honest: +0.0135 (SE 0.0022), tốt hơn ở 15/15 fold.
- **Parity code production và code research** (seed 0, fold 0): AUC 0.815 = 0.815, Score 0.6282 = 0.6282, tương quan pb = 1.0.
- **Test:** chọn 353/596 (cav 118, kr 115, lics 84, lpnmr 36); mean pb 0.635. So với EXP-003: cùng chọn 311, bỏ 52, thêm 42;
  Spearman thứ tự trong phần chung 0.913.
- **File:** `submissions/exp004_ft_ens_v1.csv`, SHA-256 `a89e78ee4b4f…`, validator VALID. `outputs/exp004_ft_ens_v1/report.json`.
- **Có nộp không?** Có, lượt #3 (sinh viên tự nộp, 2026-11-13 22:24 UTC). **Public 0.66918** (EXP-003: 0.64656; +0.0226),
  hạng 8 lúc nộp. CV lệch LB +0.039 (EXP-003: +0.029); Public chỉ 298 bài, std ~0.015–0.02, nên mức tăng Public lớn hơn CV là bình thường.
- **Phương pháp đã học (FR-04):** classification. Fine-tune encoder là phần mở rộng ngoài môn, cần trích dẫn: sentence-transformers
  (Reimers & Gurevych, 2019), SetFit (Tunstall et al., 2022, đã thử, không dùng), các checkpoint HF trong `src/embeddings.py`.
