# research/: phân tích và sweep (không phải pipeline nộp bài)

Pipeline nộp bài nằm ở `src/` + `scripts/run_experiment.py`. Thư mục này chứa phân tích và các sweep đã dùng để chọn hướng.
Kết quả ghi vào `outputs/research/` và `outputs/logs/`.

| File | Làm gì | Chạy |
|---|---|---|
| `analysis_exp003.py` | Chẩn đoán OOF của exp003: calibration, threshold, plug-in cutoff, headroom AUC, authors/kNN/year, từ phân biệt, coverage doi | `.venv\Scripts\python.exe -m research.analysis_exp003` |
| `abstract_feasibility.py` | Thử 40 bài **train**: Semantic Scholar / OpenAlex có abstract không | `-m research.abstract_feasibility 40` |
| `fetch_s2.py` | Lấy abstract/TLDR từ Semantic Scholar vào `data/external/` (gitignored). **Test bị chặn đến khi Q-07 được trả lời** | `-m research.fetch_s2 train` |
| `abstract_cv.py` | CV chỉ trên train: exp003 vs exp003 + embedding abstract | `-m research.abstract_cv minilm` |
| `finetune_cv.py` | Fine-tune encoder **trong từng fold** (CE / CE5 / SetFit), lưu OOF. Cờ: `--text {title,authors,abstract,tldr}`, `--max-len`, `--freeze-below N` (đóng băng lớp dưới, lưu bf16) | `.venv-gpu\Scripts\python.exe -m research.finetune_cv --enc minilm --methods ce` |
| `finetune_queue.sh`, `queue_*.txt`, `chain_after.sh` | Hàng đợi các lượt `finetune_cv` trên GPU; `chain_after.sh <log> <queue> <log mới>` chạy hàng đợi kế khi hàng đợi trước xong | `bash research/finetune_queue.sh research/queue_p2a_s0.txt` |
| `finetune_combine.py` | Ghép OOF nhiều lượt, so ghép cặp với A (exp003) | `-m research.finetune_combine finetune_minilm:CE ...` |
| `ens_compare.py` | So ghép cặp với **EXP-004**: `add=` (thêm thành phần CE), `swap=i/spec` (thay thành phần i), `seeds=` | `-m research.ens_compare add=finetune_e5_base_ce:CE seeds=0` |
| `stack_cv.py` | P1: stacker lồng trong fold + thứ tự từ P(y>1) của ensemble (tính lại `pm` của exp003 cho 15 fold) | `-m research.stack_cv` |
| `doi_feature_cv.py` | exp003 + one-hot series DOI, thay A trong EXP-004 | `-m research.doi_feature_cv` |
| `citation_signal_cv.py` | **Chỉ train**: metadata S2 (citation, publicationTypes) có giúp không, để quyết định hỏi Q-07 | `-m research.citation_signal_cv` |
| `sweeps/` | Các sweep 2026-11-14 (sweep1–6, ablation dữ liệu, so sánh file nhóm trưởng). Chạy với `PYTHONPATH=<repo>;<repo>\research\sweeps` | `python research\sweeps\sweep2.py` |

Các sweep chấm ngưỡng tốt nhất trên chính các fold (hơi lạc quan); `analysis_exp003.py`/`abstract_cv.py` chọn ngưỡng trên các fold còn lại ("honest").
