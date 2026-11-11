---
name: submission-management
description: Prepare, validate and log the student's own Kaggle submission for assignment-data-mining-261 WITHOUT submitting it - quota check (3 per day per team), local-validation prerequisite, id,priority format validation, SHA-256 and experiment-to-submission traceability, then recording the Public score after the student submits. Use when the student wants to submit, asks about remaining submissions, or "nộp bài / còn bao nhiêu lượt / ghi điểm LB".
---

# submission-management

## Mục đích
Mỗi lượt nộp của sinh viên phải **có lý do**, **hợp lệ** và **truy vết được**. Skill này chuẩn bị mọi thứ, còn **sinh viên tự nộp**.

## Khi nào dùng
- Trước khi nộp bài; sau khi nộp, để ghi Public score; khi cần biết quota còn lại.

## Khi nào KHÔNG dùng
- Khi file định nộp chưa có kết quả local: quay lại `independent-experiment`.
- Để dò nhãn hay split bằng nhiều lần nộp: bị cấm (INT-03).

## Ngữ cảnh cần có
File CSV định nộp, EXP id tương ứng, `data/raw/Test.csv`, `submissions/LOG.md` (copy từ template).

## Tài liệu liên quan
[11 §3](../../../docs/11-testing-evaluation.md#3-validator-cho-submission) · [templates/submission-log.md](../../../docs/templates/submission-log.md) ·
[12 §3](../../../docs/12-reproducibility.md#3-manifest-cho-mỗi-submission) · [10 §4](../../../docs/10-development-guide.md#4-nộp-bài-lên-kaggle) ·
[14](../../../docs/14-compliance-and-distribution.md)

## Quy trình
1. **Điều kiện tham gia và ngân sách nhóm:** thành viên đã tham gia competition bằng tài khoản của mình. Cuối kỳ cả nhóm gộp vào một team, nên
   **tổng số lượt của 5 người** phải dưới trần ở ngày dự kiến gộp ([14](../../../docs/14-compliance-and-distribution.md#gộp-team-cuối-kỳ-điều-kiện-của-kaggle)).
   Nhắc thành viên đối chiếu tổng số lượt của nhóm trước khi nộp. Thành viên quyết định có nộp hay không.
2. **Quota:** xem trên trang Submissions (hoặc `kaggle competitions submission-limits …`), đối chiếu với log.
3. **Bằng chứng local:** EXP tương ứng phải tốt hơn submission trước, và chênh lệch vượt mức nhiễu. Nếu không, khuyến nghị chưa nộp.
4. **Validate file** theo checklist ở 11 §3: dùng `python -I tools/validate_submission.py <file> --test data/raw/Test.csv` (tùy chọn), hoặc validator riêng, kiểm tra:
   header đúng; đủ 596 id, không thiếu, không thừa, không trùng; priority hữu hạn và ≥ 0; có ít nhất một priority > 0; cảnh báo khi có tie.
5. **Truy vết:** tính SHA-256; ghi EXP id, commit, config, seed vào `submissions/LOG.md`. Không ghi đè file.
6. **Bàn giao cho sinh viên:** đưa lệnh để sinh viên **tự** chạy, hoặc hướng dẫn nộp qua web:
   `kaggle competitions submit -c assignment-data-mining-261 -f <file> -m "<EXP-id> <commit>"`. **Agent không chạy lệnh này.**
7. **Sau khi có điểm:** ghi Public score, submission ID, độ lệch so với local. Nếu lệch nhiều, chuyển sang `validation-and-scoring`.

## Output
Kết quả validate, dòng log đầy đủ, và khuyến nghị "nộp" hoặc "chưa nộp" kèm lý do.

## Acceptance criteria
- File hợp lệ; SHA-256 trong log khớp file; có EXP id và kết quả local.
- Agent không gọi `competition_submit` hay `kaggle competitions submit`.

## Lỗi và escalation
- File không hợp lệ: sửa code sinh file, không sửa tay CSV.
- Hết quota: dừng, báo sinh viên.
- Sinh viên yêu cầu agent nộp thay: nhắc quy tắc là sinh viên tự nộp. Chỉ làm khi sinh viên xác nhận rõ ràng sau khi checklist đã đạt, và ghi lại việc đó vào log.

## Ràng buộc
Không nộp tự động, không đổi team hay gửi lời mời gộp. Không chia sẻ submission ra ngoài nhóm. Không ghi token.

## Ví dụ
- "Mình muốn nộp model mới" → kiểm tra quota, so local với lần trước, validate, ghi log, đưa lệnh để sinh viên tự nộp.
- "Kaggle báo 0.671, ghi lại giúp" → cập nhật log, tính độ lệch so với local.
