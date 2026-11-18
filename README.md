# CO3029 Data Mining: knowledge base nội bộ của nhóm

Repo nội bộ cho nhóm học thuật 5 người, dùng cho Kaggle competition
[`assignment-data-mining-261`](https://www.kaggle.com/competitions/assignment-data-mining-261): xếp thứ tự ưu tiên đọc cho 596 bài báo
(`id,priority`), chấm bằng harmonic mean của Relevance và Coverage.

Repo cung cấp cho mọi thành viên **cùng một bộ dữ kiện**: đặc tả, luật, dữ liệu và các phát hiện đã kiểm chứng, metric,
công cụ tham chiếu, hướng dẫn cài đặt và Agent Skills. Phần tài liệu không đề xuất hướng giải; riêng bản này kèm lời giải của chủ repo (bên dưới).
Mỗi thành viên clone về, làm cùng AI agent của mình, và **tự nộp bài bằng tài khoản Kaggle của mình**.

## Lời giải hiện có và cách chạy thử (dành cho thành viên nhóm)

Bản này kèm lời giải của chủ repo để các bạn chạy thử và cải tiến (Kaggle Public tốt nhất **0.66918**, CV **0.6302 ± 0.0091**):

| EXP | Cách làm | CV | Public |
|---|---|---:|---:|
| 001 | Điểm trung bình theo venue | 0.5247 | — |
| 002 | TF-IDF + logistic regression | 0.5768 | 0.59467 |
| 003 | Embedding đóng băng + kNN + TF-IDF + logistic regression | 0.6178 | 0.64656 |
| **004** | EXP-003 + 4 encoder fine-tune trong từng fold (cần GPU) | **0.6302** | **0.66918** |

```powershell
git clone <url-repo> assignment; cd assignment
python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt     # CPU
# GPU (tuỳ chọn, để fine-tune): python -m venv .venv-gpu; .\.venv-gpu\Scripts\python.exe -m pip install -r requirements-gpu.txt
# Tải data vào data/raw/ bằng tài khoản Kaggle CỦA BẠN (docs/10 §3), rồi:
.\.venv\Scripts\python.exe -m scripts.check_data                   # kiểm checksum
.\.venv\Scripts\python.exe -m research.ens_compare                  # tái tạo CV của EXP-004 từ OOF có sẵn, không cần GPU
```

**Đọc [docs/15-solution-guide.md](docs/15-solution-guide.md)**: cấu trúc code, cách chạy lại EXP-001…004, các hướng đã thử và thất bại (đừng lặp lại),
điểm đang kẹt, quy trình so sánh ghép cặp và lưu ý về quota nộp bài. Nhật ký thí nghiệm: [experiments/EXPERIMENTS.md](experiments/EXPERIMENTS.md).

> Không có trong repo (gitignore): `data/` (tự tải), `leader_csv_file/` (xin nhóm trưởng), token Kaggle, venv, ~100 file OOF trung gian.

## Bắt đầu với knowledge base (tài liệu, luật, skills)

```bash
# mở bằng AI coding agent (ví dụ Claude Code), rồi gõ:
/assignment-onboarding
```

[docs/getting-started.md](docs/getting-started.md) · [docs/README.md](docs/README.md) · [AGENTS.md](AGENTS.md) · [tools/](tools/README.md)

> **Cách tham gia:** mỗi người nộp độc lập, cuối kỳ gộp vào team của người có điểm cao nhất. Tổng submission của cả nhóm phải dưới trần để gộp được.
> Xem [docs/14](docs/14-compliance-and-distribution.md).
