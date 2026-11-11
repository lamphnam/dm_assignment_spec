# 13 — Rủi ro và câu hỏi mở

Các câu hỏi Q-11..Q-14 (thi độc lập, chia sẻ, gộp team) **đã được giảng viên trả lời**: xem [14](14-compliance-and-distribution.md#câu-trả-lời-của-giảng-viên-2026-11-11-nhóm-truyền-đạt-lại).
Khi bạn có câu trả lời, ghi câu trả lời, nguồn và ngày vào bản clone của bạn.

## 1. Câu hỏi về luật và metric

| ID | Câu hỏi | Vì sao quan trọng | Hỏi ai | Trạng thái |
|---|---|---|---|---|
| Q-01 | Coverage thực sự được tính thế nào: là recall như trên trang Evaluation, hay dựa trên "title similarity across all reading-list lengths" như trong abstract? (C-01) | Quyết định có cần đa dạng hoá theo chủ đề hay không | Giảng viên hoặc forum | Mở. Tạm theo EV (ADR-0005) |
| Q-02 | Mỗi team tối đa 5 hay 6 thành viên? (C-02) | Hợp lệ của team | Giảng viên | Mở. Tạm theo 5 |
| Q-03 | "Baseline" trong mức sàn 6.5 là entry 0.66962 hay 0.60953? (C-05) | Ngưỡng tối thiểu cần vượt | Giảng viên | Mở. Mục tiêu an toàn là > 0.66962 |
| Q-04 | Deadline nộp báo cáo/repo trên LMS? Báo cáo cần format hay độ dài cụ thể không? | Kế hoạch thời gian | LMS hoặc giảng viên | Mở |
| Q-05 | Được chọn bao nhiêu final submission? | Chọn bài nộp cuối | Trang Submissions trên Kaggle | Mở |
| Q-07 | Có được lấy dữ liệu ngoài *cho chính các bài test* (ví dụ abstract qua DOI) không? Rules cho phép dữ liệu ngoài công khai nếu được trích dẫn, nhưng chưa nói rõ trường hợp này | Có thể cải thiện representation | Giảng viên | Mở |
| Q-08 | Lỗi quoting của `Test.csv` và việc tên file khác mô tả có phải cố ý không? Host có thay file không? (C-03, C-04) | Checksum hoặc cách đọc có thể phải đổi | Forum | Mở |
| Q-10 | Có được dùng `id`, hoặc thứ tự `id` trong mỗi nhóm (venue, year), làm feature không? Đây là artifact của cách dựng dataset và có tương quan với label ([05 §3](05-dataset-overview.md#3-kích-thước-và-phân-chia)) | Integrity và khả năng giải thích | Giảng viên | Mở |
| Q-09 | Rules §1 nói "broad title coverage". Đó có phải mục tiêu định tính trong báo cáo không, khi metric (theo EV) không đo điều này? | Cách trình bày báo cáo | Giảng viên | Mở |

## 2. Rủi ro khi làm lời giải

Khả năng (L) và Tác động (I) theo thang Thấp (T), Trung bình (TB), Cao (C).

| ID | Rủi ro | L | I | Giảm thiểu |
|---|---|---|---|---|
| R-01 | **Overfit Public LB**: mỗi split chỉ có 298 bài, các team ở top chênh nhau rất ít | C | C | Chọn model theo local validation (mean ± std); hạn chế số lần nộp (NFR-04) |
| R-02 | **Distribution shift giữa train và test** (test không có `iclp`, nhiều `cav`/`lics` hơn, nghiêng về năm cũ) | Đã xác nhận | C | Tính đến khi thiết kế validation ([05 §5](05-dataset-overview.md#5-distribution-shift-giữa-train-và-test), [11 §2](11-testing-evaluation.md#2-local-validation)) |
| R-03 | **Đọc sai `Test.csv`** làm feature lệch âm thầm | C nếu dùng `read_csv` | C | Assertion sau khi đọc ([07 §2](07-data-processing.md#2-parse-testcsv), [11 §4](11-testing-evaluation.md#4-kiểm-tra-dữ-liệu-tự-động-data-checks)) |
| R-04 | **Leakage trong CV** qua duplicate, khoá giả, target encoding fit ngoài fold, artifact của `id` hay thứ tự | TB | TB–C | Leakage checklist ([07 §5](07-data-processing.md#5-leakage-checklist)) |
| R-05 | **Scorer cài sai** (tie-break, log base, trường hợp biên) | TB | C | Test case T1–T9 ([11 §1](11-testing-evaluation.md#1-đặc-tả-offline-scorer)) |
| R-06 | **Lộ Kaggle token** | TB | C | Chỉ dùng biến môi trường. Lộ thì tạo token mới ([integrations §3](integrations/kaggle-mcp-setup.md#3-credentials)) |
| R-07 | **Định nghĩa Coverage khác EV** (Q-01) | T–TB | C | Theo dõi forum; báo cáo phân tích cả hai cách hiểu |
| R-08 | **Host thay dữ liệu** | T | TB | Kiểm tra checksum ở mỗi lần chạy |
| R-09 | **Deadline và quota** (3 lượt/ngày; deadline 2026-12-14 23:59:59 UTC) | TB | TB | Không dùng quota cho thử nghiệm chưa được validate |
| R-10 | **Vi phạm integrity**, ví dụ dò nhãn qua LB | T | Rất cao | Tuân INT-01..07 |
| R-11 | **Python quá mới** với một số thư viện (3.14) | TB | T | Dùng 3.11/3.12 nếu gặp lỗi; ghi vào README |
| R-12 | **Gộp team cuối kỳ thất bại**: tổng submission của nhóm vượt trần, hoặc chưa ai chấp nhận lời mời trước deadline | TB | Rất cao | Theo dõi tổng số lượt của cả nhóm; gộp sớm ([14](14-compliance-and-distribution.md#gộp-team-cuối-kỳ-điều-kiện-của-kaggle)) |
| R-13 | **Chia sẻ code hay data ra ngoài nhóm** | T | Cao | INT-07 |

## 3. Giả định đang dùng

| ID | Giả định | Dựa trên | Nếu sai thì |
|---|---|---|---|
| A-01 | Metric đúng như trang Evaluation | EV chi tiết nhất | Xem lại policy chọn bài; có thể cần diversification |
| A-02 | Label train và test do cùng một nhà nghiên cứu gán, theo cùng tiêu chí | Data description | Model generalize kém |
| A-03 | Public và Private được chọn ngẫu nhiên từ 596 bài | Không có mô tả ngược lại | Các ước lượng std có thể sai |
| A-06 | Quota được tính lại theo ngày UTC | Thông lệ của Kaggle | Lịch nộp bị lệch |
