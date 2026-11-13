## Handoff — Research hướng tăng Score sau EXP-003 — 2026-11-14

- **Agent/công cụ:** Claude Code (Opus 5.5), VS Code, Windows 11, Python 3.14.5 trong `.venv`
- **Commit/branch:** `main`. Code + submissions ở `cd8f9ef`/`2310edd`. Research, nhật ký, handoff, sửa `docs/13` và `LOG.md` ở commit kế tiếp "Research and handoff 2026-11-14" (sinh viên đồng ý "cứ làm đi"). Chưa track: `leader_csv_file/`, `outputs/logs/`, `outputs/research/*.pkl`.
- **Trạng thái:** đang dở. Pipeline nộp bài xong và tái lập được. Research đã có kết luận chính; vài thí nghiệm phụ (abstract SPECTER/TLDR, tương tác venue) đang/chưa chạy, xem "Còn lại".

### Mục tiêu
- Tăng Private LB. Hiện tại: Public **0.64656** (EXP-003, hạng 21/26 lúc nộp). Top Public 0.68281; top 10 khoảng 0.668.
- Tiêu chí: chỉ đổi bài nộp khi CV (cùng protocol) tăng ≥ +0.015 so với EXP-003, vì std giữa fold khoảng 0.01 và Public chỉ có 298 bài.

### File liên quan
- `src/data.py`: load + kiểm checksum, đọc `Test.csv` bằng anchor (venue, year), clean text (HTML unescape, NFC, thêm lại ", " cho test).
- `src/validation.py`: protocol cố định, 5-fold StratifiedGroupKFold × seeds 0,1,2; chỉ chấm bài không thuộc `iclp`.
- `src/models.py`: `VenueMean`, `LogRegText`, `EmbedLogReg` (= `embed_v1`, model đã nộp).
- `src/embeddings.py`: embedding title pretrained, cache ở `data/interim/emb_<key>.npz` (gitignored). Ép float32 (gte-large ship fp16 → cực chậm trên CPU).
- `src/metric.py`: dùng lại `tools/score.py`.
- `scripts/run_experiment.py`: CV → chọn ngưỡng → fit full → `submissions/<name>.csv` + `outputs/<name>/report.json` → validator. BLAS 1 luồng.
- `submissions/LOG.md`: nhật ký nộp. `experiments/EXPERIMENTS.md`: nhật ký thí nghiệm, có toàn bộ bảng sweep.
- `research/`: phân tích + sweep (README trong đó). Kết quả: `outputs/research/*.json`, log: `outputs/logs/`.
- `data/external/s2_train.jsonl`: metadata Semantic Scholar cho **train** (lấy 2026-11-14 02:02). Gitignored.
- `leader_csv_file/`: bản làm sạch/bổ sung của nhóm trưởng (untracked). **Không cần cho pipeline** (ablation: 0 cải thiện).

### Đã thay đổi (phiên này)
- Toàn bộ `src/`, `scripts/`, `requirements.txt`, `.gitattributes` (giữ CSV đúng từng byte): commit `cd8f9ef`.
- `submissions/LOG.md`: điểm Public #1, #2 (`2310edd`); sau đó sửa ngày sang UTC (chưa commit).
- `docs/13`: Q-05 đã rõ (tối đa 3 final), Q-03 gần như rõ (0.60953 là benchmark host), Q-07 thêm dữ kiện khả thi (chưa commit).
- Thêm `research/`, `experiments/EXPERIMENTS.md`, file handoff này (chưa commit).

### Quyết định
- Không dùng `id` / thứ tự id làm feature (Q-10 mở, integrity).
- Không lấy dữ liệu ngoài cho **bài test** khi Q-07 chưa được trả lời. `research/fetch_s2.py` chặn `test` nếu không có cờ `--i-asked-q07`.
- Giữ `iclp` trong train (bỏ đi làm giảm 0.004), chỉ loại khỏi tập chấm.
- Agent **không nộp bài** (AGENTS.md). Sinh viên tự nộp bằng lệnh agent chuẩn bị.

