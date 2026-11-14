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

## Sau EXP-004 — phiên 2 (2026-11-14 tối), theo `handoff/claude/20261114-score-plan.md`
- **Mốc so sánh:** **EXP-004** (`ft_ens_v1`), ghép cặp trên cùng (seed, fold). Công cụ mới `research/ens_compare.py` báo hai con số:
  *honest* (ngưỡng chọn trên các fold còn lại cùng seed, lưới 0.30–0.80 bước 0.025) và *run_exp* (đúng quy trình đã cho EXP-004 0.6302:
  một ngưỡng cho cả 15 fold, lưới 0.05). Kiểm tra công cụ: EXP-004 tái tạo **honest 0.6307, run_exp 0.6302 ± 0.0091, t = 0.60**; bagging tái tạo run_exp 0.6306.
- **Tiêu chí nộp (sinh viên quyết, 2026-11-14 tối):** "chỉ cần tốt hơn lần trước". Agent áp dụng: trên 15 fold, **cả** Δ honest ghép cặp **và**
  Δ run_exp so với EXP-004 đều > 0 (một mình mỗi thước đo có thể đổi dấu ở mức ±0.003, ví dụ bagging: honest −0.003, run_exp +0.0004).

### P1a/P1b — stacking, calibration và thứ tự (`research/stack_cv.py`, chỉ dùng OOF có sẵn, không train lại encoder)
- Biến thể khai báo trước trong docstring. Stacker = logistic regression fit **lồng**: với (seed s, fold k) fit trên OOF của 4 fold còn lại cùng seed.
- `pm` (P(y>1) của head multinomial exp003) được tính lại cho 15 fold: `outputs/research/oof_A5_s*_f*.pkl`, khớp cache (max|Δ| 3e-7).

| Biến thể | AUC | Δ honest seed 0 | Δ honest seed 1–2 | Δ honest 15 fold (SE), fold tốt hơn | Δ run_exp |
|---|---:|---:|---:|---:|---:|
| ST1: LR trên 5 logit (A + 4 CE) | 0.8099 | −0.0079 | −0.0019 | −0.0039 (0.0015), 3/15 | −0.0024 |
| ST2: ST1 + logit P(y>1) của 2 CE5 | 0.8103 | −0.0047 | −0.0053 | −0.0051 (0.0011), 2/15 | −0.0028 |
| ST3: ST1 + one-hot venue | 0.8072 | −0.0086 | −0.0050 | −0.0062 (0.0016), 3/15 | −0.0030 |
| O1: thứ tự = pb_EXP004 × trung bình E[gain \| y>1] (A, CE5×2) | 0.8101 | −0.0003 | +0.0001 | −0.0000 (0.0002), 7/15 | −0.0000 |
| O2: thứ tự = pb_EXP004 × E_A[gain \| y>1] | 0.8101 | −0.0023 | −0.0004 | −0.0010 (0.0004), 2/15 | −0.0010 |
| O1/O2 với pb của ST1–3 | | −0.005…−0.011 | −0.002…−0.006 | | |
- Stacker đúng là sửa calibration (mean pb 0.648 → 0.614 = tỉ lệ thật) và học trọng số (trung bình: A 0.25, MiniLM 0.21, SciNCL 0.13, MPNet 0.09,
  SPECTER 0.07; tổng 0.75 < 1, tức "hạ nhiệt"), nhưng **Score giảm**. Lý do khả dĩ: ngưỡng đã được tune nên calibration không đem lại gì,
  còn trọng số fit riêng từng fold thêm phương sai.
- → **P1 âm hoặc bằng 0. Giữ trung bình logit trọng số đều và thứ tự của EXP-004.** Không lặp lại.

### P2a — thêm encoder CE (`research/queue_p2a_s0.txt`, rồi `queue_p2a_s12.txt`), cùng công thức CE với EXP-004
- 7 checkpoint mới (thêm vào `src/embeddings.py::MODELS`): `e5_base` (intfloat/e5-base-v2, tiền tố "query: "), `bge_base`
  (BAAI/bge-base-en-v1.5), `gte_base` (thenlper/gte-base), `specter2` (allenai/specter2_base), `scibert` (allenai/scibert_scivocab_uncased),
  `minilm_l12` (all-MiniLM-L12-v2), `distilroberta` (all-distilroberta-v1). Tiền tố e5 được thêm cả ở `src/finetune.py` (parity production).
