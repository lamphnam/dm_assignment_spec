# Tài liệu: CO3029 Data Mining Assignment (Kaggle `assignment-data-mining-261`)

Đây là **knowledge base nội bộ của nhóm 5 người**: đặc tả, luật, dữ liệu và các phát hiện đã kiểm chứng, metric, công cụ tham chiếu,
hướng dẫn cài đặt, Agent Skills. Mọi thành viên nhận **cùng một bộ dữ kiện**; mỗi người tự làm lời giải trong bản clone của mình.
Tài liệu **không** đề xuất thuật toán, model hay feature nào.
Thông tin về competition được lấy từ Kaggle API và các trang chính thức ngày **2026-11-11**.

**Mới clone? Bắt đầu tại [getting-started.md](getting-started.md).**

## Quy ước mức độ tin cậy

| Nhãn | Ý nghĩa |
|---|---|
| **[Xác minh]** | Đã kiểm tra trực tiếp: đọc trang Kaggle, chạy lệnh, hoặc tính trên dữ liệu thật |
| **[Suy luận]** | Kết luận hợp lý rút ra từ dữ liệu đã xác minh, chưa được xác nhận chính thức |
| **[Đề xuất]** | Gợi ý về quy trình hoặc tổ chức repo, không bắt buộc (không dùng cho lựa chọn lời giải) |
| **[Chưa rõ]** | Thiếu thông tin. Xem [13](13-risks-open-questions.md) |

## Mục lục

### Bài toán và luật
| File | Nội dung |
|---|---|
| [getting-started.md](getting-started.md) | **10 bước, từ clone đến nộp bài** |
| [01-project-overview.md](01-project-overview.md) | Mục tiêu, deliverables, chấm điểm, timeline |
| [02-requirements.md](02-requirements.md) | Requirements có mã (FR/NFR/INT/TEAM), mâu thuẫn giữa các nguồn |
| [14-compliance-and-distribution.md](14-compliance-and-distribution.md) | Cách nhóm tham gia Kaggle (giảng viên đã trả lời), điều kiện gộp team cuối kỳ, luật chia sẻ |
| [reference/competition-pages/](reference/competition-pages/README.md) | Bản sao nguyên văn các trang Overview, Data, Evaluation, Rules |

### Dữ liệu và đánh giá
| File | Nội dung |
|---|---|
| [05-dataset-overview.md](05-dataset-overview.md) | Nguồn, checksum, định dạng, phân phối label, distribution shift, leakage qua `id`, chất lượng dữ liệu |
| [06-data-dictionary.md](06-data-dictionary.md) | Từng cột: mô tả chính thức và quan sát thực tế |
| [07-data-processing.md](07-data-processing.md) | Cách đọc `Test.csv` đã kiểm chứng (tham khảo), chuẩn hoá, duplicate, leakage checklist |
| [08-methodology.md](08-methodology.md) | Phân tích công thức metric, các mốc tham chiếu, ràng buộc từ requirements |
| [11-testing-evaluation.md](11-testing-evaluation.md) | Đặc tả scorer và test case, dữ kiện liên quan đến validation, checklist submission, data checks |
| [12-reproducibility.md](12-reproducibility.md) | Checklist reproducibility bắt buộc (Rules §5) |

### Môi trường và công cụ
| File | Nội dung |
|---|---|
| [04-repository-structure.md](04-repository-structure.md) | Cấu trúc repo; những gì không commit |
| [../tools/README.md](../tools/README.md) | Script tham chiếu tùy chọn: kiểm tra dữ liệu, scorer, validator, metadata Kaggle |
| [10-development-guide.md](10-development-guide.md) | Môi trường, credentials, tải dữ liệu, nộp bài, git, lỗi đặc thù Windows |
| [integrations/kaggle-mcp-setup.md](integrations/kaggle-mcp-setup.md) | Kaggle MCP server và Kaggle CLI |
| [templates/](templates/experiment-log.md) | Mẫu (tùy chọn): experiment log, submission log, final solution summary |

### Agent
| File | Nội dung |
|---|---|
| [agents/onboarding.md](agents/onboarding.md) | Agent bắt đầu làm việc trong một bản clone |
| [agents/skills.md](agents/skills.md) | 8 Agent Skills: cách agent tìm thấy, cách dùng |
| [agents/agent-working-rules.md](agents/agent-working-rules.md) | Nguồn nào có thẩm quyền, xử lý mâu thuẫn, cập nhật docs cục bộ |
| [agents/session-handoff-template.md](agents/session-handoff-template.md) | Mẫu bàn giao giữa các phiên agent |
| [decisions/](decisions/README.md) | ADR của repo |

### Trạng thái và rủi ro
| File | Nội dung |
|---|---|
| [09-implementation-status.md](09-implementation-status.md) | Repo có gì, đã kiểm thử gì, nhật ký thay đổi |
| [13-risks-open-questions.md](13-risks-open-questions.md) | Rủi ro chung, câu hỏi về luật và metric |

## Sửa tài liệu trong bản clone của bạn

Bạn có thể sửa, bổ sung hay xoá tài liệu **trong bản clone của mình**, ví dụ ghi phát hiện của riêng bạn. Không cần gửi ngược lại.
Nên giữ nguyên `docs/reference/` (bản sao chính thức) để còn đối chiếu.

