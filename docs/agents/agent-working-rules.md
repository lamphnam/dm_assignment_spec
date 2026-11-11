# Quy tắc làm việc của agent trong bản clone của một sinh viên

## 1. Nguồn nào có thẩm quyền

| Câu hỏi | Nguồn |
|---|---|
| Bài tập **yêu cầu** gì? | Trang Kaggle (bản sao ở [reference/](../reference/competition-pages/README.md)), được trích thành [02-requirements.md](../02-requirements.md) |
| Lời giải của sinh viên **đang** làm gì? | **Code trong bản clone** và output khi chạy thật |
| Vì sao lại làm vậy? | ADR (repo: [decisions/](../decisions/README.md); của thành viên: ADR cục bộ) và log thí nghiệm |
| Quy tắc cho agent | [AGENTS.md](../../AGENTS.md) |

**Khi các nguồn mâu thuẫn:**
- Requirement mâu thuẫn với code: không âm thầm sửa bên nào. Báo sinh viên và đề xuất cách xử lý.
- Hai requirement mâu thuẫn nhau: xem bảng C-xx trong [02 §5](../02-requirements.md#5-mâu-thuẫn-giữa-các-nguồn-chưa-giải-quyết). Ghi câu hỏi mới vào docs cục bộ.
- Docs mô tả sai code của sinh viên: sửa docs **cục bộ** theo code.

## 2. Thay đổi requirements
Không sửa nội dung FR/NFR/INT/TEAM hay các file trong `docs/reference/`. Chỉ khi giảng viên hoặc host trả lời chính thức thì sinh viên
mới cập nhật, kèm nguồn và ngày.

## 3. Làm việc trong bản clone
- Bạn phục vụ **một** sinh viên. Mọi code, thí nghiệm, kết quả đều thuộc bản clone này.
- Viết code, tạo thư mục, commit cục bộ: được, **khi sinh viên yêu cầu**.
- Push, tạo remote, sửa repo bên ngoài: chỉ khi sinh viên yêu cầu và trỏ đúng repo riêng của họ. **Không bao giờ push lên repo nhóm.**
- Thay đổi nhỏ, mỗi commit một việc. Không reformat hàng loạt ngoài phạm vi việc đang làm.
- Trao đổi với các thành viên khác trong nhóm là được phép (Q-14). Lời giải trong bản clone này vẫn do thành viên này quyết định.

## 4. Ghi tài liệu
- Gắn nhãn [Xác minh]/[Suy luận]/[Đề xuất]/[Chưa rõ] cho mọi nhận định.
- Con số phải đi kèm cách tính lại được: lệnh, seed, commit.
- Không lặp nội dung. Hãy link tới nơi định nghĩa gốc (ví dụ metric ở [08 §1](../08-methodology.md#1-phân-tích-metric) và [11 §1](../11-testing-evaluation.md#1-đặc-tả-offline-scorer)).
- Viết tiếng Việt, giữ thuật ngữ tiếng Anh.

## 5. An toàn và integrity
- Credentials: [integrations §3](../integrations/kaggle-mcp-setup.md#3-credentials).
- Nộp Kaggle, ghi hay xoá dữ liệu trên Kaggle, đổi team: **sinh viên tự làm.**
- Tuân thủ INT-01..07 ([02 §3](../02-requirements.md#3-integrity-bắt-buộc)) và [14](../14-compliance-and-distribution.md).
