# Tích hợp Kaggle MCP server

## 1. Tổng quan

| Thuộc tính | Giá trị |
|---|---|
| Server | [Galaxy-Dawn/kaggle-mcp](https://github.com/Galaxy-Dawn/kaggle-mcp), PyPI `kaggle-mcp-server` **0.2.0**, license MIT |
| Transport | stdio (chạy local) |
| Entry point | `python -m kaggle_mcp.server` (hoặc script `kaggle-mcp-server`) |
| Số tool | **51** (đã đếm qua `list_tools`) |
| Xác thực | Biến môi trường `KAGGLE_API_TOKEN` (token dạng `KGAT_...`), hoặc `~/.kaggle/kaggle.json` |
| Phương án khác | Kaggle có MCP server chính thức dạng remote (`https://www.kaggle.com/mcp`, OAuth), theo README của kaggle-mcp. Phương án này **chưa thử** |

Theo README của server, ưu điểm so với server chính thức là có thêm 10 tool về discussions và chạy local qua stdio.

## 2. Cài đặt cho Claude Code trên máy của bạn

MCP là **tùy chọn**: Kaggle CLI (mục 7) là đủ. Đây là server **bên thứ ba**. Hãy tự xem mã nguồn hoặc README của nó trước khi cài.
Các bước dưới đây đã được kiểm chứng trên một máy của nhóm ngày 2026-11-11 **[Xác minh]** (ADR-0003):

1. Tạo venv: `python -m venv %USERPROFILE%\.kaggle-mcp-venv`
2. Cài package: `pip install kaggle-mcp-server "mcp<2"`, sau đó `pip install six`.
   - Phiên bản khi kiểm chứng: kaggle-mcp-server 0.2.0, mcp 1.30.0, kaggle 2.2.5, kagglesdk 0.1.38, six 1.17.0.
3. Đăng ký với Claude Code, **local scope** (chỉ áp dụng cho user này và thư mục này; lưu trong `~/.claude.json`, ngoài repo):
   ```powershell
   claude mcp add kaggle --scope local -e KAGGLE_API_TOKEN=<YOUR_KAGGLE_API_TOKEN> -- `
     "$env:USERPROFILE\.kaggle-mcp-venv\Scripts\python.exe" -m kaggle_mcp.server
   claude mcp get kaggle    # kết quả mong đợi: Status: √ Connected
   ```
4. Đã kiểm tra bằng cách gọi các tool thật qua một MCP client:
   `competition_get`, `competition_files`, `competition_data_summary`, `competition_leaderboard`,
   `competition_submissions`, `discussions_list`, `kernels_list`, `competitions_list`. Tất cả trả về `isError=False`.

Trong Claude Code, các tool có tên dạng `mcp__kaggle__<tool>`, ví dụ `mcp__kaggle__competition_get`.
Server mới đăng ký chỉ xuất hiện trong **session mới** (cần mở lại session hoặc reload cửa sổ).

### Vì sao phải pin `mcp<2`
Với `mcp` 2.x, `import kaggle_mcp.server` báo lỗi `No module named 'mcp.server.fastmcp'` (FastMCP đã đổi tên thành MCPServer).
Package 0.2.0 không tự giới hạn phiên bản `mcp`. **[Xác minh]**

## 3. Credentials

| Cách | Khi nào dùng | Ghi chú |
|---|---|---|
| `KAGGLE_API_TOKEN` (biến môi trường) | Mặc định | Tạo tại https://www.kaggle.com/settings → API → *Create New API Token* |
| `~/.kaggle/kaggle.json` (`{"username": ..., "key": ...}`) | Dùng định dạng key cũ | Đặt ngoài repo |
| `-e` khi chạy `claude mcp add` (local scope) | Claude Code trên một máy cá nhân | Token nằm trong `~/.claude.json`, ngoài repo |

**Quy tắc bắt buộc:**
- **Không** ghi token vào file trong repo: docs, code, notebook, `.mcp.json`, `.env` đã commit, commit message.
- **Không** in token ra log hay output của notebook.
- Nếu token từng bị dán vào chat, log hoặc commit thì **tạo token mới** trên Kaggle và cập nhật lại cấu hình:
  ```powershell
  claude mcp remove kaggle -s local
  claude mcp add kaggle --scope local -e KAGGLE_API_TOKEN=<NEW_TOKEN> -- "$env:USERPROFILE\.kaggle-mcp-venv\Scripts\python.exe" -m kaggle_mcp.server
  ```

## 4. Cấu hình cho agent khác / máy khác

**Bước 1: cài server, giống ADR-0003.**
```powershell
python -m venv "$env:USERPROFILE\.kaggle-mcp-venv"
& "$env:USERPROFILE\.kaggle-mcp-venv\Scripts\python.exe" -m pip install kaggle-mcp-server "mcp<2" six
& "$env:USERPROFILE\.kaggle-mcp-venv\Scripts\python.exe" -c "import kaggle_mcp.server; print('ok')"
```

**Bước 2: cấu hình client.** Các format JSON dưới đây lấy từ README của kaggle-mcp, đã đổi `command` sang venv.
Chỉ cấu hình Claude Code local scope ở mục 2 là đã được kiểm chứng trên máy này.

*Claude Code, project scope (`.mcp.json` ở gốc repo, có thể commit)*: dùng **cú pháp mở rộng biến môi trường** `${...}`
thay vì ghi token literal. Claude Code hỗ trợ cú pháp này theo tài liệu của nó; **chưa thử trên máy này**.
```json
{
  "mcpServers": {
    "kaggle": {
      "command": "C:\\Users\\<USER>\\.kaggle-mcp-venv\\Scripts\\python.exe",
      "args": ["-m", "kaggle_mcp.server"],
      "env": { "KAGGLE_API_TOKEN": "${KAGGLE_API_TOKEN}" }
    }
  }
}
```
Đường dẫn `command` là riêng của từng máy. Vì thế nên dùng local scope cho mỗi người, hoặc không commit `.mcp.json`.

*VS Code (`.vscode/mcp.json`, key là `servers`)* và *Cursor (`.cursor/mcp.json`, key là `mcpServers`)*: cùng cấu trúc
`command` / `args` / `env` như trên, theo README của server. Cũng không ghi token literal.

## 5. Trang mô tả và metadata của competition

- MCP server **không có** tool trả về nội dung các trang Overview, Evaluation hay Rules. Hãy đọc trên website, dùng bản sao ngày
  2026-11-11 trong [reference/competition-pages/](../reference/competition-pages/README.md), hoặc chạy `tools/competition_info.py --pages <dir>`.
- MCP `competition_get` trả về deadline, số team, metric, **max daily submissions** và **max team size**.
- Các giá trị đã xác minh qua Kaggle API ngày 2026-11-11: deadline `2026-12-14 23:59:59` UTC, `merger_deadline None`,
  `max_daily_submissions 3`, `max_team_size 6`.
- Quota còn lại hôm nay của **bạn**: xem trên trang Submissions của competition, hoặc dùng lệnh
  `kaggle competitions submission-limits assignment-data-mining-261` (có trong `kaggle competitions -h`, chưa chạy thử).

## 6. Danh mục tool và khi nào dùng

Danh sách tool lấy từ `list_tools` của server. Cột "Đã thử" chỉ áp dụng cho competition này.

| Nhóm | Tool | Dùng khi | Đã thử |
|---|---|---|---|
| Competitions (chỉ đọc) | `competition_get` | Xem deadline, metric, quota | ✅ |
| | `competition_files`, `competition_data_summary` | Kiểm tra file dữ liệu có thay đổi không | ✅ |
| | `competition_leaderboard` (top 20), `competition_leaderboard_download` | Theo dõi LB. **Không dùng để dò nhãn (INT-03)** | ✅ / ❌ |
| | `competition_submissions`, `competition_get_submission` | Kiểm tra lịch sử và trạng thái submission | ✅ / ❌ |
| | `competitions_list` | Tìm competition | ✅ |
| | `competition_download` | Lấy download URL | ❌ (dùng CLI ở mục 7) |
| Competitions (**ghi**) | `competition_submit` (tham số `blob_file_tokens`, `message`) | Nộp bài. **Cần người dùng đồng ý rõ ràng**; nên dùng CLI ở mục 7 | ❌ |
| Discussions | `discussions_list`, `discussion_detail`, `discussion_comments`, `discussions_search`… | Theo dõi thông báo hoặc giải đáp của host (Q-01..Q-08) | ✅ (`discussions_list`: chưa có discussion nào) |
| Kernels | `kernels_list`, `competition_top_kernels`, `kernel_pull` | Xem notebook công khai | ✅ (`kernels_list`: chưa có kernel nào) |
| Datasets / Models / Benchmarks | `datasets_*`, `dataset_*`, `models_*`, `model_*`, `benchmark_leaderboard` | Tìm external data hoặc pretrained model (NFR-06) | ❌ |

**Các tool có tác dụng ghi** (`competition_submit`, `dataset_create*`, `dataset_update_metadata`, `dataset_delete`,
`file_upload`, `kernel_push`, `kernel_session_*`, `model_create`, `model_update`, `model_delete`, `model_instance_*create`)
**không được gọi nếu người dùng chưa đồng ý rõ ràng.** Mỗi lần nộp bài tiêu tốn quota 3/ngày của team bạn.

## 7. Fallback: Kaggle CLI

Khi không có MCP, dùng Kaggle CLI trong cùng venv (hoặc `pip install kaggle six` trong venv khác):

| Mục đích | Lệnh | Đã thử |
|---|---|---|
| Liệt kê file | `kaggle competitions files assignment-data-mining-261` | ❌ (đã thử qua MCP) |
| Tải dữ liệu | `kaggle competitions download -c assignment-data-mining-261 -p data/raw` | ✅ |
| Tải leaderboard | `kaggle competitions leaderboard assignment-data-mining-261 --download -p <dir>` | ✅ |
| Nộp bài | `kaggle competitions submit -c assignment-data-mining-261 -f <csv> -m "<msg>"` | ❌ |
| Xem submission | `kaggle competitions submissions assignment-data-mining-261` | ❌ |
| Trang mô tả | Đọc trên website hoặc trong `docs/reference/`. Lệnh `kaggle competitions pages` báo lỗi argparse trong lúc thử | — |

`kaggle` ở đây là `~/.kaggle-mcp-venv/Scripts/kaggle.exe`. Hoặc dùng giao diện web: https://www.kaggle.com/competitions/assignment-data-mining-261.

## 8. Xử lý sự cố

| Triệu chứng | Cách xử lý |
|---|---|
| `claude mcp get kaggle` báo *Failed to connect* | Chạy thử `"%USERPROFILE%\.kaggle-mcp-venv\Scripts\python.exe" -c "import kaggle_mcp.server"` |
| `No module named 'mcp.server.fastmcp'` | `pip install "mcp<2"` trong venv |
| `No module named 'six'` | `pip install six` trong venv |
| 401/403 | Token sai hoặc đã bị thu hồi; hoặc tài khoản chưa accept rules của competition |
| Tool không hiện trong Claude Code | Mở session mới. Kiểm tra `claude mcp list` |
