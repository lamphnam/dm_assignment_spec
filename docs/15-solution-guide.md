# 15 — Lời giải của chủ repo (EXP-001…004): hướng dẫn chạy và cải tiến cho thành viên nhóm

Tài liệu này dành cho **thành viên nhóm** (và agent của họ) nhận được bản code này để **chạy thử và cố gắng cải tiến điểm**.
Phần còn lại của `docs/` là dữ kiện và luật; file này là bản đồ cho lời giải đã có.

> **Chia sẻ:** code, OOF và file nộp chủ yếu dành cho 5 thành viên (Q-14, [14](14-compliance-and-distribution.md)). Chủ repo đã chấp nhận rủi ro khi đẩy code lên GitHub;
> dù vậy **dữ liệu competition (`data/`, `leader_csv_file/`) và credentials không bao giờ nằm trong git** (license CC BY-NC-SA, Kaggle rules §5d, §6a).
> Mỗi người tự tải dữ liệu bằng tài khoản Kaggle của mình. Nếu muốn đóng repo lại thì chuyển sang private trong Settings của GitHub.

## 1. Hiện trạng (tính đến 2026-11-14)

| EXP | Cách làm | CV (15 fold, mean ± std) | Public | Nộp |
|---|---|---:|---:|---|
| EXP-001 | Điểm trung bình theo venue (baseline) | 0.5247 ± 0.0125 | — | không |
| EXP-002 | TF-IDF title + venue + year + authors, logistic regression | 0.5768 ± 0.0111 | 0.59467 | #1 |
| EXP-003 | Embedding pretrained đóng băng (MiniLM, MPNet, SPECTER) + kNN + TF-IDF, logistic regression | 0.6178 ± 0.0097 | 0.64656 | #2 |
| **EXP-004** | **EXP-003 + 4 encoder fine-tune có giám sát trong từng fold** (MiniLM, MPNet, SPECTER, SciNCL), ngưỡng 0.60 | **0.6302 ± 0.0091** | **0.66918** | #3 |

- Mốc cùng protocol: random chọn hết 0.4957; oracle chọn hết + thứ tự đúng 0.5905; oracle bỏ label 1 + thứ tự đúng 0.7579.
- **Đừng tin Public quá:** test 298 bài, std ~0.015–0.02; Public cao hơn CV khoảng 0.03–0.04. Ước lượng Private ≈ CV ≈ 0.63.
- Nhật ký đầy đủ (kể cả hướng thất bại): [experiments/EXPERIMENTS.md](../experiments/EXPERIMENTS.md). Nhật ký nộp: [submissions/LOG.md](../submissions/LOG.md).
  Bàn giao chi tiết: [handoff/claude/20261114-score-session2.md](../handoff/claude/20261114-score-session2.md).

### Điểm đang kẹt ở đâu (đọc trước khi thử ý tưởng)
- Điểm bị mất chủ yếu ở **bước chọn bài** (P(label>1), AUC ≈ 0.81), không phải ở thứ tự. Thứ tự hoàn hảo chỉ cộng thêm ~+0.019; chọn hoàn hảo cộng ~+0.111.
- Đã thử và **không giúp** (Δ so với EXP-004 từ −0.006 đến +0.001, trong mức nhiễu): stacking/calibration, thêm 7 encoder base, authors/abstract làm input,
  encoder large (e5/bge-large, chỉ train 8 lớp trên), feature `doi`, metadata Semantic Scholar, bagging, SetFit, CE5 cho thứ tự.
  Chi tiết bảng ở mục "Sau EXP-004 — phiên 2" của EXPERIMENTS.md. Đừng chạy lại những hướng này.
- Hai đòn bẩy còn lại cần giảng viên cho phép: Q-10 (dùng `id`/thứ tự trong (venue, year)) và học transductive trên title của test ([13](13-risks-open-questions.md)).
- Nhiều biến thể đã thử trên cùng 15 fold: một ứng viên "+0.001" gần như chắc chắn là nhiễu (SE ghép cặp ~0.001).

## 2. Cấu trúc code

