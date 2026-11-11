---
name: session-handoff
description: Write or resume a context handoff between AI agent sessions working on ONE student's local assignment solution - objective, relevant files, decisions, experiments, validation results, remaining work, risks and next steps - so the next session (or another agent tool on the same clone) can continue without the chat history. Use at the end of a work session, before switching agents, or when asked to continue previous work ("bàn giao / tiếp tục việc hôm qua").
---

# session-handoff

## Mục đích
Phiên agent sau, hoặc một agent khác trên cùng bản clone, làm tiếp được **mà không cần lịch sử chat**.

## Khi nào dùng
- Kết thúc phiên, hoặc phải dừng giữa chừng.
- Bắt đầu phiên mới khi đã có handoff trước đó.

## Khi nào KHÔNG dùng
- Để bàn giao giữa các thành viên. Việc đó được phép (Q-14) nhưng nằm ngoài phạm vi skill này, vốn dành cho các phiên trên cùng một bản clone.

## Ngữ cảnh cần có
Bản clone; `git status` hoặc danh sách file đã đổi; các lệnh đã chạy kèm output thật.

## Tài liệu liên quan
[session-handoff-template.md](../../../docs/agents/session-handoff-template.md) (mẫu chuẩn) · [agent-working-rules](../../../docs/agents/agent-working-rules.md)

## Quy trình
**Viết handoff:**
1. Thu thập sự thật: file đã đổi, commit, lệnh đã chạy và output **thật**, các EXP liên quan.
2. Điền mọi mục của template. Phần "Đã kiểm tra" chỉ ghi những gì **thực sự đã chạy**.
3. Lưu vào `docs/handoffs/YYYYMMDD-<chủ-đề>.md` trong bản clone, tạo thư mục nếu chưa có.
4. Nếu phiên này thay đổi hành vi đã được mô tả, cập nhật docs cục bộ.

**Tiếp tục từ handoff:**
1. Đọc handoff mới nhất.
2. Kiểm tra lại với thực tế: file có tồn tại không, test có pass không, commit có khớp không.
3. Báo sinh viên nếu có chênh lệch, rồi làm tiếp từ "Bước tiếp theo đề xuất".

## Output
Một file handoff đầy đủ. Khi tiếp tục: bản tóm tắt trạng thái và việc sẽ làm tiếp.

## Acceptance criteria
- Một agent không có ngữ cảnh đọc xong biết ngay việc tiếp theo.
- Không có token hay thông tin cá nhân. Mọi mục "đã kiểm tra" đều có lệnh và kết quả thật.

## Lỗi và escalation
- Handoff mâu thuẫn với repo thực tế: tin repo, ghi chênh lệch, báo sinh viên.
- Việc bị chặn bởi một câu hỏi về luật: ghi rõ câu hỏi và người cần hỏi.

## Ràng buộc
Không commit hay push nếu sinh viên chưa yêu cầu. Không ghi token.

## Ví dụ
- Hết phiên giữa EXP-004 → handoff ghi rõ: config đã tạo, đã chạy 3/5 fold, lệnh để chạy tiếp, kết quả tạm thời.
- "Tiếp tục việc hôm qua" → đọc `docs/handoffs/` mới nhất, chạy lại test, tóm tắt, làm tiếp.
