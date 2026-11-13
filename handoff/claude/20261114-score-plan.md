# Kế hoạch tăng điểm sau EXP-004 — 2026-11-14

> Viết cho agent phiên sau (và sinh viên). Tài liệu này chỉ đề xuất hướng thử, kèm bằng chứng và ước lượng.
> Các con số "kỳ vọng" là **phỏng đoán**, chưa đo. Kết quả thật ghi vào `experiments/EXPERIMENTS.md`.

## 1. Đang ở đâu
| | AUC P(y>1) | CV (quy trình run_experiment) | Public | Ghi chú |
|---|---:|---:|---:|---|
| EXP-003 `embed_v1` | 0.790 | 0.6178 ± 0.0097 | 0.64656 | logistic trên TF-IDF + author stats + 3 embedding đóng băng + kNN |
| **EXP-004 `ft_ens_v1`** | **0.810** | **0.6302 ± 0.0091** | **0.66918** (hạng 8) | EXP-003 + CE fine-tune 4 encoder trong từng fold |

- Top Public 0.68281; hạng 7 là 0.66962. Public chỉ có 298 bài (std khoảng 0.015–0.02), nên **chỉ tối ưu theo CV**.
- Mốc tham chiếu (cùng protocol): random 0.4957; oracle chọn đúng + thứ tự đúng 0.7579.
- Quy tắc ngón tay cái (phân tích EXP-003): **+0.01 AUC ≈ +0.004–0.005 Score**. Nâng Spearman của thứ tự từ 0.59 lên 0.81 ≈ +0.0125.
- Metric: Q = trung bình gain có trọng số DCG `1/log2(i+1)` trên danh sách được chọn, theo thứ tự priority; R = độ phủ bài y > 1; Score = trung bình điều hoà.
  Vì vậy (a) **chọn** bài (AUC) và (b) **thứ tự ở đầu danh sách** là hai đòn bẩy.

## 2. Đã thử, đừng lặp lại (bằng chứng ở `experiments/EXPERIMENTS.md`)
- Chọn ngưỡng / plug-in / cắt theo expected score; one-hot venue×year; tương tác embedding×venue.
- Embedding đóng băng lớn hơn (bge/e5/gte-large, SciNCL); clean thêm dữ liệu; authors của nhóm trưởng; bỏ `iclp`.
- Abstract/TLDR qua embedding **đóng băng** (MiniLM, SPECTER).
- SetFit (1/2/10 vòng); CE5 cho thứ tự (+0.001 trên 15 fold); bagging seed fine-tune; thay khối embedding trong EXP-003 bằng embedding đã fine-tune.
- CE 2 epoch < 4 epoch ≈ 8 epoch; có hay không tiền tố venue/year không khác biệt.

## 3. Hướng sẽ làm (theo thứ tự ưu tiên)

### P1 — Rẻ, không cần GPU, chỉ dùng OOF có sẵn (mỗi mục khoảng 1 giờ)
**P1a. Stacking / calibration các thành phần chọn bài.**
- Hiện EXP-004 lấy trung bình logit **bằng trọng số** của 5 thành phần (EXP-003 + 4 CE), và bị quá tự tin
  (mean pb 0.648 so với tỉ lệ thật 0.614).
- Thử: temperature scaling từng thành phần; logistic stacker trên các logit (± venue one-hot).
  Phải **fit lồng trong fold**: trên OOF 15 fold, fit stacker bằng 4 fold, áp vào fold thứ 5, cùng seed.
- Dữ liệu: `outputs/research/finetune_*_oof.pkl`. Ghép bằng `scripts/finalize_from_oof.py::ensemble_oof` hoặc `research/finetune_combine.py`.
- Kỳ vọng +0.002…+0.005. Nếu tốt hơn thì sửa `FineTuneEnsemble` (cần lưu stacker) và tạo `ft_ens_v2`.

**P1b. Thứ tự dùng P(y>1) tốt hơn.**
- Hiện thứ tự = E[gain] của EXP-003, trong đó phần P(y>1) đến từ head multinomial yếu (AUC khoảng 0.79).
- Thử: `eg' = pb_ens × E_A[gain | y>1]`, với `E_A[gain | y>1] = eg_A / pm_A`.
  - `pm` = P(y>1) của head multinomial. Cột này có trong `outputs/research/oof_exp003_seed0.pkl` nhưng **không có** trong cache `oof_A_s*_f*.pkl` (chỉ có eg, pb).
  - Muốn chạy đủ 15 fold thì tính lại OOF của EXP-003 kèm phân phối 5 lớp: chạy CPU, khoảng 6 giây/fold.
- Đòn bẩy thứ tự còn trống khoảng +0.0125. Kỳ vọng +0.002…+0.006.

### P2 — GPU, khung có sẵn (`research/finetune_cv.py` + `research/finetune_queue.sh`)
**P2a. Thêm encoder đa dạng cho CE.**
- Ứng viên: `intfloat/e5-base-v2` (cần tiền tố "query: "), `BAAI/bge-base-en-v1.5`, `thenlper/gte-base`, `allenai/specter2_base`,
  `allenai/scibert_scivocab_uncased`, `sentence-transformers/all-MiniLM-L12-v2`.