### Thí nghiệm đã chạy
| EXP id | Thay đổi | Score CV (mean ± std) | Q | R | Kết luận |
|---|---|---|---|---|---|
| EXP-001 | Baseline venue mean | 0.5247 ± 0.0125 | 0.356 | 1.000 | baseline báo cáo |
| EXP-002 | LogReg TF-IDF | 0.5768 ± 0.0111 | 0.451 | 0.802 | Public 0.59467 |
| EXP-003 | + char n-gram, author stats, 3 embedding (MiniLM+MPNet+SPECTER), kNN | **0.6178 ± 0.0097** | 0.515 | 0.773 | **Public 0.64656**, đang dùng |
| sweep4 | Embedding lớn (bge/e5/gte/SciNCL), các tổ hợp | ≤ 0.6158 | | | không hơn EXP-003 |
| sweep5 | Ablation dữ liệu (clean, bỏ iclp, bỏ dup, authors nhóm trưởng) | Δ −0.004…0.000 | | | clean thêm không đáng làm |
| abstract_cv | + embedding title+abstract (MiniLM), 5 fold seed 0, ngưỡng trung thực | 0.6117 vs A 0.6157 | | | **không giúp** với MiniLM |

Chi tiết từng sweep: `experiments/EXPERIMENTS.md`.

### Kết quả research (`research/analysis_exp003.py`, OOF seed 0, 2,038 bài không thuộc `iclp`)
1. **Điểm mất ở bước CHỌN bài, không phải sắp thứ tự.** AUC P(y>1) = 0.788, Spearman(E[gain], y) = 0.594.
   Mô phỏng: AUC 0.85 → +0.026, AUC 0.90 → +0.046, tức khoảng **+0.004 Score cho mỗi +0.01 AUC**. Nâng Spearman thứ tự từ 0.59 lên 0.81 chỉ được +0.0125.
2. **Phương pháp chọn ngưỡng không phải đòn bẩy.** Ngưỡng chọn trung thực = 0.55 ở cả 5 fold. Cắt danh sách theo expected-score (plug-in) cho 0.6156, so với 0.6157 của ngưỡng cố định. Score phẳng ±0.01 khi t trong [0.45, 0.65].
3. **Calibration tốt**, cả tổng thể lẫn từng venue (mean pb so với tỉ lệ thật): cav 0.545/0.543, kr 0.741/0.732, lics 0.536/0.523, lpnmr 0.813/0.819. Test có mean pb = 0.617.
4. **Venue khó nhất là `lics`** (AUC 0.721), tiếp theo cav 0.773, kr 0.773, lpnmr 0.897. Riêng cav + lics đã chiếm 68% test.
5. **Sở thích khác nhau theo venue** (log-odds token):
   - cav, thích: neural/deep/network, synthesis, markov, data-driven.
   - lics, thích: probabilistic, graph, first-order, constructive. Không thích: quantum, homotopy, effectful.
   - kr, thích: description logics, argumentation, belief revision, temporal, OWL, preferences.
   - lpnmr, thích: ASP/answer set.
   - Phía label 1 còn bị chi phối bởi token của proceedings/front matter.
6. **Năm:** trong cav/kr/lpnmr, bài mới hơn được thích hơn; `lics` ngược lại. Test nghiêng về năm cũ (43% ≤ 2019, train 38%). Thêm one-hot venue×year không giúp (−0.003).
7. **kNN:** nhãn của bài gần nhất chỉ có ích khi độ tương đồng cosine > 0.79 (cùng phe "đáng đọc" 0.84, so với khoảng 0.61 ở mức thường).
8. **Public 0.647 có lẽ hơi may.** Expected score trên test tính từ xác suất đã calibrate là 0.621, gần CV 0.618. Std của một split 298 bài khoảng 0.015–0.02, nên **Private có thể chỉ khoảng 0.62–0.63**. Đừng đuổi theo Public.
9. **Dữ liệu ngoài, khả thi kỹ thuật** (chỉ kiểm trên train):
   - Semantic Scholar tìm thấy 2266/2469 bài train: abstract 1502, TLDR 1874; title khớp ≥ 0.9 ở 36/37 bài mẫu.
   - OpenAlex có abstract cho 19/20 DOI mẫu.
   - Test có 359 DOI + 235 ID S2 (594/596 bài).
   - **Nhưng abstract qua MiniLM không tăng CV** (xem bảng). SPECTER và TLDR đang được kiểm tra, xem "Còn lại".

