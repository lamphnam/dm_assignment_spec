# 10 — Hướng dẫn phát triển

## 1. Chuẩn bị môi trường

Repo **không có dependency manifest**. Bạn tạo nó trong bản clone của mình, với thư viện tùy bạn chọn. Các bước dưới đây là **[Đề xuất]**,
trừ những chỗ ghi khác.

```powershell
# Từ thư mục gốc của repo (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
# Thêm package khi task cần, rồi pin phiên bản:
python -m pip install pandas numpy scikit-learn
python -m pip freeze > requirements.txt
```

- Máy dùng để kiểm chứng các lệnh có Python **3.14.5** **[Xác minh]**. Chưa kiểm tra xem các thư viện ML có wheel cho 3.14 chưa
  **[Chưa rõ]**. Nếu cài lỗi, dùng Python 3.11 hoặc 3.12 và ghi lại phiên bản đã chọn vào README (FR-07b).
- Nếu cài Kaggle MCP theo [integrations](integrations/kaggle-mcp-setup.md), venv của nó (`%USERPROFILE%\.kaggle-mcp-venv`)
  **chỉ dùng cho MCP và Kaggle CLI**. Không cài package của lời giải vào đó.

## 2. Credentials

Đặt token qua biến môi trường, **không bao giờ ghi vào file trong repo**:

```powershell
$env:KAGGLE_API_TOKEN = "<YOUR_KAGGLE_API_TOKEN>"   # chỉ có hiệu lực trong phiên hiện tại
```
```bash
export KAGGLE_API_TOKEN="<YOUR_KAGGLE_API_TOKEN>"   # Git Bash
```

Chi tiết và các cách khác: [integrations/kaggle-mcp-setup.md](integrations/kaggle-mcp-setup.md#3-credentials).

## 3. Tải dữ liệu

Trước tiên, **tham gia competition và accept rules bằng tài khoản Kaggle của bạn** trên website.
**[Xác minh]**: lệnh dưới đây đã chạy thành công ngày 2026-11-11 với Kaggle CLI trong venv của MCP. Với `pip install kaggle six` thì
bất kỳ venv nào cũng dùng được.

```bash
# Git Bash; KAGGLE_API_TOKEN đã được đặt
mkdir -p data/raw
~/.kaggle-mcp-venv/Scripts/kaggle.exe competitions download -c assignment-data-mining-261 -p data/raw
cd data/raw && unzip -o assignment-data-mining-261.zip && sha256sum *.csv
```
```powershell
# PowerShell
& "$env:USERPROFILE\.kaggle-mcp-venv\Scripts\kaggle.exe" competitions download -c assignment-data-mining-261 -p data/raw
Expand-Archive data/raw/assignment-data-mining-261.zip -DestinationPath data/raw -Force
Get-FileHash data/raw/*.csv -Algorithm SHA256
```

So khớp checksum với [05 §1](05-dataset-overview.md#1-nguồn). Có thể tải thủ công từ tab *Data* trên Kaggle (cần đăng nhập
và đã accept rules). Lệnh `Expand-Archive` chưa được chạy thử trên máy này.

## 4. Nộp bài lên Kaggle

**Bạn tự nộp**, qua web hoặc bằng lệnh dưới đây. Agent không chạy lệnh nộp.
Lệnh dưới đây là cú pháp chuẩn của Kaggle CLI và **chưa được chạy thử** khi viết tài liệu này:

```bash
~/.kaggle-mcp-venv/Scripts/kaggle.exe competitions submit -c assignment-data-mining-261 \
    -f submissions/<file>.csv -m "<commit-hash> <mô tả ngắn>"
~/.kaggle-mcp-venv/Scripts/kaggle.exe competitions submissions assignment-data-mining-261
```

Trước khi nộp:
1. Chạy validator ([11 §3](11-testing-evaluation.md#3-validator-cho-submission)).
2. Commit code và ghi commit hash vào message.
3. Ghi manifest ([12 §3](12-reproducibility.md#3-manifest-cho-mỗi-submission)).
4. Kiểm tra quota 3 lần/ngày, ví dụ bằng `kaggle competitions submission-limits assignment-data-mining-261` (lệnh có trong
   `kaggle competitions -h`, chưa chạy thử).

**Không nộp chỉ để dò leaderboard (INT-03).** Quy trình đầy đủ và log: skill `submission-management`,
[templates/submission-log.md](templates/submission-log.md).

## 5. Quy ước code **[Đề xuất]**

- Logic nằm trong `src/`, entry point nằm trong `scripts/`. Notebook chỉ dùng cho EDA và hình vẽ phục vụ báo cáo.
- Mọi hàm ngẫu nhiên đều nhận `seed`, mặc định lấy từ config.
- Đọc dữ liệu **chỉ** qua loader của bạn ([07](07-data-processing.md)). Không đọc `Test.csv` bằng `pd.read_csv` mặc định.
- Tính điểm **chỉ** qua scorer của bạn, sau khi nó đã qua T1–T9 ([11 §1](11-testing-evaluation.md#1-đặc-tả-offline-scorer)).
- Đường dẫn luôn tương đối với gốc repo. Không hardcode `C:\Users\...`.

## 6. Git trong bản clone của bạn

- Bản clone là của bạn: tự do tạo branch, commit cục bộ, sửa docs.
- **Không push lên repo nhóm.** Nếu muốn lưu trên GitHub (Rules §5 yêu cầu có repo lời giải), hãy tạo repo **private** của bạn:
  ```bash
  git remote rename origin group            # giữ repo nhóm để thỉnh thoảng pull bản cập nhật tài liệu
  git remote add origin <url-repo-private-của-bạn>
  git push -u origin main
  ```
  Cấp quyền cho teaching team theo Rules §5. Chia sẻ trong nhóm 5 người là được phép; không chia sẻ ra ngoài nhóm.
- `.gitignore` của repo đã loại `data/`, credentials và venv. Kiểm tra bằng `git status --ignored` trước khi commit.

## 7. Lỗi đặc thù môi trường Windows **[Xác minh]**

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `UnicodeEncodeError: 'charmap' codec` khi print | Console dùng cp1252 | Dùng `python -X utf8 ...`, đặt `PYTHONIOENCODING=utf-8`, hoặc gọi `sys.stdout.reconfigure(encoding="utf-8")`. Ghi file thì luôn truyền `encoding="utf-8"` |
| `PYTHONIOENCODING` không có tác dụng | Chạy `python -I` (isolated mode bỏ qua các biến `PYTHON*`) | Dùng `reconfigure` trong code |
| Đối số JSON truyền vào exe từ PowerShell 5.1 bị mất dấu nháy | Cách PowerShell 5.1 xử lý quoting cho native command | Ghi JSON ra file rồi truyền đường dẫn, hoặc dùng Git Bash |
| `ModuleNotFoundError: No module named 'six'` khi chạy `kaggle` | kaggle 2.2.5 thiếu dependency này | `pip install six` trong venv |
| `kaggle competitions pages ...` báo lỗi argparse | Thứ tự đối số của subcommand `pages` rất khó dùng | Đọc trên website, hoặc dùng bản sao trong [reference/](reference/competition-pages/README.md) |
| `Test.csv` cho ra số cột lung tung | Lỗi quoting của dữ liệu, không phải lỗi môi trường | [07 §2](07-data-processing.md#2-parse-testcsv) |
