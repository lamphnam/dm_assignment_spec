---
name: kaggle-research
description: Read-only investigation of the assignment-data-mining-261 Kaggle competition for the student - rules pages, deadline, team size, daily submission limit, leaderboard, discussions and host announcements, and downloading the data with the student's own account - via a configured Kaggle MCP server or the official Kaggle CLI, with credential hygiene. Use to verify a rule, check whether competition pages changed, look for announcements, or download data ("kiểm tra luật Kaggle / tải dữ liệu / xem LB").
---

# kaggle-research

## Mục đích
Lấy thông tin **từ nguồn chính thức** thay vì phỏng đoán, và biết khi nào snapshot trong `docs/reference/` đã cũ.

## Khi nào dùng
- Cần xác minh luật (quota, team, deadline), hoặc kiểm tra xem trang competition có thay đổi không.
- Tải dữ liệu; tìm thông báo của host liên quan đến các câu hỏi mở (Q-01..Q-10).

## Khi nào KHÔNG dùng
- Để nộp bài, tạo, sửa hay xoá dataset, kernel, model, hoặc đổi team. Các tool ghi đó cần sinh viên đồng ý rõ ràng; skill này không làm.
- Để suy ra quyền từ một competition khác.

## Ngữ cảnh cần có
Kaggle credentials của sinh viên trong biến môi trường `KAGGLE_API_TOKEN` (hoặc `~/.kaggle/kaggle.json`). **Không bao giờ in hay ghi token.**
MCP `kaggle` (tùy chọn) hoặc Kaggle CLI ([integrations](../../../docs/integrations/kaggle-mcp-setup.md)).

## Tài liệu liên quan
[integrations](../../../docs/integrations/kaggle-mcp-setup.md) · [reference/competition-pages/](../../../docs/reference/competition-pages/README.md) ·
[02 §3b](../../../docs/02-requirements.md#3b-team-và-submission-luật-kaggle) · [14](../../../docs/14-compliance-and-distribution.md)

## Quy trình
1. **Chọn kênh:** nếu có MCP `kaggle`, chỉ dùng tool đọc (`competition_get`, `competition_files`, `competition_leaderboard`,
   `discussions_list`, `discussions_search`…). Nếu không, dùng Kaggle CLI (integrations §7) hoặc website.
2. **Luật và metadata:** `competition_get` trả về deadline, max daily submissions, max team size. Có thể dùng thêm `tools/competition_info.py`
   (chỉ đọc; có `merger_deadline` và quota còn lại của tài khoản). Đối chiếu với 02 §3b.
   Nếu khác, coi Kaggle là đúng và báo sinh viên.
3. **Trang mô tả:** đọc trên website và so với `docs/reference/`. Nếu khác, báo sinh viên và cập nhật bản sao **cục bộ** (ghi ngày).
4. **Tải dữ liệu:** theo [10 §3](../../../docs/10-development-guide.md#3-tải-dữ-liệu), rồi chuyển sang `dataset-integrity`.
5. **Discussion và LB:** tìm thông báo của host, trích nguyên văn kèm ngày. Không dò LB để suy ra nhãn.
6. **Ghi kết quả** với nhãn [Xác minh] (kèm nguồn và ngày) hoặc [Chưa rõ].

## Output
Dữ kiện có nguồn, ngày và nhãn; danh sách trang đã thay đổi (nếu có).

## Acceptance criteria
Không có dữ kiện nào thiếu nguồn; không bịa tên tool MCP hay tham số; không có token trong output hay file.

## Lỗi và escalation
- Lỗi 401/403: token sai hoặc hết hạn, hoặc chưa accept rules. Báo sinh viên; không yêu cầu dán token vào chat.
- MCP lỗi `mcp.server.fastmcp`: xem mục xử lý sự cố trong integrations.

## Ràng buộc
Chỉ đọc. Không cài phần mềm khi sinh viên chưa đồng ý; không sửa cấu hình agent toàn cục.

## Ví dụ
- "Quota là 3 tổng hay 3 mỗi ngày?" → `competition_get` hoặc trang Overview: 3 mỗi ngày, trích Kaggle rules §5a.
- "Host có trả lời về coverage chưa?" → `discussions_search` hoặc `discussions_list`, trích nguyên văn nếu có, cập nhật Q-01 cục bộ.
