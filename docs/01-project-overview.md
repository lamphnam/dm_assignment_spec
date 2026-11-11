# 01 — Tổng quan dự án

## 1. Bối cảnh

- **Môn học:** CO3029 (Data Mining). Mã môn lấy từ tiêu đề trang Rules: *"CO3029 Assignment Rules and Report Rubric"*. **[Xác minh]**
- **Competition:** [Assignment Data Mining - 261](https://www.kaggle.com/competitions/assignment-data-mining-261)
  (slug `assignment-data-mining-261`, id `170622`). Category Community, reward Kudos, host hiển thị là *TU VU NGOC*. **[Xác minh]**
- **License dữ liệu:** CC BY-NC-SA 4.0 (trường `licenseName` của competition). **[Xác minh]**
- Thư mục làm việc nằm trong `hk261/DM/`. "261" nhiều khả năng là mã học kỳ. **[Suy luận]**

## 2. Bài toán

Một nhà nghiên cứu cần biết **nên đọc bài báo nào tiếp theo**. Có 3,090 bài báo (metadata: `title`, `venue`, `year`,
`authors`, `doi`), trong đó:

- **Train:** 2,494 bài, có `Label` từ 1 đến 5 thể hiện sở thích đọc của *một* nhà nghiên cứu.
  - **1** = không muốn đọc.
  - **2–5** = muốn đọc, độ ưu tiên tăng dần.
- **Test:** 596 bài, label bị ẩn.

**Output:** với mỗi bài trong test, đưa ra một số `priority ≥ 0`.

- `priority = 0` nghĩa là **không đề xuất** bài đó.
- `priority > 0` nghĩa là đề xuất, và số càng lớn thì bài càng được đọc sớm.

**[Xác minh]**: trích từ [data-description](reference/competition-pages/data-description.md) và [evaluation](reference/competition-pages/evaluation.md).

Đây là bài toán **ranking kèm selection** (chọn bài và sắp thứ tự), không phải dự đoán đúng nhãn 1–5. Evaluator chỉ dùng
**thứ tự** và **tập được chọn**, không quy đổi priority thành rating. Chi tiết metric: [08-methodology.md](08-methodology.md#1-phân-tích-metric).

### Stakeholder và nhu cầu

- **Nhà nghiên cứu (người dùng cuối):** muốn bài hay nhất xuất hiện ở đầu danh sách, đồng thời không bỏ sót bài đáng đọc.
  Hai nhu cầu này tương ứng với hai thành phần của metric là **Relevance** và **Coverage**.
- **Giảng viên:** chấm theo vị trí trên Private LB (60%) và báo cáo (40%). Báo cáo phải chứng minh được tư duy data mining.
- Nhãn phản ánh **sở thích cá nhân**, không phải chất lượng khoa học. **[Xác minh]**
- Bạn tự tìm hiểu sở thích của nhà nghiên cứu qua dữ liệu train. Đây là phần "Data analysis" và "Insights" của rubric.

## 3. Deliverables

Theo [Rules §5](reference/competition-pages/rules.md). **[Xác minh]**

| # | Deliverable | Ghi chú |
|---|---|---|
| D1 | Submission hợp lệ trên Kaggle và submission cuối cùng được chọn | 596 dòng `id,priority` |
| D2 | GitHub repository chứa code sinh ra submission | Có thể để private nếu cấp quyền cho teaching team (email trong Rules §5) |
| D3 | Báo cáo | Phải có GitHub URL, **final commit hash**, Kaggle team name, submission ID; tên, MSSV và đóng góp của từng thành viên |
| D4 | README repository đủ thông tin để tái lập kết quả | Danh sách mục bắt buộc ở [12-reproducibility.md](12-reproducibility.md) |
| D5 | Bản lưu **chính xác** file CSV đã nộp | Không được sinh lại file khác rồi coi như bản đã nộp |

## 4. Chấm điểm môn học

**[Xác minh]**, theo Rules §3–§4:

\[ A = 0.60\,L + 0.40\,R \] (thang 0–10, làm tròn tới 0.5 gần nhất)

- **L (ranking grade)** được quy đổi từ **vị trí trên Private LB** trong số các team hợp lệ của lớp:

  | Vị trí | L |
  |---|---:|
  | Top 10% | 10.0 |
  | >10–20% | 9.5 |
  | >20–30% | 9.0 |
  | >30–40% | 8.75 |
  | >40–50% | 8.5 |
  | >50–60% | 8.25 |
  | >60–70% | 8.0 |
  | >70–80% | 7.75 |
  | >80–90% | 7.5 |
  | >90–100% | 7.0 |
  | **Public score thấp hơn Public score của Baseline** | **6.5** |

  Mốc cắt được làm tròn lên bằng `ceil(p × N)`. Team có Private score bằng nhau thực sự (không chỉ bằng nhau khi làm tròn hiển thị)
  nhận cùng mức điểm.
- **R (report grade)** chấm theo rubric 7 tiêu chí ([02-requirements.md](02-requirements.md#4-rubric-báo-cáo-r)).
  Hai tiêu chí nặng nhất là *Solution design* (2.0) và *Evaluation/error analysis/fairness* (2.0).

> Cần phân biệt **raw Kaggle score** (harmonic mean của Q và R, thang 0–1) với **ranking grade L**.
> L không bằng raw score × 10.

## 5. Timeline và giới hạn

| Mục | Giá trị | Nhãn |
|---|---|---|
| Competition mở | 2026-10-13 18:14 UTC (`enabledDate`) | [Xác minh] |
| Deadline Kaggle | **2026-12-14 23:59:59 UTC**, tức 06:59:59 sáng 2026-12-15 giờ Việt Nam | [Xác minh] |
| Số lần nộp tối đa | **3 submission/ngày/team** (`max_daily_submissions`), không phải 3 submission tổng | [Xác minh] |
| Merger deadline riêng | API trả về `None`, nên mốc giới hạn là deadline competition (Kaggle rules §5c(iii)) | [Xác minh] (API). Chưa đối chiếu trên website |
| Kích thước team | Kaggle cho tối đa 6; Rules môn học cho tối đa 5 | [Xác minh]. Mâu thuẫn C-02 |
| Deadline nộp báo cáo/repo trên LMS | **Chưa biết** | [Chưa rõ], câu hỏi Q-04 |
| Số submission cuối được chọn | **Chưa biết** | [Chưa rõ], câu hỏi Q-05 |
| Công bố điểm | Khoảng 2 tuần sau khi assignment kết thúc | [Xác minh] |

## 6. Tình trạng leaderboard

Public LB tại thời điểm snapshot 2026-11-11 (~11:15 UTC). **[Xác minh]**

- 25 entry. Score cao nhất **0.68281**, thấp nhất 0.60953.
- Có **hai** entry cùng tên `baseline_submission.csv`:
  - Score **0.66962**, 41 lần nộp, xếp thứ 6.
  - Score **0.60953**, 1 lần nộp ngày 2026-10-13, xếp cuối.
- Entry 0.60953 có `LastSubmissionDate` là 2026-10-13 17:35:58, gần thời điểm competition mở (`enabledDate` 18:14 UTC;
  múi giờ của cột ngày trong file LB chưa được xác nhận). Nhiều khả năng đây là baseline của host. Entry 0.66962 có thể là
  một team sinh viên đặt trùng tên. **[Suy luận]** Vì không rõ entry nào là "Baseline" dùng cho mức sàn 6.5,
  đây là câu hỏi Q-03 cần hỏi giảng viên.
- Khoảng cách giữa các team rất nhỏ: top 3 đều nằm trong khoảng 0.673–0.683. Mỗi split chỉ có 298 bài, nên nhiễu là đáng kể.
  Xem [13-risks-open-questions.md](13-risks-open-questions.md).
- Leaderboard thay đổi liên tục. Hãy xem bản mới nhất trên Kaggle.

## 7. Thi độc lập

Repo giả định **mỗi thành viên tự làm lời giải và tự quản lý việc tham gia Kaggle** bằng tài khoản của mình.
Cần lưu ý:
- Quota là **3 submission/ngày/team**.
- Giảng viên cho phép: nộp độc lập; 5 người chia sẻ thoải mái với nhau; **cuối kỳ 4 người join team của người có điểm cao nhất** (Q-11..Q-14).
- Việc gộp phải thỏa điều kiện §5c của Kaggle, gồm **trần tổng submission** và deadline.

Xem [14-compliance-and-distribution.md](14-compliance-and-distribution.md).

## 8. Tài liệu liên quan

- Requirements chi tiết: [02-requirements.md](02-requirements.md)
- Dữ liệu: [05-dataset-overview.md](05-dataset-overview.md)
- Metric và hướng tiếp cận: [08-methodology.md](08-methodology.md)
