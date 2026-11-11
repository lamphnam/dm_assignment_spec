# tools/: công cụ tham chiếu (tùy chọn)

Các script chỉ đọc, đã kiểm thử, dùng để **đối chiếu**. Chúng không quy định cách bạn làm lời giải: bạn có thể dùng, sửa, hoặc tự viết lại.
Bốn script chỉ dùng stdlib (Python ≥ 3.9), trừ `competition_info.py` cần `kaggle` và `kagglesdk`.

| Script | Làm gì | Lệnh | Kiểm thử (2026-11-11) |
|---|---|---|---|
| `inspect_data.py` | Checksum, schema, đọc `Test.csv` theo cách đã kiểm chứng, kiểm tra ranh giới field, duplicate, shift, probe leakage | `python -I tools/inspect_data.py data/raw [--json out.json]` | 48 check, 0 FAIL; exit 2 nếu thiếu file |
| `score.py` | Cài đặt metric chính thức: `selftest` (T1–T9), `score` (chấm file dự đoán với label **local**), `bounds` (mốc tham chiếu ở 08 §1) | `python -I tools/score.py selftest` | ALL PASS |
| `validate_submission.py` | Kiểm tra file `id,priority` theo FR-01..03, in SHA-256. **Không nộp bài** | `python -I tools/validate_submission.py <csv> --test data/raw/Test.csv` | Bắt đúng 6 loại lỗi; chấp nhận file hợp lệ |
| `competition_info.py` | Chỉ đọc: deadline, `merger_deadline`, quota, kích thước team; `--pages <dir>` để tải lại các trang competition | `<python có kaggle> tools/competition_info.py` | In đủ trường; tải được 6 trang |

`score.py score` chỉ dùng với label **của validation lấy từ train**. Không bao giờ dùng với nhãn ẩn của test.

> Giảng viên cho phép 5 thành viên dùng chung (Q-14). Không chia sẻ ra ngoài nhóm ([docs/14](../docs/14-compliance-and-distribution.md)).
