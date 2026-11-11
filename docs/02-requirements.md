# 02 — Requirements

**Nguồn có thẩm quyền về hành vi mong muốn (intended behavior)** là các trang Kaggle của competition, được sao lưu ở
[reference/competition-pages/](reference/competition-pages/README.md). Tài liệu này chỉ **trích và đánh mã** các yêu cầu đó,
không thêm yêu cầu mới. Nếu cần thay đổi hoặc diễn giải lại một requirement, hãy làm theo
[agents/collaboration-guidelines.md](agents/agent-working-rules.md#2-thay-đổi-requirements).

Viết tắt nguồn: **EV** = [evaluation](reference/competition-pages/evaluation.md),
**DD** = [data-description](reference/competition-pages/data-description.md),
**OV** = [overview-description](reference/competition-pages/overview-description.md),
**AB** = [overview-abstract](reference/competition-pages/overview-abstract.md),
**RU** = [rules](reference/competition-pages/rules.md).

## 1. Functional requirements

| ID | Requirement | Nguồn |
|---|---|---|
| FR-01 | Output là file CSV có **đúng hai cột** `id,priority`, mỗi cột theo đúng tên này | EV, DD, RU §1 |
| FR-02 | File có **đúng 596 dòng dữ liệu**, mỗi test `id` xuất hiện **đúng một lần** | EV, RU §1 |
| FR-03 | `priority` phải là số **hữu hạn và không âm**. `0` = không đề xuất; `> 0` = đề xuất, giá trị càng lớn thì càng được đọc sớm. Thang đo tùy ý, khuyến nghị dùng `[0, 10]` | EV, DD |
| FR-04 | Hệ thống phải dùng **ít nhất một** phương pháp đã học trong môn một cách thực chất: classification, regression, clustering, hoặc itemset-based recommendation (frequent itemsets / association rules). Chỉ nhắc tên phương pháp mà không thực sự dùng trong hệ thống thì **không đạt** | RU §2, OV |
| FR-05 | Báo cáo phải giải thích phương pháp đã học đóng góp vào priority cuối cùng như thế nào, và vai trò của các kỹ thuật bổ sung | RU §2 |
| FR-06 | Repository GitHub phải chứa code sinh ra submission. Repo có thể private nếu cấp quyền truy cập cho teaching team | RU §5 |
| FR-07 | README của repo phải có: (a) file input và dữ liệu bổ sung kèm nguồn và các bước chuẩn bị; (b) cách cài môi trường, **phiên bản dependency**, **random seed**; (c) notebook hoặc lệnh chính xác để train và sinh `id,priority`; (d) quy trình local validation, **kết quả validation mong đợi**, hướng dẫn tái lập submission đã chọn; (e) phần cứng, thời gian chạy ước tính, các hạn chế ảnh hưởng đến việc tái lập | RU §5 |
| FR-08 | Báo cáo phải có GitHub URL, **final commit hash**, Kaggle team name, submission identifier(s); tên, MSSV và đóng góp của từng thành viên | RU §1, §5 |
| FR-09 | Lưu lại **chính xác** file CSV đã nộp | RU §5 |
| FR-10 | Chọn submission cuối cùng trên Kaggle trước deadline, với số lượng mà competition cho phép | RU §1 |

## 2. Non-functional requirements

| ID | Requirement | Nguồn |
|---|---|---|
| NFR-01 | **Reproducibility:** kết quả phải tái lập được từ dữ liệu có sẵn. Kết quả không tái lập được thì không đạt điểm tối đa phần implementation/evaluation | RU §5 |
| NFR-02 | **Fair evaluation:** so sánh các phương pháp trên **cùng các validation partition** và cùng quy tắc tính điểm. Giải thích cách split xử lý duplicate hoặc các bài liên quan đến nhau | RU §7 |
| NFR-03 | Báo cáo phải có **điểm từng thành phần** (Relevance, Coverage) và các lỗi điển hình, không chỉ báo con số tổng tốt nhất | RU §6, §7 |
| NFR-04 | Không coi việc tune lặp lại trên Public LB là bằng chứng độc lập về khả năng generalization | RU §7 |
| NFR-05 | Nếu dùng metadata của test theo cách unsupervised (ví dụ fit TF-IDF hoặc clustering trên train và test gộp lại), phải **công khai** điều đó và dùng cùng một protocol nhất quán trong local validation | RU §7 |
| NFR-06 | External data, pretrained model, code bên thứ ba đều được phép nếu **truy cập công khai**, được **trích dẫn** và giải thích | RU §7 |
| NFR-07 | Tuân thủ submission limit (3 lần/ngày) và deadline trên Kaggle và LMS | RU §1, metadata competition |
| NFR-08 | **Bảo mật:** không commit Kaggle credentials hoặc token. Yêu cầu này do nhóm đặt ra cho repo, không có trong Rules | Quy ước dự án |

## 3. Integrity (bắt buộc)

| ID | Cấm | Nguồn |
|---|---|---|
| INT-01 | Tìm cách lấy hidden test labels hoặc tự dựng answer key cho test | RU §7 |
| INT-02 | Suy ngược tập nào thuộc Public, tập nào thuộc Private | RU §7 |
| INT-03 | Khai thác feedback của leaderboard để suy ra nhãn từng bài, ví dụ nộp các file chỉ khác nhau ở một bài | RU §7 |
| INT-04 | Trao đổi implementation, file submission hoặc lời giải hoàn chỉnh với team khác. Thảo luận chung thì được phép | RU §7, Kaggle foundational rules §5d, §6a |
| INT-05 | Dùng hand labeling hoặc human prediction trên test data | Kaggle foundational rules §4b |
| INT-06 | Mỗi người chỉ dùng **một** tài khoản Kaggle và chỉ thuộc **một** team | Kaggle foundational rules §5; RU §1 |
| INT-07 | **Chia sẻ riêng tư code hoặc data với người ngoài nhóm**. Trong nhóm 5 người: giảng viên đã cho phép (Q-14). Chia sẻ công khai trên forum hoặc notebook của competition thì được | Kaggle foundational rules §5d, §6a–b |

## 3b. Team và submission (luật Kaggle)

Nguồn: Kaggle foundational rules (tab Rules, không có trong snapshot ở `reference/`) và metadata competition, lấy ngày 2026-11-11.
Hệ quả đối với việc phân phối và việc thi độc lập: [14-compliance-and-distribution.md](14-compliance-and-distribution.md).

| ID | Luật | Nguồn |
|---|---|---|
| TEAM-01 | Mỗi team tối đa **3 submission/ngày** | Metadata `max_daily_submissions = 3`; foundational §5a |
| TEAM-02 | Phải đăng ký cá nhân trước khi vào team; phải **xác nhận** lời mời | Foundational §5b |
| TEAM-03 | Gộp team được phép nếu: (i) không vượt Max Team Size; (ii) tổng submission của các team gộp ≤ số submission được phép của một team tại ngày yêu cầu gộp; (iii) gộp xong trước merger deadline hoặc deadline competition, tùy cái nào sớm hơn; (iv) thỏa các luật khác | Foundational §5c |
| TEAM-04 | Merger deadline riêng: API báo không có (`None`) | API competition |

## 4. Rubric báo cáo (R)

Theo [RU §6](reference/competition-pages/rules.md). Tổng điểm là 10.

| # | Tiêu chí | Điểm | Cần có để đạt tối đa (tóm tắt) |
|---|---|---:|---|
| 1 | Presentation & clarity | 1.0 | Cấu trúc mạch lạc, thuật ngữ chính xác, hình và bảng dễ đọc, có trích dẫn |
| 2 | Problem formulation & domain understanding | 1.5 | Xác định stakeholder, nhu cầu đọc, input/output, constraint, ý nghĩa của relevance/coverage, liên hệ giữa metric và mục tiêu thực tế |
| 3 | Data analysis | 1.5 | Phân phối, missing values, duplicates, label imbalance, đặc điểm metadata/text, các quan hệ liên quan đến bài toán; giải thích lựa chọn cleaning bằng bằng chứng |
| 4 | Insights | 1.5 | Phát hiện cụ thể có bằng chứng; tách rõ quan sát với giả định; nêu hệ quả và kỳ vọng kiểm chứng được |
| 5 | Solution design & implementation | 2.0 | Biện minh cho lựa chọn, liên hệ với insight, mô tả preprocessing, representation, thuật toán, setting; có phương pháp đã học; tái lập được từ GitHub |
| 6 | Evaluation, error analysis, fairness | 2.0 | Validation design có lý do; dùng metric của competition; so sánh với baseline trong cùng điều kiện; phân tích Q/R, ranking failure; đề cập leakage, sampling bias, LB overfitting, variance |
| 7 | Conclusions | 0.5 | Tóm tắt điều bằng chứng ủng hộ, hạn chế, những gì có thể generalize, hướng tiếp theo |

Báo cáo phải đi theo chuỗi **domain understanding → data analysis → insights → solution choices → implementation → evaluation → conclusions**.
Liệt kê tool, đưa plot không giải thích, hay chụp màn hình leaderboard **không** được tính là insight.

## 5. Mâu thuẫn giữa các nguồn (chưa giải quyết)

Các mâu thuẫn dưới đây **chưa được giải quyết**. Không được âm thầm chọn một phía. Mỗi mâu thuẫn được theo dõi như một câu hỏi
trong [13-risks-open-questions.md](13-risks-open-questions.md).

| ID | Mâu thuẫn | Nguồn A | Nguồn B | Cách làm tạm thời |
|---|---|---|---|---|
| C-01 | **Định nghĩa Coverage** | AB: *"coverage measured through title similarity across all reading-list lengths"*; RU §1: *"provide broad title coverage"* | EV: Coverage = recall của các bài có rating > 1; *"title similarity is not part of the metric"* | Tạm coi **EV** là đúng vì trang này chi tiết nhất và có công thức. Không tối ưu theo title diversity cho đến khi được xác nhận (Q-01) |
| C-02 | **Số thành viên tối đa** | RU §1, OV, AB: tối đa **5** | Cài đặt Kaggle `maxTeamSize = 6` | Tạm theo **5**, quy định khắt khe hơn (Q-02) |
| C-03 | **Tên file dữ liệu** | DD: `test.csv`, `sample_submission.csv` | File thực tế: `Test.csv`, `Submission.csv` | Code dùng tên file thực tế. Trên Windows tên file không phân biệt hoa thường, nhưng Linux/Kaggle thì có (Q-08) |
| C-04 | **Format `Test.csv`** | DD: các cột `id,title,venue,year,authors,doi` | File thực tế không quote dấu phẩy trong `title`/`authors`; số field mỗi dòng từ 6 đến 16 | Cần cách đọc riêng, xem [07 §2](07-data-processing.md#2-parse-testcsv) (Q-08) |
| C-05 | **"Baseline" cho mức điểm sàn 6.5** | RU §4: *"Public score lower than Public score of Baseline"* | LB có hai entry tên `baseline_submission.csv` (0.66962 và 0.60953) | Mục tiêu an toàn là vượt **0.66962** (Q-03) |
| C-06 | **Thứ hạng tính trên ai** | RU §4: chỉ tính "eligible course teams" | LB có cả entry baseline | Không ảnh hưởng đến code, chỉ ảnh hưởng ước lượng điểm L |
