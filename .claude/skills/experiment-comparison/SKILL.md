---
name: experiment-comparison
description: Compare the candidate experiments of ONE student's own solution with evidence - compliance gates, offline metrics under the same protocol, stability across folds and seeds, Public leaderboard as a noisy signal, reproducibility, complexity and explainability - to choose what to submit next or which submission to select as final, and record the decision. Never ranks by best Public score alone. Use when asked "so sánh các thí nghiệm / chọn bản nào để nộp / chọn final".
---

# experiment-comparison

## Mục đích
Chọn ứng viên nộp bài, hoặc final submission, **trong các thí nghiệm của chính sinh viên** bằng một quy trình công bằng và có ghi chép.

## Khi nào dùng
- Có từ 2 ứng viên trở lên trong `experiments/EXPERIMENTS.md`.
- Trước khi chọn final submission trên Kaggle (Q-05), hoặc trước khi viết phần "Solution design" của báo cáo.

## Khi nào KHÔNG dùng
- Để chọn người có lời giải tốt nhất trong nhóm: theo gợi ý của giảng viên, đó là người **có điểm cao nhất** ([14](../../../docs/14-compliance-and-distribution.md)).
- Khi các ứng viên chạy trên protocol khác nhau. Hãy chạy lại chúng trên cùng protocol trước.

## Ngữ cảnh cần có
Log thí nghiệm, scorer đã qua T1–T9, protocol cố định, `submissions/LOG.md` (nếu đã nộp).

## Tài liệu liên quan
[templates/final-solution-summary.md](../../../docs/templates/final-solution-summary.md) · [11 §2](../../../docs/11-testing-evaluation.md#2-local-validation) ·
[08 §2](../../../docs/08-methodology.md#2-ràng-buộc-từ-requirements-khi-thiết-kế-lời-giải) · [02 §4](../../../docs/02-requirements.md#4-rubric-báo-cáo-r)

## Quy trình
1. **Chốt tiêu chí trước khi xem bảng.** Tiêu chí do thành viên tự chọn. Ví dụ hay dùng: local score theo protocol của bạn, độ ổn định
   (std, số fold thua baseline), Public LB (là tín hiệu có nhiễu), độ khớp giữa local và Public, khả năng tái lập, độ phức tạp,
   khả năng giải thích cho báo cáo. Ghi lại tiêu chí đã chọn.
2. **Gate:** FR-04, INT-01..07, tái lập được, submission hợp lệ, đã công khai việc dùng metadata của test hay artifact `id` nếu có. Không đạt thì loại.
3. **Chạy lại** mọi ứng viên trên **cùng** scorer, fold và seed.
4. **Bảng so sánh** kèm std. Các cặp có chênh lệch nhỏ hơn khoảng 1 std thì coi là ngang nhau, và quyết định dựa vào độ ổn định, độ phức tạp, khả năng giải thích.
5. **Quyết định:** không chọn chỉ vì Public LB cao nhất. Có thể ensemble, nhưng ensemble phải được đánh giá như một ứng viên mới.
6. **Ghi lại:** ADR cục bộ "chọn lời giải cuối cùng" và `final-solution-summary.md`.

## Output
Bảng so sánh, quyết định có lý do, ADR cục bộ và solution summary.

## Acceptance criteria
- Tiêu chí được chốt trước khi xem kết quả. Mọi số liệu tái lập được bằng lệnh. Có nêu rủi ro overfit Public.

## Lỗi và escalation
- Ứng viên không tái lập được: loại cho đến khi sửa được.
- Local và Public mâu thuẫn mạnh: cân nhắc nhiễu và shift ([interpretation](../validation-and-scoring/references/interpretation.md)), ghi rõ trong ADR, báo thành viên.

## Ràng buộc
Chỉ dùng thí nghiệm trong bản clone này. Không nộp bài để "phân xử".

## Ví dụ
- "EXP-007 Public 0.680, EXP-009 Public 0.674 nhưng local của EXP-009 tốt hơn" → chạy lại cả hai, xem std; áp dụng tiêu chí đã chốt, ghi lý do và rủi ro overfit.
