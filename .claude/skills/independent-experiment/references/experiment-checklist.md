# Checklist cho một thí nghiệm

## Trước khi chạy
- [ ] Giả thuyết một câu, gắn với một phát hiện trong phân tích dữ liệu của bạn
- [ ] Đúng **một** thay đổi so với thí nghiệm tham chiếu
- [ ] Config có seed và các tham số; lưu config trước khi chạy
- [ ] Protocol giống các lần trước (cùng partition, seed, cách chấm)

## Ý tưởng ablation điển hình (mỗi dòng một thí nghiệm)
| Thành phần | Ablation |
|---|---|
| Từng nhóm metadata (venue, year, DOI, authors) | Bỏ nhóm đó; hoặc chỉ dùng nhóm đó |
| Rule hoặc heuristic tự đặt | Tắt rule, so sánh |
| Thống kê theo tác giả | Bỏ multi-hot hoặc target encoding |
| Title text | Bỏ TF-IDF hoặc embedding; đổi n-gram |
| Policy chọn bài | Ngưỡng cố định so với tỷ lệ chọn đã tune; quét ngưỡng và vẽ đường Score/Q/R |
| Ordering và selection | Thay đổi cách xếp thứ tự hoặc cách chọn bài, giữ nguyên phần còn lại |

## Sau khi chạy
- [ ] Score/Q/R mean ± std, % bài được chọn
- [ ] Δ so với baseline tốt nhất; có vượt ~1 std không
- [ ] 5–10 lỗi điển hình
- [ ] Commit hoặc snapshot; thời gian chạy
- [ ] Kết luận và bước tiếp theo
