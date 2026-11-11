# Agent Skills của repo nhóm

## 1. Vị trí và cách agent tìm thấy

| Agent | Thư mục được quét | Nguồn | Nhãn |
|---|---|---|---|
| Claude Code | `.claude/skills/<name>/SKILL.md` ở thư mục khởi động và các thư mục cha, lên đến gốc repo; hỗ trợ symlink | https://code.claude.com/docs/en/skills | [Xác minh] (tài liệu). **Đã thấy hoạt động:** Claude Code liệt kê được các skill của repo này ngay trong session tạo ra chúng (2026-11-11) |
| Codex | `.agents/skills` từ CWD lên đến gốc repo; `$HOME/.agents/skills`; theo symlink | https://learn.chatgpt.com/docs/build-skills | [Xác minh] (tài liệu); chưa thử trên repo này |
| Chuẩn Agent Skills | `SKILL.md` bắt buộc có `name` (1–64 ký tự `a-z0-9-`, **trùng tên thư mục**) và `description` (1–1024 ký tự); thư mục tùy chọn `scripts/`, `references/`, `assets/` | https://agentskills.io/specification | [Xác minh] (tài liệu) |

**Nguồn chuẩn duy nhất: `.claude/skills/`** (ADR-0006). Trong Claude Code, gõ `/<tên-skill>` hoặc mô tả việc cần làm.

### Dùng với Codex hoặc agent đọc `.agents/skills`
Tạo liên kết thư mục cục bộ (đã nằm trong `.gitignore`):
```powershell
# Windows: junction, không cần quyền admin (đã thử trên máy kiểm chứng)
New-Item -ItemType Directory -Force .agents | Out-Null
cmd /c mklink /J .agents\skills .claude\skills
```
```bash
# macOS/Linux
mkdir -p .agents && ln -s ../.claude/skills .agents/skills
```
Codex nói rõ là hỗ trợ *symlink*. Việc nó có đọc được qua *junction* hay không thì **chưa thử** **[Chưa rõ]**.

## 2. Danh mục

Các skill hướng dẫn **cách** điều tra, kiểm chứng và đánh giá, **không** nói phải làm lời giải gì. Script tham chiếu tùy chọn nằm ở [tools/](../../tools/README.md).

| Skill | Dùng khi |
|---|---|
| [assignment-onboarding](../../.claude/skills/assignment-onboarding/SKILL.md) | Bắt đầu phiên; sinh viên mới clone |
| [dataset-integrity](../../.claude/skills/dataset-integrity/SKILL.md) | Tải xong dữ liệu; đọc đúng `Test.csv`; hiểu chất lượng, shift, leakage |
| [validation-and-scoring](../../.claude/skills/validation-and-scoring/SKILL.md) | Viết hoặc kiểm tra scorer (T1–T9), thiết kế validation, diễn giải chênh lệch local/LB |
| [independent-experiment](../../.claude/skills/independent-experiment/SKILL.md) | Thí nghiệm theo hướng của bạn, ablation, ghi log |
| [experiment-comparison](../../.claude/skills/experiment-comparison/SKILL.md) | So sánh **các thí nghiệm của chính sinh viên** để chọn ứng viên nộp bài hoặc final |
| [submission-management](../../.claude/skills/submission-management/SKILL.md) | Chuẩn bị, validate, ghi log submission (**không tự nộp**) |
| [kaggle-research](../../.claude/skills/kaggle-research/SKILL.md) | Xác minh luật, quota, deadline; tải dữ liệu; xem discussion (chỉ đọc) |
| [session-handoff](../../.claude/skills/session-handoff/SKILL.md) | Kết thúc phiên agent hoặc tiếp tục từ phiên trước |

Luồng điển hình: `assignment-onboarding` → `kaggle-research` → `dataset-integrity` → `validation-and-scoring`
→ nhiều vòng `independent-experiment` (+ `experiment-comparison`) → `submission-management`; cuối mỗi phiên dùng `session-handoff`.

## 3. Bảo trì skill
- `SKILL.md` chỉ chứa quy trình. Kiến thức dài đặt trong `references/` hoặc ở `docs/` và được link tới.
- Skill không được chỉ định thuật toán, feature, baseline hay protocol cụ thể. Dữ kiện đặt trong `docs/`, công cụ đặt trong `tools/`.
- Sinh viên có thể sửa hoặc thêm skill **trong bản clone của mình**.
