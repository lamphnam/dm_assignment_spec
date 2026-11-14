## Handoff — Tăng điểm sau EXP-004, phiên 2: mọi hướng của score-plan đều âm — 2026-11-14 (tối)

- **Agent/công cụ:** Claude Code (Opus 5.5), VS Code, Windows 11. `.venv` (CPU, không đổi) và `.venv-gpu` (torch 2.15.0+cu132, RTX 3050 4 GB).
- **Commit/branch:** `main`, commit kế tiếp sau `4b7595e` ("Session 2 after EXP-004: score-plan directions, all negative"). Không push.
- **Trạng thái:** **xong**. Không có ứng viên nào tốt hơn EXP-004 → **không tạo file nộp mới, không có lệnh nộp**.
  EXP-004 vẫn là bản tốt nhất: CV 0.6302 ± 0.0091, Public 0.66918 (hạng 8 lúc nộp).
- Đọc trước: handoff [20261114-finetune-exp004.md](20261114-finetune-exp004.md) và kế hoạch [20261114-score-plan.md](20261114-score-plan.md)
  (mục 0 đã cập nhật trạng thái từng hướng).

### TL;DR
- Đã thử: P1a stacking/calibration, P1b thứ tự, P2a (+7 encoder base, 15 fold), P2b (authors, lr), P2c (abstract, chỉ train),
  P3a-lite (e5/bge-large, chỉ train 8 lớp trên, không cần `peft`), feature `doi`, thêm CE5 cho thứ tự, metadata S2 (chỉ train).
- **Tất cả đều nằm trong khoảng Δ −0.006…+0.001 so với EXP-004** (ghép cặp, honest). Không cái nào đạt tiêu chí "cả Δ honest và Δ run_exp > 0".
- Nguyên nhân nhất quán: bước chọn bài kẹt ở **AUC ≈ 0.81**. Thêm encoder có thể đẩy AUC lên 0.814 nhưng Score không tăng.
  Thứ tự đã lấy ~74% đòn bẩy (thứ tự hoàn hảo chỉ +0.019). Chọn bài hoàn hảo đáng +0.111, nhưng cần **thông tin mới**.
- Abstract và citation count (đo trên train) **không** có tín hiệu → không cần hỏi Q-07 vì lý do điểm.
- **Khuyến nghị:** dừng tối ưu điểm. Dồn thời gian cho **báo cáo + README (FR-07)**. Hai đòn bẩy lớn còn lại cần giảng viên quyết: Q-10 và P3b.

### Mục tiêu (sinh viên giao)
Tăng điểm sau EXP-004 theo score-plan (P1 → P3), giữ protocol `src/validation.py`, fine-tune trong fold, sàng lọc seed 0 → chốt → xác nhận seed 1–2,
so ghép cặp với EXP-004. **Tiêu chí nộp (sinh viên):** "chỉ cần tốt hơn lần trước". Agent áp dụng: trên 15 fold, Δ honest **và** Δ run_exp đều > 0.
Sinh viên cho phép "chạy hết trên GPU", treo máy qua đêm.

### File liên quan / đã thay đổi
- `research/ens_compare.py` (mới): so ghép cặp với **EXP-004** (`add=`, `swap=i/spec`, `seeds=`, `out=`). Báo *honest* và *run_exp*.
  Kiểm tra: tái tạo EXP-004 honest 0.6307, run_exp 0.6302 ± 0.0091 t 0.60; bagging run_exp 0.6306 (= handoff trước).
- `research/stack_cv.py` (mới): P1a/P1b. Tính lại phân phối 5 lớp của exp003 cho 15 fold → `outputs/research/oof_A5_s*_f*.pkl` (như mọi `*.pkl`: không track; mất thì script tự tính lại, ~2 phút CPU).
- `research/doi_feature_cv.py`, `research/citation_signal_cv.py` (mới): feature `doi` series; metadata S2 (chỉ train).
- `research/finetune_cv.py`: cờ `--text {title,authors,abstract,tldr}`, `--max-len`, `--freeze-below N` (phần đóng băng lưu bf16, encode dưới autocast);
  tiền tố encoder từ `src/embeddings.py::PREFIX` (e5: "query: "). Mặc định giữ nguyên hành vi EXP-004.
