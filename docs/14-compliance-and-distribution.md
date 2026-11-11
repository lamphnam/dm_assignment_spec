# 14 — Cách nhóm tham gia Kaggle và luật chia sẻ

## Câu trả lời của giảng viên (2026-11-11, nhóm truyền đạt lại)

| ID | Câu hỏi | Trả lời |
|---|---|---|
| Q-14 | Thành viên có được dùng chung repo này (gồm `tools/` và phân tích dữ liệu) không? | **Được.** Năm người là một nhóm trên lớp, được thoải mái chia sẻ |
| Q-11 | Có được nộp bài độc lập không? | **Được.** Mỗi người nộp bằng tài khoản riêng. **Cuối kỳ, 4 người còn lại join vào team của người có điểm cao nhất** (giảng viên gợi ý) |
| Q-12 | Báo cáo và điểm tính theo người hay theo nhóm? | Không phát sinh: cuối cùng cả nhóm gộp thành **một team** |
| Q-13 | Có được trao đổi kết quả giữa các thành viên không? | **Được.** Ngoài 5 người thì không có team nào khác cần tính tới |

Repo là knowledge base dùng chung của 5 người. Trao đổi code, kết quả hay ý tưởng **trong nhóm** đều được phép.
**Không** chia sẻ riêng tư với người ngoài nhóm (Kaggle foundational rules §5d, §6a; Rules §7).

> Kaggle §6a cho phép ngoại lệ khi được *"specifically permitted"*, và giảng viên chính là host của competition. Nên giữ lại một bằng chứng
> bằng văn bản cho sự cho phép này (tin nhắn, email hoặc thông báo trên LMS) để dùng khi cần.

## Gộp team cuối kỳ: điều kiện của Kaggle

Gộp team chỉ thành công khi thỏa **Kaggle foundational rules §5c** **[Xác minh: nội dung luật]**:

| Điều kiện | Áp dụng cho nhóm |
|---|---|
| (i) Team sau khi gộp ≤ Max Team Size | 5 người ≤ 6 (Kaggle) và ≤ 5 (môn học). ✅ |
| (ii) **Tổng submission của các team gộp ≤ số submission một team được phép tính đến ngày yêu cầu gộp** | Cần theo dõi. Xem bên dưới |
| (iii) Gộp xong trước merger deadline hoặc deadline competition | API báo không có merger deadline riêng, nên mốc là **2026-12-14 23:59:59 UTC** (06:59 sáng 15/12 giờ VN). Mọi người phải **chấp nhận lời mời** trước mốc này |
| (iv) Team sau khi gộp thỏa các luật khác | Mỗi người một tài khoản, chỉ thuộc một team |

**Trần submission (ii)** **[Suy luận từ câu chữ của luật]**: khoảng `3 × số ngày từ 2026-10-13 đến ngày yêu cầu gộp`, tính cả hai đầu.

| Ngày yêu cầu gộp | Trần ước tính (tổng của 5 người) |
|---|---:|
| 2026-11-30 | 147 |
| 2026-12-07 | 168 |
| 2026-12-12 | 183 |

- Nếu cả 5 người cùng nộp 3 lượt/ngày (15 lượt/ngày cho cả nhóm), tổng sẽ vượt trần sau khoảng một tuần. Lúc đó **không gộp được nữa**.
  Cả nhóm cần theo dõi **tổng số lượt đã dùng** và giữ nó dưới trần của ngày dự kiến gộp, kèm một khoảng dự phòng.
- Trước khi gửi yêu cầu gộp, kiểm tra trên trang Team của Kaggle. Kaggle sẽ từ chối nếu vượt điều kiện. Agent **không** tự gửi hay chấp nhận lời mời.
- Sau khi gộp, team có chung quota 3/ngày. Nên gộp sớm hơn deadline vài ngày để còn thời gian xử lý sự cố và chọn final submission (Q-05).

## Luật liên quan **[Xác minh, 2026-11-11]**

| Luật | Nguồn |
|---|---|
| Mỗi người một tài khoản, chỉ thuộc một team; quota 3 submission/ngày/team | Kaggle foundational rules §5a–b; metadata |
| Không chia sẻ riêng tư code hay data ra ngoài team; chia sẻ công khai thì phải đăng trên forum hoặc notebook của competition | §5d, §6a–b |
| Không trao đổi implementation hay submission với team khác; "general discussion" thì được | Rules §7 |
