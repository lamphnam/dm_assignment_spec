# 04 — Cấu trúc repository

## 1. Repo của nhóm

```text
assignment/
├── README.md, AGENTS.md, CLAUDE.md   # giới thiệu; quy tắc cho agent (CLAUDE.md import AGENTS.md)
├── .gitignore                        # loại data/, credentials, venv
├── .claude/skills/                   # 8 Agent Skills (SKILL.md + references/)
├── tools/                            # script tham chiếu tùy chọn, đã kiểm thử
└── docs/
    ├── getting-started.md, README.md, 01..14-*.md
    ├── agents/                       # onboarding, skills, agent-working-rules, session-handoff-template
    ├── decisions/                    # ADR
    ├── integrations/                 # Kaggle MCP / CLI
    ├── templates/                    # mẫu tùy chọn: experiment log, submission log, final solution summary
    └── reference/competition-pages/  # bản sao nguyên văn trang Kaggle
```

Repo **không chứa** lời giải, dữ liệu, kết quả thí nghiệm, submission hay thông tin cá nhân. Không có branch chung và không nhận
pull request từ thành viên (ADR-0008).

## 2. Trong bản clone của bạn

Tổ chức thư mục là việc của bạn. Requirements chỉ đòi hỏi:
- Có **lệnh hoặc notebook chính xác** để tái lập submission đã chọn, và README theo Rules §5 (FR-07, [12](12-reproducibility.md)).
- **Lưu đúng** file CSV đã nộp (FR-09).
- Không commit `data/` hay credentials.

## 3. Những gì không được commit

| Loại | Lý do |
|---|---|
| Kaggle token, `kaggle.json`, `.env` | NFR-08 |
| `.mcp.json` chứa token dạng literal | NFR-08. Dùng `${KAGGLE_API_TOKEN}` ([integrations §4](integrations/kaggle-mcp-setup.md#4-cấu-hình-cho-agent-khác--máy-khác)) |
| `data/`, `*.zip` | Dữ liệu có license CC BY-NC-SA 4.0; mỗi người tự tải |
| `.agents/skills` (liên kết cục bộ) | Liên kết riêng của từng máy (ADR-0006) |

Nếu repo lời giải của bạn được đẩy lên GitHub, hãy để **private** và cấp quyền cho teaching team theo Rules §5.
