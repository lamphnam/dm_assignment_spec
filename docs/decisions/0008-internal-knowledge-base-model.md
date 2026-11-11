# 0008 — Repo là knowledge base nội bộ của nhóm 5 người

- **Trạng thái:** Accepted (người dùng xác nhận, 2026-11-11)
- **Ngày:** 2026-11-11
- **Liên quan:** [getting-started](../getting-started.md), [14](../14-compliance-and-distribution.md), ADR-0002

## Bối cảnh
Repo phục vụ nhóm học thuật 5 người. Mỗi thành viên clone về, làm lời giải riêng cùng AI agent của mình, và tự nộp bài.
Các phiên trước đã lần lượt: (1) thiết kế workflow nhóm, gồm task board, tracker và gộp team; (2) coi repo là starter phân phối cho người ngoài,
và vì thế cách ly phân tích dữ liệu cùng tools. Cả hai cách hiểu đều không đúng.

## Quyết định
1. Repo cung cấp cho mọi thành viên **cùng một bộ dữ kiện**: đặc tả, luật, dữ liệu, các phát hiện đã kiểm chứng, metric,
   công cụ tham chiếu tùy chọn, hướng dẫn cài đặt, skills.
2. Tài liệu và skill **trung tính**: mô tả vấn đề, dữ kiện, ràng buộc và **cách** điều tra hay kiểm chứng; **không** chỉ định thuật toán, model,
   feature, baseline hay protocol.
3. Không có hạ tầng làm việc nhóm: không task board, không tracker chung, không đồng bộ, không push ngược. Việc gộp team cuối kỳ do các thành viên tự làm trên Kaggle (điểm 4).
4. Giảng viên (cũng là host) cho phép 5 thành viên chia sẻ thoải mái, nộp độc lập, rồi cuối kỳ gộp vào team của người có điểm cao nhất
   ([14](../14-compliance-and-distribution.md)). Repo không có workflow gộp; chỉ nêu điều kiện §5c của Kaggle.

## Hệ quả
- Năm agent có thể đi theo năm hướng khác nhau trên cùng một nền dữ kiện.
- Q-11..Q-14 đã có câu trả lời (2026-11-11). Ràng buộc còn lại là trần tổng submission khi gộp team.
