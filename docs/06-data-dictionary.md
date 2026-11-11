# 06 — Data dictionary

Mô tả chính thức của từng cột lấy từ [data-description](reference/competition-pages/data-description.md).
Các cột "Quan sát thực tế" là **[Xác minh]** trên dữ liệu ngày 2026-11-11.

## `train.csv` (2,494 dòng) và `Test.csv` (596 dòng)

| Cột | Mô tả chính thức | Kiểu | Quan sát thực tế | Missing (train / test) |
|---|---|---|---|---|
| `id` | Unique paper identifier | `int` (giữ thêm bản `str` để tie-break) | Train 0–3093, test 713–3085, không trùng nhau. Sắp xếp theo venue rồi year giảm dần ([05 §3](05-dataset-overview.md#3-kích-thước-và-phân-chia)) | 0 / 0 |
| `title` | Paper title | `str` | 2,430/2,494 title train kết thúc bằng dấu `.`. Độ dài từ 1 đến 52 từ, median 8. Có HTML entities. Ở test, 34 title chứa dấu phẩy không được quote | 0 / 0 |
| `venue` | Publication venue | `category` | Chỉ 5 giá trị viết thường: `kr`, `cav`, `lics`, `iclp`, `lpnmr`. Test chỉ có 4 giá trị, **không có `iclp`** | 0 / 0 |
| `year` | Publication year | `int` | Train 2016–2026 (2026 chỉ 1 bài), test 2016–2025 | 0 / 0 |
| `authors` | Paper authors | `list[str]` sau khi chuẩn hoá | Chuỗi tác giả ngăn bởi dấu phẩy. Train có quote; test **không** quote. Tối đa 16 tác giả. Dạng tên "First Last" (có 1 ngoại lệ). Có segment rỗng (train 22, test 7) và tên viết tắt hoặc một từ | **192 / 41** chuỗi rỗng |
| `doi` | Digital Object Identifier | `str` | **Không chỉ chứa DOI.** Train: 1,458 DOI `10.x`, 1,011 URL `semanticscholar.org/paper/<hash>`, 25 URL khác (ví dụ ceur-ws). Test: 359 / 235 / 2. Có trùng lặp giữa các bài khác nhau | 0 / 0 |
| `Label` | Rating 1–5, chỉ có trong train | `int` | 1: 903, 2: 514, 3: 438, 4: 367, 5: 272 | 0 / — |

### Ví dụ dòng (nguyên văn)

`train.csv`, có quote:
```csv
2,Learning and Contesting Assumption-based Argumentation Frameworks (Invited Talk).,iclp,2025,"Ofer Arieli, Jesse Heyninck",https://www.semanticscholar.org/paper/1c433ff0c724aeaa6449948f3f99ec30a20e9bc5,2
```

`Test.csv`, không quote. Dòng này có 9 field trong khi header chỉ có 6:
```csv
979,Explainable Planning Using Answer Set Programming.,kr,2020,Van Nguyen,Stylianos Loukas Vasileiou,Tran Cao Son,William Yeoh,10.24963/kr.2020/66
```

`Test.csv` có dấu phẩy trong title. Parse thường sẽ hiểu nhầm `venue = "Implementation"`:
```text
756,Querying Inconsistent Prioritized Data with ORBITS: Algorithms,Implementation,and Experiments.,kr,...
```

## `Submission.csv` (template)

| Cột | Mô tả | Ràng buộc (FR-01..03) |
|---|---|---|
| `id` | Test id, trùng tập và thứ tự với `Test.csv` | Mỗi id đúng một lần, đủ 596 id |
| `priority` | Template đặt `0` cho mọi dòng | Số thực hữu hạn, không âm. `0` = không đề xuất |

## Ý nghĩa của `Label` trong metric

| Label | Gain g = (y−1)/4 | Tính vào mẫu số Coverage? |
|---:|---:|---|
| 1 | 0.00 | Không |
| 2 | 0.25 | Có |
| 3 | 0.50 | Có |
| 4 | 0.75 | Có |
| 5 | 1.00 | Có |

Xem [08-methodology.md](08-methodology.md#1-phân-tích-metric).