### Đã kiểm tra
| Kiểm tra | Lệnh | Kết quả thật |
|---|---|---|
| Scorer | `python -I tools/score.py selftest` | ALL PASS (T1–T9) |
| Dữ liệu | `python -I tools/inspect_data.py data/raw` | 48 checks, 0 FAIL; 3 SHA-256 khớp docs/05 |
| Loader | `.venv\Scripts\python.exe -m scripts.check_data` | checksums OK; khớp title nhóm trưởng 2494/2494 & 596/596 |
| Harness | oracle/random trên 15 fold | oracle bỏ label 1 = 0.7579, random = 0.4957 |
| Tái lập EXP-003 | `run_experiment --model embed_v1` chạy 2 lần | SHA-256 giống nhau `11645f1f4e2e…`; validator VALID |
| CSV giữ đúng byte trong git | `git hash-object` so với blob HEAD | khớp (nhờ `.gitattributes`) |
| Research | `-m research.analysis_exp003` | xem mục trên; `outputs/research/summary_exp003.json` |
| Abstract (train) | `-m research.fetch_s2 train`; `-m research.abstract_cv minilm` | 0.6117 vs 0.6157 (không giúp) |
| SetFit cài được? | `pip install --dry-run setfit` | resolve OK (setfit 1.2.0); **chưa chạy thử** |

Chưa kiểm tra (và lý do): sweep6 (ensemble head, ngưỡng theo venue, HGB) bị dừng theo yêu cầu; fine-tune encoder chưa làm; README tái lập (FR-07) chưa viết.

### Còn lại
- **Thí nghiệm đang/chưa chạy khi viết handoff** (log ở `outputs/logs/`):
  - `research.abstract_cv specter`: title[SEP]abstract với SPECTER → `outputs/research/abstract_cv_abstract_specter.json`.
  - `research.abstract_cv --tldr minilm`: title + TLDR → `outputs/research/abstract_cv_tldr_minilm.json`.
  - `research.venue_interaction_cv`: tương tác embedding × venue (giả thuyết từ phát hiện 5) → `outputs/research/venue_interaction_cv.json`.
  - Kết quả cuối được ghi ở mục "Cập nhật cuối phiên" bên dưới, nếu kịp. Nếu không có, chạy lại các lệnh trên.
- Câu hỏi mở cần hỏi giảng viên: **Q-07** (dữ liệu ngoài cho bài test; chỉ đáng hỏi gấp nếu SPECTER/TLDR cho thấy tăng), **Q-10** (`id`), Q-01, Q-04 (deadline LMS).
- Chưa viết README tái lập (FR-07a–e); báo cáo chưa bắt đầu.
- Nên thu hồi Kaggle token cũ và tạo token mới: token đã từng bị dán vào chat. Token mới lưu ở `%USERPROFILE%\.kaggle\access_token`.

### Rủi ro đã biết
- **Overfit Public** (R-01): Public 0.647 cao hơn kỳ vọng 0.62. Chọn model theo CV.
- **Trần submission khi gộp team** (R-12): ngày UTC 2026-11-13 bạn đã dùng 2/3. Cần hỏi nhóm tổng số lượt đã dùng; trần khoảng 3 × số ngày từ 13/10.
- **Fine-tune encoder phải làm TRONG từng fold.** Fine-tune trên toàn train rồi mới CV là leakage.
- Embedding cache (`data/interim`) và S2 data không nằm trong git. Máy mới phải tải lại model HF (khoảng 1–2.5 GB).
- Python 3.14 + torch 2.15 CPU: chạy được. Cài torch bằng `--index-url https://download.pytorch.org/whl/cpu`.