- **Quy tắc chốt lúc 20:06**, khi mới có seed 0 của 2/7 encoder và chưa có kết quả seed 1–2 nào: chạy seed 1–2 cho **cả 7** encoder
  (không bước chọn nào quyết định việc chạy). Hai ứng viên: **C_all** = EXP-004 + 7 encoder; **C_sel** = EXP-004 + các encoder có Δ seed 0 > 0.

Seed 0, từng encoder (A = exp003; Δ so với A, giống bảng EXP-004) và khi thêm vào EXP-004 (Δ ghép cặp honest so với **EXP-004**):
| Encoder | F0 (đóng băng) AUC | CE AUC | A+CE AUC | A+CE Δ vs A | EXP-004 + enc: AUC | Δ vs EXP-004, fold tốt hơn |
|---|---:|---:|---:|---:|---:|---:|
| (EXP-004 dùng) MiniLM / MPNet / SPECTER / SciNCL | 0.73–0.74 | 0.786–0.795 | 0.800–0.805 | +0.003…+0.008 | (0.8085) | — |
| e5_base | 0.778 | 0.794 | 0.805 | +0.0085 | 0.8098 | −0.0010, 1/5 |
| bge_base | 0.767 | 0.790 | 0.801 | +0.0024 | 0.8087 | −0.0027, 1/5 |
| gte_base | 0.759 | 0.785 | 0.799 | +0.0002 | 0.8082 | −0.0037, 0/5 |
| specter2 | 0.777 | 0.800 | 0.809 | +0.0053 | 0.8105 | **+0.0019, 4/5** |
| minilm_l12 | 0.724 | 0.791 | 0.802 | +0.0044 | 0.8088 | −0.0016, 3/5 |
| distilroberta | 0.751 | 0.804 | 0.810 | +0.0030 | 0.8118 | −0.0024, 1/5 |
| scibert | 0.783 | 0.797 | 0.808 | +0.0006 | 0.8105 | **+0.0006, 3/5** |
| C_all (EXP-004 + 7) | | | | | 0.8124 | −0.0027, 2/5 |
→ Theo quy tắc: **C_sel = EXP-004 + specter2 + scibert**. Từng encoder mới ngang hoặc hơn 4 encoder cũ, nhưng thêm vào ensemble thì gần như không đổi
(AUC +0.000…+0.004, Score trong nhiễu): **bão hoà**. Thời gian CE: ~30 s/fold (base), ~16 s/fold (MiniLM-L12, DistilRoBERTa).

### P2b — input / siêu tham số CE (seed 0, `research/queue_p2bc_s0.txt`); P2c — fine-tune với abstract (chỉ train)
Cờ mới của `research/finetune_cv.py`: `--text {title,authors,abstract,tldr}`, `--max-len`, `--freeze-below`. Mặc định giữ nguyên EXP-004.
| Biến thể (seed 0) | F0 AUC | CE AUC | A+CE Δ vs A | Thay vào EXP-004: Δ vs EXP-004 | Thêm vào EXP-004: Δ |
|---|---:|---:|---:|---:|---:|
| MiniLM, text + `" \| authors"` | 0.721 | 0.779 (title: 0.788) | +0.0037 | −0.0020, 2/5 | −0.0011, 2/5 |
| MPNet, lr 5e-5 (gốc 2e-5) | 0.736 | 0.792 (gốc 0.795) | +0.0027 | −0.0020, 2/5 | −0.0041, 1/5 |
| **P2c** MiniLM, title + abstract (fallback TLDR), max 256 token | 0.689 | **0.745** | −0.0012 | −0.0044, 1/5 | −0.0023, 1/5 |
| MPNet + authors / + abstract (256) | CUDA OOM trên 4 GB → chạy lại max 128 token (`queue_p2bc_rerun.txt`) | | | | |
→ Authors trong text và lr cao hơn: kém hơn. **Abstract làm CE kém hẳn** (AUC 0.788 → 0.745), khớp kết quả với embedding đóng băng:
**không có lý do để xin Q-07 cho abstract.** (Đo chỉ trên train; test không dùng dữ liệu ngoài.)