```text
src/            code dùng chung (pipeline nộp bài)
  data.py         đọc train/Test (parser Test.csv), kiểm checksum, chuẩn hoá text
  validation.py   protocol cố định: StratifiedGroupKFold 5 fold × seeds 0,1,2 = 15 fold, chấm bài không thuộc iclp
  metric.py       scorer (dùng lại tools/score.py, đã qua T1–T9)
  embeddings.py   embedding pretrained, cache trong data/interim/
  models.py       VenueMean, LogRegText, EmbedLogReg (exp003), FineTuneEnsemble (ft_ens_v1)
  finetune.py     FineTunedEncoder (fine-tune CE, tất định, cần GPU)
scripts/
  check_data.py          kiểm checksum dữ liệu
  run_experiment.py      CV 15 fold + fit toàn bộ train + sinh submissions/<name>.csv + outputs/<name>/report.json
  finalize_from_oof.py   như trên nhưng lấy CV từ OOF có sẵn (không chạy lại CV fine-tune)
research/       phân tích và sweep (không phải pipeline nộp bài), xem research/README.md
experiments/    EXPERIMENTS.md: nhật ký thí nghiệm
submissions/    CSV đã nộp (giữ nguyên từng byte) + LOG.md
outputs/        report.json của EXP-001…004, JSON tóm tắt các sweep; một phần OOF (xem §5)
tools/          scorer, validator, inspect_data (tham chiếu)
```

## 3. Cài môi trường

Môi trường gốc: Windows 11, Python 3.14.5, RTX 3050 Laptop 4 GB. Chưa thử ở Python/OS khác; nếu cài lỗi, thử Python 3.12 và ghi lại phiên bản.

```powershell
# CPU (đủ cho EXP-001…003, tools, và các script research chạy trên OOF)
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# GPU (cần cho fine-tune, tức EXP-004 từ đầu); cần driver NVIDIA đủ mới cho CUDA 13.2, xem ghi chú trong file
python -m venv .venv-gpu
.\.venv-gpu\Scripts\python.exe -m pip install -r requirements-gpu.txt
.\.venv-gpu\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available())"
```

Hai venv chỉ khác bản torch. Nếu chỉ muốn thử ý tưởng dựa trên OOF có sẵn thì **không cần GPU** (xem §5).
Không có GPU: fine-tune một encoder cho cả 15 fold mất vài chục giờ CPU, nên không khả thi; hãy làm việc trên OOF hoặc trên `src/models.py` với embedding đóng băng.

## 4. Tải dữ liệu và kiểm tra

