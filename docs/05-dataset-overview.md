# 05 — Tổng quan dataset

Mọi con số trong file này là **[Xác minh]**: được tính trực tiếp trên các file tải từ Kaggle ngày 2026-11-11.
Những chỗ ghi **[Suy luận]** là diễn giải từ các con số đó. Đây là **dữ kiện**, không phải gợi ý nên dùng feature hay phương pháp nào.
Tính lại được bằng `python tools/inspect_data.py data/raw` ([tools/](../tools/README.md)).
Được dùng chung trong nhóm (Q-14); không chia sẻ ra ngoài nhóm ([14](14-compliance-and-distribution.md)).

## 1. Nguồn

| Thuộc tính | Giá trị |
|---|---|
| Loại | Competition data. **Không phải** Kaggle Dataset nên không có owner/version riêng |
| Competition | `assignment-data-mining-261` — https://www.kaggle.com/competitions/assignment-data-mining-261/data |
| Host | TU VU NGOC (tên hiển thị trên Kaggle) |
| License | CC BY-NC-SA 4.0 |
| Gói tải về | `assignment-data-mining-261.zip` (208,942 bytes) |
| Cách tải | [10-development-guide.md](10-development-guide.md#3-tải-dữ-liệu) |

Competition data **không có số version công khai**. Để đảm bảo tái lập, hãy so khớp SHA-256 của từng file:

| File | Kích thước (bytes) | Số dòng dữ liệu | SHA-256 |
|---|---:|---:|---|
| `train.csv` | 438,135 | 2,494 | `d591c126e1a7554895a72749f04ea95be199526d1b05ebe42803783d8be4822a` |
| `Test.csv` | 102,926 | 596 | `61d655b2512d8bd27ec593e8a149e172e0e3283e618e1ea0b5840e5f717399d6` |
| `Submission.csv` | 4,701 | 596 | `88a1d0ff0b3b00b8a380fe87d1b353e6cdf2045ef06a571c1149e2ffb8e38816` |

Nếu checksum khác thì host đã thay file. Khi đó phải chạy lại profiling và cập nhật docs (rủi ro R-08).

## 2. Đặc điểm định dạng

| | `train.csv` | `Test.csv` | `Submission.csv` |
|---|---|---|---|
| Header | `id,title,venue,year,authors,doi,Label` | `id,title,venue,year,authors,doi` | `id,priority` |
| Quoting | Chuẩn RFC 4180: field chứa dấu phẩy được quote | **Lỗi: không quote**. Số field mỗi dòng từ 6 đến 16 | Chuẩn |
| Line ending | LF, có newline cuối file | **CRLF, không có newline cuối** | — |
| Encoding | UTF-8, không có BOM, không có ký tự U+FFFD | UTF-8, không có U+FFFD | ASCII |
| Ghi chú | | Đọc bằng `csv`/`pandas` mặc định sẽ **lệch cột âm thầm**. Cần một cách đọc riêng ([07](07-data-processing.md#2-parse-testcsv)) | 596 dòng, **mọi `priority` = 0**; id và thứ tự trùng khớp `Test.csv` |

> Nộp nguyên `Submission.csv` (toàn số 0) sẽ được **score = 0**: danh sách đề xuất rỗng nên Q = 0, mà theo EV thì
> "if either component is zero, the final score is defined as 0". File này chỉ là template.

## 3. Kích thước và phân chia

- Tổng cộng 3,090 bài: 2,494 train và 596 test. Test chia thành **298 Public + 298 Private**; hai tập này bị ẩn và được chấm độc lập.
- `id` train nằm trong khoảng 0–3093, `id` test trong khoảng 713–3085. Hai tập **không trùng id**.
  Có 4 id không xuất hiện ở tập nào: 919, 1347, 2064, 3084.
- **`id` được sắp theo venue rồi đến year giảm dần.** Trong train, các khoảng id theo venue là:
  `iclp` 0–455, `kr` 456–1268, `lpnmr` 1269–1422, `cav` 1423–2301, `lics` 2302–3093. Trong mỗi venue, year không tăng theo id (tỷ lệ 100%).
  Id của test nằm xen kẽ trong cùng các khoảng đó.
  **[Suy luận]** Test được lấy ra từ cùng một danh sách gốc, nên `id` là proxy của venue + year.
- **`id` còn mang tín hiệu về label bên trong mỗi nhóm (venue, year)** **[Xác minh, phát hiện khi audit]**.
  Spearman(id, Label) trung bình có trọng số theo kích thước nhóm là **−0.091**. Permutation test với 300 hoán vị label trong nhóm
  cho z ≈ −4.6, p < 1/300. Nhóm mạnh nhất là `kr` 2019 (n = 40, ρ = −0.52).
  Mean label theo quintile vị trí trong nhóm: 2.50 / 2.50 / 2.52 / 2.43 / **2.21**. Sau khi loại các bài giống front matter:
  2.51 / 2.50 / 2.52 / 2.44 / 2.38.
  **[Suy luận]** Thứ tự gốc trong mỗi kỷ yếu (bài chính trước, bài phụ hay front matter sau) bị lộ qua `id`.
  Đây là **artifact của cách dựng dataset**. Dùng nó làm feature là vấn đề integrity hoặc khả năng giải thích, cần hỏi giảng viên (Q-10).
  Xem [07 §5](07-data-processing.md#5-leakage-checklist).

## 4. Phân phối label

| Label | Ý nghĩa | Số bài | Tỷ lệ | Gain trong metric |
|---:|---|---:|---:|---:|
| 1 | Không muốn đọc | 903 | 36.2% | 0 |
| 2 | Muốn đọc, ưu tiên thấp | 514 | 20.6% | 0.25 |
| 3 | | 438 | 17.6% | 0.50 |
| 4 | | 367 | 14.7% | 0.75 |
| 5 | Ưu tiên cao nhất | 272 | 10.9% | 1.00 |

- **Imbalance:** 63.8% bài là "worthwhile" (label > 1). Label 5 chỉ chiếm 10.9%.

### Theo venue (train)

| venue | n | mean label | % label 1 | Phân phối 1/2/3/4/5 |
|---|---:|---:|---:|---|
| `lpnmr` | 116 | 3.14 | 18% | 21/18/23/32/22 |
| `iclp` | 456 | 2.94 | 26% | 117/78/75/86/100 |
| `kr` | 661 | 2.73 | 27% | 177/134/132/127/91 |
| `cav` | 657 | 2.12 | 46% | 300/135/109/69/44 |
| `lics` | 604 | 1.94 | 48% | 288/149/99/53/15 |

**[Suy luận]** Nhà nghiên cứu quan tâm đến ASP/logic programming/knowledge representation (`lpnmr`, `iclp`, `kr`)
nhiều hơn formal verification (`cav`) và logic in computer science (`lics`). Venue là tín hiệu rất mạnh.

### Theo year (train)

Mean label tăng nhẹ theo thời gian: khoảng 2.18–2.29 giai đoạn 2016–2019 và khoảng 2.36–2.74 giai đoạn 2020–2025.
Tỷ lệ label 1 giảm từ 39–45% xuống 30–38%. Năm 2026 chỉ có 1 bài (một proceedings, label 1).

### Theo đặc điểm title (train)

| Title chứa (không phân biệt hoa thường) | n | mean label | % label 1 |
|---|---:|---:|---:|
| `proceedings` | 56 | 1.00 | 100% |
| `front matter` | 7 | 1.00 | 100% |
| `preface` | 7 | 1.00 | 100% |
| `workshop` | 27 | 1.15 | 96% |
| `short paper` | 8 | 1.50 | 62% |
| `invited` | 7 | 1.86 | 57% |
| `abstract` (gồm cả "extended abstract") | 96 | 2.59 | 29% |

**[Suy luận]** Các bản ghi proceedings, front matter hay preface là bản ghi của cả kỷ yếu, không phải một bài báo, và trong train chúng luôn có label 1.

### Theo các trường khác (train)
- `authors` rỗng (192 bài, 7.7%): mean label 2.28, 47% label 1. Có authors: mean 2.45, 35% label 1.
- `doi` dạng `10.x` (1,458): mean 2.38. Dạng URL Semantic Scholar (1,011): mean 2.53. URL khác (25): mean 1.80, 56% label 1.
- Có 54 tác giả xuất hiện từ 8 bài trở lên trong train. Mean label theo tác giả dao động từ 1.5 đến 3.73.
  **410/596 bài test có ít nhất một tác giả đã xuất hiện trong train.**

## 5. Distribution shift giữa train và test

Bảng dưới là phân bố của test sau khi parse đúng (xem [07](07-data-processing.md#2-parse-testcsv)). **[Xác minh]**

| venue | train n | test n | Ghi chú |
|---|---:|---:|---|
| `cav` | 657 | 221 | |
| `lics` | 604 | 187 | |
| `kr` | 661 | 151 | Test **không có** bài `kr` năm 2017, 2024, 2025. Train có 101 bài kr năm 2024 và 86 bài năm 2025 |
| `lpnmr` | 116 | 37 | Chỉ có các năm 2017, 2019, 2022, 2024, giống train |
| `iclp` | 456 | **0** | **Test không có bài `iclp` nào** |

Số bài test theo năm: 2016: 56, 2017: 51, 2018: 93, 2019: 58, 2020: 75, 2021: 73, 2022: 61, 2023: 47, 2024: 45, 2025: 37.
Test **nghiêng về các năm cũ** hơn train.

**Hệ quả [Suy luận]:**
- `cav` + `lics` chiếm 68% test nhưng chỉ 51% train. Nếu tỷ lệ label 1 theo từng venue của train vẫn giữ nguyên trên test,
  thì test có khoảng **39.8%** bài label 1, so với 36.2% ở train.
- Một tập validation lấy ngẫu nhiên từ train sẽ có phân phối venue/year khác test, vì có `iclp` và nhiều bài năm gần đây hơn.
  Cách xử lý điều này khi thiết kế validation là lựa chọn của mỗi người ([11 §2](11-testing-evaluation.md#2-local-validation)).

## 6. Vấn đề chất lượng dữ liệu

Chi tiết ở [06-data-dictionary.md](06-data-dictionary.md) và [07-data-processing.md](07-data-processing.md).

| # | Vấn đề | Quy mô | Tác động |
|---|---|---|---|
| Q1 | `Test.csv` không quote dấu phẩy | 485/596 dòng có nhiều hơn 6 field. 34 dòng có dấu phẩy trong **title**, nên parse thường bị lệch cả venue và year | Gây lỗi feature âm thầm |
| Q1b | `Test.csv` **bỏ mọi khoảng trắng sau dấu phẩy**: không có chuỗi `", "` nào trong toàn file. Train có 169 title chứa `", "` | Toàn file | So sánh text giữa train và test sẽ bị ảnh hưởng nếu không chuẩn hoá |
| Q2 | Title trùng sau khi chuẩn hoá (train) | 6 nhóm, 16 dòng. **2 nhóm có label mâu thuẫn**: id 110 (3) / 122 (5); id 273 (4) / 1341 (3) | Leak qua fold, nhiễu label |
| Q3 | `doi` không phải định danh duy nhất | 11 giá trị trùng trong train. Một URL `ceur-ws.org/.../abstract2GDE24.pdf` dùng chung cho **25** bài train và 1 bài test. 3 giá trị `doi` trùng giữa train và test nhưng là **các bài khác nhau** | Không được dùng `doi` làm khoá hay để join |
| Q4 | HTML entities trong text | 42 dòng train, 15 dòng test (`&apos;`, `&quot;`, `&eacute;`...) | Tokenization bị sai |
| Q5 | Ký tự hỏng (mojibake) | Ví dụ id 99: chuỗi ký tự Hangul thay cho ký hiệu toán học | Không đáng kể |
| Q6 | Format `authors` khác nhau | Train dùng `", "`. Test sau parse được nối bằng `","` không có khoảng trắng. 1 dòng train dùng dạng "Họ Tên" kèm entity | Phải chuẩn hoá trước khi so khớp tác giả |
| Q7 | `year` lệch với nội dung | Ví dụ id 0: "Proceedings … ICLP 2025" có year 2026 | Không đáng kể |
| Q8 | `venue` của test chỉ chứa 4 giá trị chuẩn sau khi parse đúng | Nếu parse sai sẽ thấy hơn 30 "venue" rác như `CAV 2024`, `Zagreb`... | Dấu hiệu nhận biết parse sai |
| Q9 | `authors` có segment rỗng (ví dụ `", Yushi Cao"`) | train 22, test 7 (trong số các dòng có authors) | Lọc segment rỗng khi tách authors. Đây là đặc điểm của dữ liệu nguồn, không phải lỗi parse |
| Q10 | Tên tác giả viết tắt hoặc một từ (`Govind`, `Krishna` trong test id 2538; train có `R. Govind`) | Ít | So khớp tác giả giữa train và test có thể bỏ sót |

Kiểm tra ranh giới field của `Test.csv` (không chỉ kiểm tra số dòng): xem
[test-csv-notes](../.claude/skills/dataset-integrity/references/test-csv-notes.md). Chạy lại được bằng
`python tools/inspect_data.py data/raw`. Script này chứa các giá trị mong đợi ở mục 1 và mục 4;
khi dữ liệu đổi, **cập nhật cả hai nơi**.

Kiểm tra khác: test **không** có title trùng với train và **không** có title trùng nhau trong nội bộ test (sau khi parse đúng).
Không có giá trị missing ở `title`, `venue`, `year`, `doi`.

## 7. Tái lập và kiểm chứng

1. Tải dữ liệu theo [10-development-guide.md](10-development-guide.md#3-tải-dữ-liệu).
2. So khớp SHA-256 với bảng ở mục 1.
3. Chạy các assertion trong [11-testing-evaluation.md](11-testing-evaluation.md#4-kiểm-tra-dữ-liệu-tự-động-data-checks)
   (số dòng, phân phối label, phân phối venue của test).
