# research/: phân tích và sweep (không phải pipeline nộp bài)

Pipeline nộp bài nằm ở `src/` + `scripts/run_experiment.py`. Thư mục này chứa phân tích và các sweep đã dùng để chọn hướng.
Kết quả ghi vào `outputs/research/` và `outputs/logs/`.

| File | Làm gì | Chạy |
|---|---|---|
| `analysis_exp003.py` | Chẩn đoán OOF của exp003: calibration, threshold, plug-in cutoff, headroom AUC, authors/kNN/year, từ phân biệt, coverage doi | `.venv\Scripts\python.exe -m research.analysis_exp003` |
| `abstract_feasibility.py` | Thử 40 bài **train**: Semantic Scholar / OpenAlex có abstract không | `-m research.abstract_feasibility 40` |
| `fetch_s2.py` | Lấy abstract/TLDR từ Semantic Scholar vào `data/external/` (gitignored). **Test bị chặn đến khi Q-07 được trả lời** | `-m research.fetch_s2 train` |
| `abstract_cv.py` | CV chỉ trên train: exp003 vs exp003 + embedding abstract | `-m research.abstract_cv minilm` |
| `sweeps/` | Các sweep 2026-11-14 (sweep1–6, ablation dữ liệu, so sánh file nhóm trưởng). Chạy với `PYTHONPATH=<repo>;<repo>\research\sweeps` | `python research\sweeps\sweep2.py` |

Các sweep chấm ngưỡng tốt nhất trên chính các fold (hơi lạc quan); `analysis_exp003.py`/`abstract_cv.py` chọn ngưỡng trên các fold còn lại ("honest").