- Phải thêm vào `src/embeddings.py::MODELS`. Chưa kiểm tra tải về và VRAM; cỡ base (110M) vừa 4 GB với fused AdamW.
- Bằng chứng: 1 → 3 → 4 encoder cho AUC 0.800 → 0.805/0.808 → 0.810 (bão hoà dần). Kỳ vọng +0.002…+0.005 nếu đủ khác biệt.
- Chi phí: khoảng 5 phút/encoder trên seed 0, khoảng 10 phút cho seed 1–2.

**P2b. Siêu tham số và input của CE.**
- lr 3e-5 / 5e-5; 6 epoch; label smoothing; thêm authors vào text (`"<venue> <year>: <title> | authors: …"`). Cần thêm cờ vào `texts_of`.
- Mỗi biến thể chỉ chạy seed 0 trước. Kỳ vọng nhỏ (+0.001…+0.004); **rủi ro dò theo nhiễu**, nên giới hạn số biến thể.

**P2c. Fine-tune với abstract, chỉ trên train.**
- Abstract qua embedding đóng băng không giúp, nhưng **chưa thử fine-tune**. Dữ liệu train có ở `data/external/s2_train.jsonl` (abstract 1502/2469, TLDR 1874).
- Chỉ đo CV trên train. Nếu tăng ≥ +0.01 thì báo sinh viên gửi **Q-07** cho giảng viên kèm số liệu.
- **Không** lấy dữ liệu ngoài cho test khi Q-07 chưa được trả lời. `research/fetch_s2.py` chặn test nếu không có `--i-asked-q07`.

### P3 — Cần cài thêm hoặc xác nhận luật trước
- **P3a. LoRA cho encoder lớn** (bge-large/e5-large, 335M; full fine-tune không vừa 4 GB). Cần cài `peft` (hỏi sinh viên).
  Bản đóng băng của chúng không hơn ở sweep4, nên kỳ vọng thấp.
- **P3b. Transductive** (MLM domain adaptation trên title train+test, label propagation trên đồ thị kNN có test).
  Phải công khai theo NFR-05. **Không pseudo-label test** khi chưa hỏi giảng viên (AGENTS.md: không tự gán nhãn test).
- **P3c. Dữ liệu dblp/proceedings của nhóm trưởng** (`leader_csv_file/proceedings*.csv`): là dữ liệu ngoài, nên với test thì bị Q-07 chặn.
  Chỉ phân tích trên train.

## 4. Quy trình bắt buộc (giữ giống EXP-004)
1. **Fine-tune trong từng fold**: load lại checkpoint pretrained mỗi fold, chỉ dùng phần train của fold. Không dùng `id` (Q-10).
2. **Sàng lọc trên seed 0** (5 fold), so ghép cặp với A bằng `research/finetune_combine.py` (Δ, SE, số fold tốt hơn).
3. **Chốt cấu hình trước**, ghi vào `research/queue_*.txt` và EXPERIMENTS.md, **rồi mới chạy seed 1–2**. Kết luận dựa trên 15 fold.
4. So với **EXP-004** (không phải EXP-003). Mốc EXP-004 theo ngưỡng trung thực: xem `outputs/research/finetune_combine_15f_4ce_2eg.json`.
   Cần thêm một script so trực tiếp ensemble mới với EXP-004 ghép cặp từng fold (hiện `finetune_combine` chỉ so với A).
5. Tạo file nộp: `scripts/finalize_from_oof.py` (thêm mục vào `COMPONENTS`), có `--parity`, và chạy fit lại để kiểm tra trùng byte.
6. **Tiêu chí đề xuất nộp:** tiêu chí gốc là CV +0.015. Sinh viên đã chấp nhận nộp EXP-004 với +0.012 (tốt hơn ở 15/15 fold).
   **Hỏi sinh viên** ngưỡng cho vòng mới trước khi đề xuất. Agent không nộp.
7. Job dài chạy nền, log vào `outputs/logs/`. `PYTHONIOENCODING=utf-8`. Chạy qua đêm thì đặt `powercfg`, rồi trả lại như cũ
   (gốc: STANDBYIDLE AC/DC 180 s, LIDACTION AC/DC 1).

## 5. Ngân sách
- GPU: RTX 3050 Laptop 4 GB, `.venv-gpu`. Một encoder cỡ base mất khoảng 30 giây/fold; 15 fold khoảng 8–10 phút/encoder.
- Kaggle: 3 lượt/ngày/team; cá nhân đã dùng 3 (đều ngày UTC 13/11). Khi gộp team cuối kỳ, tổng lượt của 5 người phải dưới trần (docs/14).
- Deadline: 2026-12-14 23:59 UTC. **Báo cáo và README (FR-07) vẫn chưa có**; nên dành thời gian song song.