- `research/chain_after.sh` (mới) và `research/queue_p2a_s0.txt`, `queue_p2a_s12.txt`, `queue_p2bc_s0.txt`, `queue_p2bc_rerun.txt`, `queue_ce5_more_s0.txt`.
- `src/embeddings.py`: thêm 7 checkpoint (`e5_base`, `bge_base`, `gte_base`, `specter2`, `scibert`, `minilm_l12`, `distilroberta`) và tiền tố e5_base.
- `src/finetune.py`: `FineTunedEncoder` thêm tiền tố encoder (rỗng với 4 encoder của EXP-004 → `ft_ens_v1` không đổi).
- `research/README.md`: bảng script cập nhật. `experiments/EXPERIMENTS.md`: mục "Sau EXP-004 — phiên 2" (đủ bảng).
- `handoff/claude/20261114-score-plan.md`: mục 0 (trạng thái) + "→ ĐÃ THỬ" ở từng hướng.
- `outputs/research/*.json` mới (tóm tắt từng lượt, `ens_compare_p2a_*.json`, `stack_cv.json`) được commit; `*_oof.pkl` không track (như cũ).

### Quyết định
- **Hai thước đo cho tiêu chí nộp** (honest và run_exp đều > 0): một mình mỗi cái đổi dấu ở mức ±0.003 (bagging: −0.003 / +0.0004).
- **P2a: chạy seed 1–2 cho cả 7 encoder**, quy tắc chọn C_sel/C_all chốt lúc 20:06 trước khi có seed 1–2 (ghi trong `queue_p2a_s12.txt`).
  C_sel (chọn trên seed 0, +0.0016) âm trên seed 1–2 (−0.0020): đúng kiểu chọn theo nhiễu.
- **Không xác nhận seed 1–2 cho CE5 thứ tự** (seed 0 +0.0001 ± 0.0003): xác nhận tín hiệu bằng 0 chỉ có thể sinh "cải thiện" do nhiễu, tốn lượt nộp.
- **Không chạy lại MPNet + authors/abstract** sau OOM (batch 32, ≥128 token): bản MiniLM đã âm rõ. Muốn thử thì cần gradient accumulation.
- **Không cài `peft`** (chưa được duyệt riêng). Thay bằng đóng băng lớp dưới, không cần thư viện mới.
- P1 (sklearn) chạy CPU vì không có đường GPU; mọi thứ có torch chạy GPU.
- Vẫn giữ: không `id` (Q-10), không dữ liệu ngoài cho test (Q-07), không pseudo-label, agent không nộp.

### Thí nghiệm đã chạy (chi tiết: `experiments/EXPERIMENTS.md`, "Sau EXP-004 — phiên 2")
| Hướng | Δ honest vs EXP-004 (15 fold trừ khi ghi seed 0) | Δ run_exp | Kết luận |
|---|---:|---:|---|
| P1a stacker ST1/ST2/ST3 | −0.0039 / −0.0051 / −0.0062 | −0.002…−0.003 | ✗ |
| P1b thứ tự O1 / O2 | −0.0000 / −0.0010 | −0.0000 / −0.0010 | ✗ |
| P2a C_sel (EXP-004 + specter2 + scibert) | −0.0008 (seed 1–2: −0.0020) | −0.0000 | ✗ |
| P2a C_all (EXP-004 + 7 encoder) | −0.0015 (seed 1–2: −0.0009) | +0.0005 | ✗ |
| P2b authors (MiniLM) / lr 5e-5 (MPNet), seed 0 | −0.0020 / −0.0020 | | ✗ |
| P2c abstract (MiniLM), seed 0, chỉ train | −0.0044 (CE AUC 0.788 → 0.745) | | ✗ |
| P3a-lite e5-large / bge-large top 8, seed 0 | −0.0043 / −0.0042 | | ✗ |
| `doi` series trong exp003 | −0.0003 | +0.0003 | ✗ |
| +4 CE5 cho thứ tự, seed 0 | +0.0001 | | ✗ |
| Metadata S2 trong exp003, chỉ train | +0.0011 (AUC không đổi) | −0.0003 | ✗ |

