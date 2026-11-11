---
name: dataset-integrity
description: Obtain, load and inspect the assignment-data-mining-261 competition files reproducibly in the member's clone - checksums, schema, reading the inconsistently quoted Test.csv correctly, value-level field checks, duplicates, train/test shift and leakage artefacts - using the verified findings in docs/05-07 and the optional tools/inspect_data.py as cross-checks. Use after downloading data, when a loader gives odd columns, or when asked about data quality, duplicates or leakage ("kiểm tra dữ liệu").
---

# dataset-integrity

## Mục đích
Thành viên có dữ liệu **được đọc đúng** và hiểu các đặc điểm hay bẫy của nó, đủ dùng cho phần Data analysis của báo cáo.
Đặc điểm nào **quan trọng cho lời giải** thì thành viên tự đánh giá.

## Khi nào dùng
Sau khi tải dữ liệu; khi viết hoặc đổi loader; khi cần số liệu cho báo cáo (rubric tiêu chí 3–4); khi nghi ngờ leakage.

## Khi nào KHÔNG dùng
Để train hay chọn model (dùng `independent-experiment`). Để suy luận nhãn ẩn của test (cấm, INT-01..03).

## Ngữ cảnh cần có
`data/raw/` có `train.csv`, `Test.csv`, `Submission.csv`. Nếu chưa có: `kaggle-research` hoặc [10 §3](../../../docs/10-development-guide.md#3-tải-dữ-liệu).

## Tài liệu liên quan
[05](../../../docs/05-dataset-overview.md) (các phát hiện đã kiểm chứng) · [06](../../../docs/06-data-dictionary.md) · [07](../../../docs/07-data-processing.md) ·
[references/test-csv-notes.md](references/test-csv-notes.md) · [tools/inspect_data.py](../../../tools/README.md) · [14](../../../docs/14-compliance-and-distribution.md)

## Quy trình
1. **Đối chiếu nhanh (tùy chọn):** `python -I tools/inspect_data.py data/raw`. Kết quả 0 FAIL nghĩa là dữ liệu trùng với snapshot đã phân tích trong 05.
   Nếu checksum khác thì dữ liệu đã đổi: các con số trong 05 có thể không còn đúng.
2. **Đọc dữ liệu cho lời giải:** dùng cách đọc đã kiểm chứng ở [07 §2](../../../docs/07-data-processing.md#2-parse-testcsv), hoặc tự xây cách khác.
   Dù chọn cách nào, phải assert theo [11 §4](../../../docs/11-testing-evaluation.md#4-kiểm-tra-dữ-liệu-tự-động-data-checks) và kiểm tra **giá trị**
   của các dòng phức tạp (ví dụ 756, 1368, 979), không chỉ số dòng.
3. **Hiểu dữ liệu:** đọc 05–07, rồi kiểm chứng hoặc mở rộng theo câu hỏi của chính thành viên. Phân tích nào đáng làm, và kết luận gì cho lời giải,
   là do thành viên và agent tự quyết định.
4. **Leakage:** rà [07 §5](../../../docs/07-data-processing.md#5-leakage-checklist), đặc biệt artifact `id` (Q-10).
5. **Ghi lại** các phân tích mới vào tài liệu cục bộ (ví dụ `reports/`), kèm lệnh để tính lại và nhãn [Xác minh]/[Suy luận].

## Output
Một cách đọc dữ liệu đã được kiểm chứng; các phân tích của thành viên; danh sách bẫy dữ liệu liên quan đến lời giải của họ.

## Acceptance criteria
Đọc đúng 596 dòng test với mọi trường hợp lệ; checksum đã được ghi lại; mọi con số chạy lại được.

## Lỗi và escalation
Dòng không đọc được hoặc mơ hồ: dừng, đưa ví dụ cho thành viên, không đoán. Checksum khác với 05: báo thành viên.

## Ràng buộc
Không sửa `data/raw/`; không commit dữ liệu. Luật chia sẻ giữa các team: [14](../../../docs/14-compliance-and-distribution.md).

## Ví dụ
- "Tải xong rồi, kiểm tra giúp" → chạy `tools/inspect_data.py`, tóm tắt các điểm chính trong 05, hỏi thành viên muốn đào sâu phần nào.
- "Sao Test.csv đọc ra 9 cột?" → giải thích quoting (05 §2, 07 §2), cùng chọn cách đọc, assert từng trường.
