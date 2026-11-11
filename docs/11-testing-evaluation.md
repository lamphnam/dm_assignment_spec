# 11 — Testing và evaluation

Đặc tả của scorer, validator và data checks. Đã có bản tham chiếu **tùy chọn** đã kiểm thử trong [tools/](../tools/README.md)
(`score.py`, `validate_submission.py`, `inspect_data.py`). Bạn dùng hay tự viết đều được. Scorer tự viết nên qua được T1–T9.

## 1. Đặc tả offline scorer

Phải bám đúng [evaluation](reference/competition-pages/evaluation.md). Input là các cặp `(id, priority)` của **một split**
cùng label thật của các id trong split đó.

1. Bỏ các bài có `priority == 0`.
2. Sort theo `priority` **giảm dần**. Các bài cùng priority được xếp theo `str(id)` **tăng dần**.
3. Với vị trí r = 1..m: g_r = (y_r − 1)/4 và w_r = 1/log2(r + 1).
4. Q = Σ w_r g_r / Σ w_r. Nếu m = 0 thì Q = 0.
5. P = số bài trong split có y > 1. R = (số bài được chọn có y > 1) / P. Nếu P = 0 thì R = 0.
6. Score = 2QR/(Q + R). Nếu Q = 0 hoặc R = 0 thì Score = 0.

Scorer phải trả về **cả ba giá trị (Score, Q, R)** để phục vụ NFR-03.

### Test cases bắt buộc

Các giá trị dưới đây là **[Xác minh]**: tính theo đúng các bước trên (chỉ dùng công thức, không dùng dữ liệu), làm tròn 6 chữ số.
So sánh với sai số ≤ 5e-7.

| # | Labels theo thứ tự đề xuất | Labels toàn split | Q | R | Score |
|---|---|---|---:|---:|---:|
| T1 | [5] | [5] | 1.000000 | 1.000000 | 1.000000 |
| T2 | [1] | [1, 2] | 0 | 0 | 0 |
| T3 | [5, 1] | [5, 1, 3] | 0.613147 | 0.500000 | 0.550823 |
| T4 | [1, 5] | [5, 1, 3] | 0.386853 | 0.500000 | 0.436209 |
| T5 | [3, 3, 2] | [3, 3, 2, 1, 1] | 0.441340 | 1.000000 | 0.612403 |
| T6 | [] (mọi priority = 0) | [2, 3] | 0 | 0 | 0 |
| T7 | Q = 0.80, R = 0.60 (ví dụ trong EV) | — | — | — | 0.685714 |
| T8 | Tie-break: id `"10"`, `"9"`, `"1000"`, `"713"` cùng priority | — | Thứ tự phải là `10, 1000, 713, 9` | | |
| T9 | Priority âm | — | Phải báo lỗi (FR-03) | | |

T3 và T4 chứng minh rằng thứ tự ảnh hưởng đến Q nhưng không ảnh hưởng đến R.

## 2. Local validation

Rules §7: cách chia train để validate **do mỗi người tự chọn**, nhưng phải nhất quán, giải thích được, và mọi phương pháp được so sánh
trên **cùng partition và cùng quy tắc chấm** (NFR-02). Không có protocol bắt buộc. Dưới đây là các **dữ kiện** liên quan khi thiết kế:

| Dữ kiện | Nguồn |
|---|---|
| Mỗi split chính thức có **298 bài**; Q được normalize theo độ dài danh sách, R được tính trên từng split | EV |
| Std của Score giữa các subset 298 bài lấy từ train khoảng 0.014–0.023 | [08 §1](08-methodology.md#các-mốc-tham-chiếu-đã-tính-xác-minh) |
| Train có các bài trùng title, cùng DOI, hoặc liên quan đến nhau | [07 §4](07-data-processing.md#4-duplicate-và-các-bài-liên-quan) |
| Phân phối venue/year của test khác train (test không có `iclp`) | [05 §5](05-dataset-overview.md#5-distribution-shift-giữa-train-và-test) |
| `id` và thứ tự trong file có tương quan với label | [05 §3](05-dataset-overview.md#3-kích-thước-và-phân-chia), Q-10 |
| Metadata của test là công khai; dùng nó (unsupervised) thì phải công khai trong báo cáo | NFR-05 |

Báo cáo phải giải thích được lựa chọn validation, và nêu leakage, sampling bias, overfit LB, độ biến thiên (rubric tiêu chí 6).

## 3. Validator cho submission

Chạy **trước mỗi lần nộp**. Validator thất bại thì không nộp.

- [ ] Header chính xác là `id,priority`.
- [ ] Có đúng 596 dòng. Tập id trùng khớp **tuyệt đối** với `Test.csv`, không thiếu, không thừa, không trùng.
- [ ] `priority` parse được thành float, **hữu hạn** (không NaN, không inf) và **≥ 0**.
- [ ] Có ít nhất một `priority > 0`. Nếu toàn 0 thì score = 0.
- [ ] (Cảnh báo) Số giá trị priority > 0 bị trùng nhau, vì sẽ bị tie-break theo id dạng text.
- [ ] (Cảnh báo) Tỷ lệ bài được chọn có hợp lý so với tỷ lệ đã tune trên validation không.
- [ ] Đã ghi SHA-256 của file vào manifest ([12](12-reproducibility.md#3-manifest-cho-mỗi-submission)).

## 4. Kiểm tra dữ liệu tự động (data checks)

Giá trị **[Xác minh]** trên dữ liệu ngày 2026-11-11. Nếu một assertion thất bại, dữ liệu đã thay đổi hoặc parser bị lỗi.
`tools/inspect_data.py` chạy toàn bộ các kiểm tra này.

| Kiểm tra | Giá trị mong đợi |
|---|---|
| SHA-256 ba file | Như [05 §1](05-dataset-overview.md#1-nguồn) |
| Số dòng train / test / template | 2494 / 596 / 596 |
| Phân phối Label (train) | {1: 903, 2: 514, 3: 438, 4: 367, 5: 272} |
| Venue (test, sau khi đọc đúng) | {cav: 221, lics: 187, kr: 151, lpnmr: 37} |
| Year (test) | Mọi giá trị nằm trong 2016–2025 |
| `authors` rỗng | train 192, test 41 |
| Giao nhau id train/test | ∅ |
| Thứ tự id của template | Trùng thứ tự id của `Test.csv` |

## 5. Báo cáo kết quả

Rubric tiêu chí 6 yêu cầu: điểm từng thành phần (Q, R), so sánh với baseline trong cùng điều kiện, ví dụ lỗi tiêu biểu,
và độ biến thiên hoặc độ bất định của kết quả.