### Đã kiểm tra
| Kiểm tra | Lệnh | Kết quả thật |
|---|---|---|
| Đối chiếu handoff | `git log --oneline -5`, `git status` | HEAD `4b7595e`; chỉ untracked như dự kiến |
| Scorer | `python -I tools/score.py selftest` | ALL PASS |
| Dữ liệu | `.venv\Scripts\python.exe -m scripts.check_data` | checksums OK |
| CUDA | `.venv-gpu\Scripts\python.exe -c "import torch; …"` | True, 2.15.0+cu132, RTX 3050 Laptop |
| OOF của EXP-004 | `ls outputs/research` vs `COMPONENTS["ft_ens_v1"]` | đủ 10 file |
| Công cụ so sánh | `-m research.ens_compare` (không add) | EXP-004 honest 0.6307, run_exp 0.6302 ± 0.0091 t 0.60 |
| `pm` của exp003 tính lại | `research.stack_cv` | khớp cache: max\|Δeg\| 2.9e-7, max\|Δpb\| 1.9e-7 |
| Text theo chế độ | in thử `texts_of` 4 chế độ | đúng; abstract/TLDR phủ 79% bài train |
| powercfg | `powercfg /query`, `/qh … LIDACTION` | đặt 19:56 (AC: sleep never, gập máy không làm gì); **trả về 21:30**: STANDBYIDLE AC/DC 0xb4, HIBERNATEIDLE AC 0 / DC 0x7fffffff, LIDACTION AC/DC 1 |
| Tiến trình nền | `Get-Process tail`, WMI | đã dừng 11 tiến trình `tail -f` mồ côi của các phiên trước (theo dõi log đã xong) |

Chưa kiểm tra: không có model production mới nên không có parity/validator/file nộp. `src/finetune.py` chỉ thêm tiền tố (rỗng với EXP-004);
không fit lại `ft_ens_v1` để kiểm tra trùng byte (lần tới tái tạo EXP-004 nên chạy `scripts.finalize_from_oof … --sub-dir outputs/<x>` một lần).

### Còn lại
- **Báo cáo + README tái lập (FR-07): ưu tiên số 1**, chưa có gì. Chất liệu mới cho Evaluation/Insights: bảng phiên 2 (kết quả âm cũng là kết quả),
  phân tích theo venue (lics khó nhất, AUC 0.724 → 0.762), khoảng trống thứ tự/chọn bài (+0.019 / +0.111).
- Chọn final trên Kaggle (sinh viên): theo CV → EXP-004 và EXP-003.
- Câu hỏi giảng viên: **Q-10** (`id`/thứ tự trong (venue, year), tương quan với nhãn) và **P3b** transductive là hai đòn bẩy còn lại.
  Q-07: số liệu cho thấy abstract và metadata S2 không giúp, nên không còn cần vì điểm.
- Thu hồi Kaggle token cũ.

### Rủi ro đã biết
- Nhiều biến thể đã thử trên cùng 15 fold: nếu sau này có ứng viên "+0.001", gần như chắc chắn là nhiễu (SE ghép cặp ~0.001).
- Kết quả âm của P2b/P2c/P3a chỉ trên seed 0 (5 fold) và một vài encoder; đủ để đóng hướng vì Δ âm rõ, không phải bằng chứng tuyệt đối.
- GPU 4 GB: input dài (≥128 token) với MPNet batch 32 OOM; e5/bge-large cần phần đóng băng ở bf16.
- Trần submission khi gộp team: cá nhân vẫn 3 lượt (không nộp thêm phiên này).

### Bước tiếp theo đề xuất
1. **Viết báo cáo + README (FR-07).** README: cài `.venv` / `.venv-gpu`, tải data, checksum, lệnh tái tạo EXP-001…004
   (EXP-004: `research/queue_*.txt` → `scripts.finalize_from_oof`). Báo cáo: dùng bảng EXPERIMENTS.md, gồm cả các hướng âm của phiên 2.
2. Hỏi giảng viên Q-10 (và P3b nếu muốn). Chỉ khi được phép mới thử; quy trình như score-plan mục 4.
3. Nếu vẫn muốn thử điểm mà không cần giảng viên: P2e (loss xếp hạng cho thứ tự), trần lý thuyết +0.019, kỳ vọng < +0.003. Không khuyến nghị.
