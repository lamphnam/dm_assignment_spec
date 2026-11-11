# Snapshot các trang competition trên Kaggle

**Mục đích:** lưu bản sao nguyên văn các trang mô tả của competition
[`assignment-data-mining-261`](https://www.kaggle.com/competitions/assignment-data-mining-261)
để agent có thể đọc yêu cầu khi không có mạng hoặc không có Kaggle credentials.

| File | Trang trên Kaggle | Nội dung chính |
|---|---|---|
| [overview-abstract.md](overview-abstract.md) | Overview (abstract) | Mô tả ngắn bài toán |
| [overview-description.md](overview-description.md) | Overview → Description | Dữ liệu, yêu cầu môn học, công thức điểm tổng |
| [data-description.md](data-description.md) | Data | Mô tả file, cột, format submission |
| [evaluation.md](evaluation.md) | Evaluation | **Công thức metric đầy đủ** |
| [rules.md](rules.md) | Rules (assignment rules) | Yêu cầu, rubric báo cáo, quy đổi rank → điểm, integrity |

- **Thời điểm lấy:** 2026-11-11 (UTC+7).
- **Cách lấy:** gọi `kagglesdk` → `CompetitionApiService.ListCompetitionPages` (xem [../../integrations/kaggle-mcp-setup.md](../../integrations/kaggle-mcp-setup.md#5-trang-mô-tả-và-metadata-của-competition)).
- Trang `foundational-rules` (luật chung của Kaggle, khoảng 24 KB) **không** được sao vào đây. Hãy đọc trực tiếp trên Kaggle (tab Rules).

> **Quy tắc:** đây là các bản sao **chỉ đọc**. Không chỉnh sửa nội dung. Nếu trang trên Kaggle thay đổi, hãy lấy lại snapshot,
> ghi ngày mới vào file này và so sánh khác biệt trong [../../13-risks-open-questions.md](../../13-risks-open-questions.md).
> Các file là nguyên văn tiếng Anh, có công thức LaTeX dạng `\[ ... \]` nên có thể không render được trên mọi Markdown viewer.
