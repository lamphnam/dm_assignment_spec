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

> **Cập nhật 2026-11-18:** bản clone của chủ repo có thêm lời giải (`src/`, `scripts/`, `research/`, `experiments/`, `submissions/`, `outputs/`, `handoff/`,
> `requirements*.txt`) để các thành viên khác chạy thử và cải tiến; xem [15](15-solution-guide.md). Dữ liệu vẫn không nằm trong repo.
> Khung ban đầu (knowledge base không có lời giải, không nhận PR) là theo ADR-0008; phần lời giải là bổ sung của chủ repo.

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
| `leader_csv_file/` | Bản dữ liệu làm sạch của nhóm trưởng (derived từ dữ liệu competition); xin trực tiếp nhóm trưởng |
| `.venv/`, `.venv-gpu/`, checkpoint, cache HuggingFace, `outputs/logs/` | Nặng, tự sinh lại |
| `outputs/research/*.pkl` (trừ 10 file OOF của EXP-004) | ~100 file OOF trung gian, ~40 MB; xem [15 §5](15-solution-guide.md#5-chạy-lại) |

Nếu repo lời giải của bạn được đẩy lên GitHub, hãy để **private** và cấp quyền cho teaching team theo Rules §5.
