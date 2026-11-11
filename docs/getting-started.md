# Getting Started

Bạn vừa clone knowledge base của nhóm. Từ đây, **bản clone là không gian làm việc riêng của bạn**: code, thí nghiệm, kết quả và
submission đều là của bạn. Không cần push ngược lại hay đồng bộ với ai. Các bước dưới đây là **quy trình chung**.
Cách giải bài thì do bạn và agent của bạn tự quyết định.

| # | Bước | Tài liệu / skill |
|---|---|---|
| 1 | Clone repo. Muốn lưu lên GitHub thì dùng repo **private** riêng ([10 §6](10-development-guide.md#6-git-trong-bản-clone-của-bạn)) | — |
| 2 | Đọc [AGENTS.md](../AGENTS.md), [02-requirements](02-requirements.md), [14 cách tham gia](14-compliance-and-distribution.md) | — |
| 3 | Gõ `/assignment-onboarding` | `assignment-onboarding` |
| 4 | Cài môi trường: venv, thư viện tùy bạn chọn, Kaggle CLI hoặc MCP | [10](10-development-guide.md), [integrations](integrations/kaggle-mcp-setup.md) |
| 5 | Tham gia competition bằng **tài khoản của bạn**, tải dữ liệu vào `data/raw/`, kiểm tra | `kaggle-research`, `dataset-integrity`; [05](05-dataset-overview.md)–[07](07-data-processing.md) |
| 6 | Hiểu metric; có một scorer đáng tin (tự viết hoặc dùng `tools/score.py`) | `validation-and-scoring`; [08](08-methodology.md), [11](11-testing-evaluation.md) |
| 7 | Khám phá và thí nghiệm theo hướng **của bạn**: giả thuyết, validation, ghi log, so sánh với một baseline do bạn chọn (rubric yêu cầu) | `independent-experiment`, `experiment-comparison` |
| 8 | Kiểm tra file nộp và ghi log | `submission-management`; [templates/](templates/submission-log.md) |
| 9 | **Bạn tự nộp** (3 lượt/ngày/team) và ghi Public score | [10 §4](10-development-guide.md#4-nộp-bài-lên-kaggle) |
| 10 | Chọn final submission; viết README tái lập và báo cáo | [12](12-reproducibility.md), [02 §4](02-requirements.md#4-rubric-báo-cáo-r) |

Cuối mỗi phiên làm việc với agent, dùng `session-handoff`.

**Lưu ý về số lượt nộp:** cuối kỳ cả nhóm gộp vào team của người có điểm cao nhất. Gộp chỉ được nếu **tổng submission của 5 người** dưới trần
(khoảng 147 lượt nếu gộp ngày 30/11; xem [14](14-compliance-and-distribution.md#gộp-team-cuối-kỳ-điều-kiện-của-kaggle)). Đừng dùng hết 3 lượt/ngày.