#### P2a — xác nhận seed 1–2 (cả 7 encoder, 10 fold mới) và 15 fold — `outputs/research/ens_compare_p2a_*.json`
| Cấu hình | AUC 15 fold | Δ honest seed 1–2 (fold tốt hơn) | Δ honest 15 fold (SE), fold tốt hơn | Δ run_exp (CV, t) |
|---|---:|---:|---:|---:|
| EXP-004 (mốc) | 0.8101 | — | — | 0.6302 ± 0.0091, t 0.60 |
| **C_sel** = EXP-004 + specter2 + scibert (chọn trên seed 0) | 0.8125 | **−0.0020 (3/10)** | −0.0008 (0.0009), 7/15 | −0.0000 |
| **C_all** = EXP-004 + 7 encoder | 0.8141 | **−0.0009 (4/10)** | −0.0015 (0.0014), 6/15 | +0.0005 (0.6306 ± 0.0090) |
| từng encoder thêm vào EXP-004 (15 fold) | 0.8100–0.8133 | −0.0011…+0.0002 | −0.0018…+0.0008 | −0.0002…+0.0010 |
→ **Không ứng viên nào đạt tiêu chí** (cần cả Δ honest và Δ run_exp > 0). C_sel được chọn trên seed 0 (+0.0016) nhưng âm trên seed 1–2: đúng kiểu chọn theo nhiễu.
AUC tăng tới +0.004 nhưng Score không tăng: ở mức AUC 0.81, thêm encoder chỉ title **không còn chuyển thành điểm**. Hướng P2a đóng lại.

### P3a-lite — encoder lớn, chỉ fine-tune 8 lớp trên (không cần `peft`), seed 0 — `research/queue_p2bc_rerun.txt`
- `--freeze-below 16`: embeddings + 16/24 lớp dưới đóng băng và **lưu ở bf16** (lần đầu để fp32 thì CUDA OOM trên 4 GB), 8 lớp trên + head
  train như CE. Khoảng 44 s/fold.
| Encoder | F0 AUC | CE AUC | A+CE Δ vs A | Thêm vào EXP-004: AUC, Δ honest (fold tốt hơn) |
|---|---:|---:|---:|---:|
| e5-large-v2, top 8 | 0.764 | 0.792 (fold 0: 0.826, các fold khác 0.775–0.793) | +0.0025 | 0.8092, −0.0043 (1/5) |
| bge-large-en-v1.5, top 8 | 0.758 | 0.789 | +0.0036 | 0.8090, −0.0042 (0/5) |
| cả hai | | | | 0.8093, −0.0002 (2/5) |
→ Không hơn encoder cỡ base. Đóng hướng. (MPNet + authors / + abstract: OOM cả ở 128 token với batch 32; không chạy lại vì bản MiniLM đã âm rõ.)

### `doi` làm feature — `research/doi_feature_cv.py` (CPU, sklearn)
- `doi` chưa từng được dùng làm feature. Feature: one-hot "series" = prefix DOI + chữ đầu hậu tố (vd. `10.4204/eptcs`, `10.24963/kr`,
  `10.1109/lics`), hoặc `s2_url` / `ceur` / `other_url`; nhóm có < 5 bài trong fold train bị bỏ. **Không** dùng số trong hậu tố
  (vị trí bài trong tập kỷ yếu, gần với artifact `id` của Q-10).
- Train: trong cùng venue, tỉ lệ y>1 khác nhau vừa phải (cav: 10.1109 0.69 (n 42), 10.1007 0.53, EPTCS 0.29 (n 14), ceur 0.11 (n 9));
  lics 10.1109/10.1145 gần như trùng với năm.
| Biến thể | AUC | Δ honest seed 0 | Δ honest seed 1–2 | Δ honest 15 fold, fold tốt hơn | Δ run_exp |
|---|---:|---:|---:|---:|---:|
| A' = exp003 + doi series, so với A | 0.7914 (A 0.7901) | −0.0016 | −0.0012 | −0.0013, 6/15 | −0.0007 |
| EXP-004 với A' thay A, so với EXP-004 | 0.8106 | +0.0002 | −0.0006 | −0.0003, 6/15 | +0.0003 |
→ Trong nhiễu, không đạt tiêu chí. Đóng hướng.