### Bước tiếp theo đề xuất (theo thứ tự ưu tiên)
1. **Đọc kết quả 3 thí nghiệm còn dở**: mục "Cập nhật cuối phiên" hoặc 3 file JSON ở trên. Thí nghiệm nào tăng ≥ 0.01 (honest, seed 0) thì xác nhận lại trên 15 fold bằng `run_experiment` với model mới.
2. **Fine-tune encoder cho bước chọn** (không bị chặn bởi luật; đòn bẩy lớn nhất còn lại). SetFit (Tunstall et al., 2022, arXiv:2209.11055) hoặc `SentenceTransformerTrainer`, train contrastive trên cặp worthwhile/label 1, **trong từng fold**. Bắt đầu với MiniLM (nhanh trên CPU), đo AUC P(y>1) và Score. Mục tiêu AUC ≥ 0.82.
3. **Ensemble đa dạng cho bước chọn**: chạy lại `research/sweeps/sweep6.py` (đã có code). Đây là trung bình head binary + multinomial + HistGradientBoosting, kèm seed bagging. Kỳ vọng nhỏ (+0.003…0.008) nhưng rẻ.
4. **Bán giám sát / transductive** (phải công khai theo NFR-05): label propagation trên đồ thị kNN gồm cả title test (Zhou et al., 2004). Đánh giá đúng protocol: validation fold đóng vai "test không nhãn".
5. **Nếu abstract SPECTER/TLDR tăng rõ:** gửi Q-07 cho giảng viên kèm số liệu. Chỉ khi được phép mới chạy `fetch_s2 test --i-asked-q07`, và phải trích dẫn Semantic Scholar (Kinney et al., 2023, arXiv:2301.10140).
6. **Không đáng làm tiếp** (đã có bằng chứng): tinh chỉnh ngưỡng/plug-in, clean thêm, embedding lớn hơn, authors của nhóm trưởng, one-hot venue×year.
7. **Song song cho báo cáo:** viết README tái lập (FR-07); dùng các bảng trong `experiments/EXPERIMENTS.md` cho mục Evaluation và Data analysis (rubric 3, 4, 6). Có thể thêm clustering chủ đề cho phần Insights.
8. Nộp tiếp chỉ khi CV tăng ≥ 0.015. Agent chuẩn bị file, commit và lệnh; **sinh viên tự nộp**.

### Cập nhật cuối phiên
Cả 3 thí nghiệm đã chạy xong (khoảng 02:30 ngày 14/11 giờ VN). Cùng protocol: 5 fold seed 0, chấm bài không thuộc `iclp`, ngưỡng chọn trung thực. Mốc A = exp003 = **0.6157 ± 0.0078**, AUC 0.788.

| Thí nghiệm | Score | AUC | Δ so với A |
|---|---:|---:|---:|
| + title+abstract SPECTER (title[SEP]abstract) | 0.6078 ± 0.0136 | 0.788 | −0.008 |
| SPECTER abstract thay embedding title | 0.5967 ± 0.0100 | 0.764 | −0.019 |
| + title+TLDR (MiniLM) | 0.6105 ± 0.0092 | 0.783 | −0.005 |
| TLDR thay embedding title | 0.5996 ± 0.0091 | 0.754 | −0.016 |
| + embedding × venue (w=1) | 0.6164 ± 0.0053 | 0.787 | +0.001 (trong nhiễu) |
| + embedding × venue (w=2) | 0.6105 ± 0.0088 | 0.782 | −0.005 |

**Kết luận:**
- **Abstract/TLDR không giúp**, với cả MiniLM lẫn SPECTER. Vì vậy Q-07 **không còn gấp**; hướng dữ liệu ngoài coi như loại, trừ khi có ý tưởng khác.
- **Tương tác venue không giúp.** Model tuyến tính có vẻ đã bão hoà trên các biểu diễn cố định (frozen).
- ⇒ Bước tiếp theo #1 **giữ nguyên và quan trọng hơn**: fine-tune encoder trong từng fold (SetFit / SentenceTransformerTrainer). Tiếp theo là #3 ensemble và #4 transductive. Bỏ #5 (abstract).

Việc khác đã làm cuối phiên:
- Commit research, nhật ký và handoff.
- Trả cài đặt sleep khi cắm sạc về 3 phút (`powercfg /change standby-timeout-ac 3`). Trước đó đã tạm đặt "never" để job chạy qua đêm.