Tham gia competition và accept rules bằng **tài khoản Kaggle của bạn**, rồi theo [10 §3](10-development-guide.md#3-tải-dữ-liệu) để tải vào `data/raw/`
(`data/` bị gitignore). Sau đó:

```powershell
.\.venv\Scripts\python.exe -m scripts.check_data          # SHA-256 phải khớp docs/05 §1
python -I tools/score.py selftest                         # ALL PASS
python -I tools/inspect_data.py data/raw                  # 48 check, 0 FAIL
```

Không commit token Kaggle. Đặt qua biến môi trường hoặc file `%USERPROFILE%\.kaggle\access_token` (ngoài repo).

## 5. Chạy lại

### 5a. Không GPU, vài phút: đối chiếu với EXP-004

Repo có sẵn 10 file OOF của các thành phần EXP-004 (`outputs/research/finetune_{minilm,minilm_s12,minilm_ce5,mpnet_ce,mpnet_s12,mpnet_ce5,specter_ce,specter_s12,scincl_ce,scincl_s12}_oof.pkl`, tổng 11.5 MB)
và `outputs/exp004_ft_ens_v1/test_predictions.npz`.

```powershell
# Tái tạo con số CV của EXP-004 từ OOF, kỳ vọng: honest 0.6307, run_exp 0.6302 ± 0.0091
.\.venv\Scripts\python.exe -m research.ens_compare
# So ghép cặp một biến thể với EXP-004 (ví dụ thêm một thành phần CE đã có OOF)
.\.venv\Scripts\python.exe -m research.ens_compare add=finetune_e5_base_ce:CE seeds=0
```

Các OOF khác của sweep (≈100 file, ~40 MB) **không** nằm trong git: hỏi chủ repo (gửi file zip của `outputs/research/*.pkl`) hoặc tự sinh lại (§5c).

### 5b. CPU: EXP-001…003 (từ đầu)

```powershell
.\.venv\Scripts\python.exe -m scripts.run_experiment --model venue_mean  --name exp001_venue_mean
.\.venv\Scripts\python.exe -m scripts.run_experiment --model logreg_text --name exp002_logreg_text
.\.venv\Scripts\python.exe -m scripts.run_experiment --model embed_v1    --name exp003_embed_v1
```

`embed_v1` tính embedding lần đầu (cần tải model từ HuggingFace, vài chục phút CPU) rồi cache vào `data/interim/`.
Kỳ vọng: CV 0.5247 / 0.5768 / 0.6178. EXP-003 tái lập từng byte (SHA-256 `11645f1f4e2e…`) trên máy gốc; máy khác có thể lệch nhỏ.
Nhớ `--name` mới (ví dụ `exp005_<ý_tưởng>`) khi thử ý tưởng của bạn để không ghi đè `submissions/` của người khác.

### 5c. GPU: fine-tune lại các thành phần EXP-004

```powershell
# Một thành phần (ví dụ MiniLM, cả 15 fold)
.\.venv-gpu\Scripts\python.exe -m research.finetune_cv --enc minilm --methods ce
# Cả hàng đợi (ghi log vào outputs/logs/, OOF vào outputs/research/); Git Bash
bash research/finetune_queue.sh research/queue_confirm_s12.txt
```

Toàn bộ hàng đợi EXP-004 mất ~75 phút – 1.5 giờ GPU trên RTX 3050 4 GB. VRAM 4 GB: MPNet batch 32 với input ≥128 token bị OOM; encoder large cần `--freeze-below`.
Sau đó sinh file nộp:

```powershell
.\.venv-gpu\Scripts\python.exe -m scripts.finalize_from_oof --model ft_ens_v1 --name exp004_repro --sub-dir outputs/exp004_repro
```

Kỳ vọng: SHA-256 CSV `a89e78ee4b4f…` trên máy gốc. GPU/driver khác có thể lệch nhỏ, kết quả không bảo đảm trùng từng byte.

## 6. Quy trình thử ý tưởng (để so sánh được với nhau)

1. **Giữ nguyên protocol** `src/validation.py` (15 fold, chấm bài không thuộc `iclp`) và scorer `src/metric.py`. Không đổi, vì mọi số trong EXPERIMENTS.md dựa trên đó.
2. **Fine-tune hay fit mọi thứ chỉ trong train của fold** (fold validation đóng vai test). Không dùng `id` làm feature (Q-10 chưa trả lời), không dùng nhãn test,
   không pseudo-label. Dữ liệu ngoài phải công khai nguồn (NFR-06); dữ liệu ngoài cho test cần Q-07.
3. **So ghép cặp với EXP-004** từng fold (`research/ens_compare.py` làm sẵn): báo Δ, SE và số fold tốt hơn. Sàng lọc trên seed 0 rồi **xác nhận trên seed 1–2** với cấu hình chốt trước;
   chọn theo nhiễu là bẫy chính ở bài này.
4. Ghi mục mới vào [experiments/EXPERIMENTS.md](../experiments/EXPERIMENTS.md) (kể cả kết quả âm).
5. Skill hữu ích: `independent-experiment`, `experiment-comparison`, `validation-and-scoring`.

## 7. Nộp bài (quan trọng cho cả nhóm)

- **Mỗi người nộp bằng tài khoản Kaggle riêng**, tự nộp (agent không nộp). Quota 3 lượt/ngày/team.
- **Đừng nộp lại file có sẵn trong `submissions/`** (đã nộp rồi, tốn lượt vô ích). Chỉ nộp ứng viên mới có bằng chứng CV tốt hơn EXP-004 vượt nhiễu.
- Cuối kỳ cả nhóm join team của người điểm cao nhất; gộp chỉ thành công nếu **tổng submission của cả nhóm** dưới trần ([14](14-compliance-and-distribution.md#gộp-team-cuối-kỳ-điều-kiện-của-kaggle)).
  Đừng dùng hết quota. Hiện chủ repo đã dùng 3 lượt.
- Trước khi nộp: `python -I tools/validate_submission.py <csv> --test data/raw/Test.csv`; ghi vào `submissions/LOG.md` của bản clone của bạn (skill `submission-management`).

## 8. Làm việc với repo này như một nhóm

- Docs gốc nói "mỗi người một bản clone, không push ngược". Với repo này, hai cách hợp lý: (a) mỗi bạn clone rồi làm trên **branch riêng**, kết quả tốt thì gửi lại diff/branch cho chủ repo;
  hoặc (b) tạo repo private riêng. Dù cách nào, đừng đẩy dữ liệu, token, hay các OOF ngoài danh sách trong `.gitignore`.
- Trước khi commit/push: `git status --ignored` và kiểm tra không có `data/`, `leader_csv_file/`, token, `*.pkl` ngoài danh sách cho phép.
- `leader_csv_file/` (bản làm sạch của nhóm trưởng) không nằm trong repo; chỉ dùng cho một vài script trong `research/sweeps/`, hỏi nhóm trưởng nếu cần.
  EXP-001…004 **không** dùng nó (chỉ dùng `data/raw/`).
