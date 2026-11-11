---
name: assignment-onboarding
description: Onboard a group member (or their AI coding agent) who just cloned the group's internal knowledge base for the CO3029 Data Mining Kaggle assignment (assignment-data-mining-261) - what the assignment requires, the dataset and verified findings, the official metric, rules and sharing constraints, optional tools, what already exists in this clone, and sensible next steps. Use at the start of a session or when asked what the project is or where to start ("bắt đầu từ đâu / dự án này là gì").
---

# assignment-onboarding

## Mục đích
Giúp một thành viên và agent của họ nắm được bài tập trong khoảng 10 phút, chỉ dựa trên bản clone. Skill này chỉ truyền đạt **dữ kiện và ràng buộc**,
không chọn hướng giải thay thành viên.

## Khi nào dùng
Lần đầu mở bản clone, hoặc đầu một phiên mới khi chưa có handoff. Khi được hỏi "bài này là gì" hay "bắt đầu từ đâu".

## Khi nào KHÔNG dùng
Khi đã có handoff của phiên trước (dùng `session-handoff`), hoặc khi đã có việc cụ thể (dùng skill chuyên đề).

## Ngữ cảnh cần có
Không cần gì thêm ngoài bản clone.

## Tài liệu liên quan
[AGENTS.md](../../../AGENTS.md) · [getting-started](../../../docs/getting-started.md) · [01](../../../docs/01-project-overview.md) · [02](../../../docs/02-requirements.md) ·
[05](../../../docs/05-dataset-overview.md) · [08](../../../docs/08-methodology.md) · [14](../../../docs/14-compliance-and-distribution.md) · [tools/](../../../tools/README.md)

## Quy trình
1. Đọc `AGENTS.md`, `docs/getting-started.md`, `docs/01`, `docs/02`, `docs/14`; lướt qua `docs/05` và `docs/08 §1`.
2. Kiểm tra bản clone: `data/raw/` đã có chưa, thành viên đã có code hay log gì chưa, có handoff không, `git log --oneline -10`.
3. Tóm tắt, mỗi ý 1–2 câu:
   - Output là `id,priority` cho 596 bài; Score là harmonic mean của Q (relevance có trọng số theo vị trí) và R (coverage).
   - Chấm điểm: 60% vị trí Private LB, 40% báo cáo. Bắt buộc: ít nhất một phương pháp đã học (FR-04), so sánh với một baseline, tái lập được.
   - Các dữ kiện quan trọng đã kiểm chứng (05): `Test.csv` bị lỗi quoting; test có distribution shift so với train;
     `id` có tương quan với label (Q-10).
   - Luật: một tài khoản; 3 submission/ngày/team; nộp độc lập rồi cuối kỳ gộp vào team của người cao điểm nhất, nên tổng số lượt của nhóm phải dưới trần (14); không dò nhãn.
   - Có các công cụ tùy chọn trong `tools/`.
4. Hỏi thành viên muốn bắt đầu từ đâu, và gợi ý skill phù hợp. **Không** đề xuất model hay feature cụ thể.

## Output
Bản tóm tắt khoảng 15 dòng, gồm tiến độ hiện tại, các lựa chọn bước tiếp theo, và lưu ý về luật.

## Acceptance criteria
Mọi dữ kiện đều có link nguồn. Không bịa luật hay số liệu. Không chỉ định hướng giải.

## Lỗi và escalation
Docs mâu thuẫn với bản clone: báo thành viên; code là nguồn sự thật về lời giải. Thiếu thông tin luật: chỉ ra câu hỏi mở và người cần hỏi.

## Ràng buộc
Chỉ đọc. Không gọi tool ghi của Kaggle.

## Ví dụ
- "Mình vừa clone, giờ làm gì?" → tóm tắt, rồi gợi ý cài môi trường và tải dữ liệu (`kaggle-research`, `dataset-integrity`).
- "Nắm tình hình đi" → kiểm tra bản clone, thấy đã có scorer, hỏi thành viên muốn thí nghiệm theo hướng nào (`independent-experiment`).