### Phân tích lỗi EXP-004 theo venue (OOF 15 fold, ngưỡng 0.60) — chất liệu cho phần Insights
| Venue | Bài/seed | Tỉ lệ y>1 | AUC A → EXP-004 | Tỉ lệ chọn | Precision | Recall | Spearman thứ tự trong phần chọn |
|---|---:|---:|---:|---:|---:|---:|---:|
| cav | 657 | 0.543 | 0.780 → 0.792 | 0.507 | 0.760 | 0.710 | 0.55 |
| kr | 661 | 0.732 | 0.773 → 0.796 | 0.794 | 0.829 | 0.899 | 0.46 |
| lics | 604 | 0.523 | 0.724 → **0.762** | 0.492 | 0.731 | 0.688 | 0.45 |
| lpnmr | 116 | 0.819 | 0.890 → 0.914 | 0.853 | 0.909 | 0.947 | 0.71 |
→ lics vẫn khó nhất nhưng là venue fine-tune giúp nhiều nhất (+0.038 AUC).
**Khoảng trống (cùng tập chọn của EXP-004):** thứ tự hoàn hảo +0.019; thứ tự ngẫu nhiên −0.053; chọn hoàn hảo +0.111.
Thứ tự hiện tại đã lấy ~74% đòn bẩy thứ tự; nút thắt là bước chọn (AUC 0.81).

### Thứ tự: thêm CE5 (`research/queue_ce5_more_s0.txt`), seed 0
- Một ứng viên khai báo trước (20:35): thứ tự = trung bình E[gain] của A + CE5 của MiniLM, MPNet (như EXP-004) **và** SPECTER, SciNCL,
  specter2, e5_base; chọn bài giữ nguyên pb của EXP-004.
| Biến thể (seed 0) | Δ honest vs EXP-004 (SE), fold tốt hơn |
|---|---:|
| + CE5 SPECTER / SciNCL / specter2 / e5_base (từng cái) | −0.0006 / +0.0004 / +0.0004 / +0.0000 |
| **Ứng viên: + cả 4** | **+0.0001 (0.0003), 3/5** |
→ Bằng 0, nên không chạy xác nhận seed 1–2 (xác nhận một tín hiệu bằng 0 chỉ có thể sinh "cải thiện" do nhiễu). Thứ tự cũng đã bão hoà với ensemble CE5.

### Kết luận phiên 2 (2026-11-14 tối)
- **Không có ứng viên nào tốt hơn EXP-004** theo tiêu chí đã chốt. Không tạo file nộp mới. EXP-004 vẫn là bản tốt nhất (CV 0.6302, Public 0.66918).
- Bằng chứng nhất quán: với thông tin hiện có (title, venue, year, authors, doi), bước chọn bài kẹt ở **AUC ≈ 0.81**.
  Thêm encoder (7 base + 2 large), stacking, đổi input/siêu tham số, thêm feature `doi` đều cho AUC +0.000…+0.004 và Score trong nhiễu (|Δ| ≤ 0.002).
  Thứ tự đã lấy ~74% đòn bẩy và cũng bão hoà.
- GPU dùng khoảng 1 giờ 30 phút (19:57–21:27). Powercfg đã được trả về như cũ lúc 21:30.

### Metadata Semantic Scholar (citation count, publicationTypes) — CHỈ TRAIN, để quyết định có hỏi Q-07 không — `research/citation_signal_cv.py`
- Dữ liệu: `data/external/s2_train.jsonl` (2266/2469 bài train có citationCount). Test không có và không được lấy khi Q-07 chưa trả lời.
- Feature thêm vào exp003: log1p(citations), cờ thiếu, log1p(citations) trừ trung bình cùng năm (fold-train), one-hot publicationTypes.
| Biến thể | AUC | Δ honest seed 0 / seed 1–2 | Δ honest 15 fold, fold tốt hơn | Δ run_exp |
|---|---:|---:|---:|---:|
| A' = exp003 + metadata S2, so với A | 0.7898 (A 0.7901) | −0.0042 / −0.0027 | −0.0032, 4/15 | −0.0013 |
| EXP-004 với A' thay A | 0.8103 | +0.0004 / +0.0015 | +0.0011, 9/15 | −0.0003 |
→ AUC không đổi: nhãn **không** phản ánh mức trích dẫn. Không có lý do hỏi Q-07 cho metadata S2 (cùng kết luận với abstract).
