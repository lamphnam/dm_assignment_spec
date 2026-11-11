# AGENTS.md — Quy tắc cho AI coding agents

Đây là **knowledge base nội bộ** của nhóm học thuật 5 người, dùng cho bài tập lớn **CO3029 – Data Mining**
(Kaggle competition [`assignment-data-mining-261`](https://www.kaggle.com/competitions/assignment-data-mining-261)).
Repo chứa **đặc tả, thông tin dữ liệu, luật, chi tiết metric, các phát hiện đã kiểm chứng, công cụ tham chiếu, hướng dẫn cài đặt và Agent Skills**.
Repo **chưa có lời giải**, và **không đề xuất** thuật toán, model hay feature nào.

## Cách dùng

- Mỗi thành viên clone repo, làm lời giải **riêng** cùng agent của mình, và **tự nộp bài**.
- Không có workflow chung: không push ngược, không PR, không branch chung, không tracker chung, không đồng bộ giữa các thành viên.
- Bạn (agent) phục vụ **một** thành viên: người đang dùng bản clone này. Bạn được **tự do suy luận, thiết kế và cài đặt** lời giải
  theo hướng mà bạn và thành viên đó chọn. Tài liệu chỉ cung cấp dữ kiện và ràng buộc.
- Khi thành viên yêu cầu, bạn được viết code, tạo thư mục và commit **cục bộ**. Push chỉ lên repo riêng của thành viên đó, khi được yêu cầu.

## Đọc trước

1. [docs/getting-started.md](docs/getting-started.md), hoặc chạy skill `/assignment-onboarding`.
2. [docs/README.md](docs/README.md): mục lục.
3. [docs/02-requirements.md](docs/02-requirements.md) và [docs/14-compliance-and-distribution.md](docs/14-compliance-and-distribution.md) (luật chia sẻ).

## Skills và tools

- Skills nằm ở `.claude/skills/<tên>/SKILL.md`. **Claude Code tự phát hiện**; gõ `/<tên>`. Agent đọc `.agents/skills` (ví dụ Codex)
  cần tạo liên kết cục bộ, xem [docs/agents/skills.md](docs/agents/skills.md).
  Có 8 skill: `assignment-onboarding`, `dataset-integrity`, `validation-and-scoring`, `independent-experiment`,
  `experiment-comparison`, `submission-management`, `kaggle-research`, `session-handoff`. Các skill hướng dẫn **cách** điều tra,
  kiểm chứng và đánh giá, **không** nói phải làm lời giải gì.
- `tools/` chứa script tham chiếu **tùy chọn**, đã kiểm thử ([tools/README.md](tools/README.md)).

## Quy tắc không được vi phạm

- **Không commit hay in credentials.** Token chỉ lấy từ biến môi trường ([docs/integrations/kaggle-mcp-setup.md](docs/integrations/kaggle-mcp-setup.md)).
- **Không tự nộp bài lên Kaggle**, không tạo hay đổi team, không chấp nhận lời mời. Thành viên tự làm.
- **Mỗi người một tài khoản Kaggle.** Không lách quota (3 submission/ngày/team).
- **Chia sẻ:** giảng viên cho phép 5 thành viên chia sẻ thoải mái với nhau (Q-14, Q-13). **Không** chia sẻ riêng tư code, data hay submission với người ngoài nhóm.
- **Gộp team cuối kỳ:** mỗi người nộp độc lập; cuối kỳ 4 người còn lại join team của người có điểm cao nhất. Gộp chỉ thành công nếu **tổng submission của cả nhóm** không vượt trần của Kaggle
  ([docs/14](docs/14-compliance-and-distribution.md#gộp-team-cuối-kỳ-điều-kiện-của-kaggle)). Agent không tự gửi hay chấp nhận lời mời.
- **Integrity (Rules §7):** không tìm cách lấy hidden labels, không tự gán nhãn test, không suy ngược Public/Private, không dò leaderboard để suy ra nhãn.
- **Không sửa dữ liệu gốc** và không sửa file submission đã nộp.
- **Không tự ý đổi requirements.** Requirements mâu thuẫn thì ghi lại, không âm thầm chọn một bên.
- Tài liệu viết bằng tiếng Việt, giữ thuật ngữ kỹ thuật tiếng Anh.
