# Test.csv — ghi chú kỹ thuật (kiểm chứng ngày 2026-11-11)

Bổ sung cho [07 §2](../../../../docs/07-data-processing.md#2-parse-testcsv). Đây là kết quả kiểm tra **ranh giới field**,
không chỉ kiểm tra số dòng.

| Kiểm tra | Kết quả |
|---|---|
| Mỗi dòng có đúng một anchor `(venue ∈ {kr,cav,lics,iclp,lpnmr}, năm 4 chữ số)` | 596/596 |
| Field cuối (`doi`) bắt đầu bằng `10.` hoặc `http` | 596/596 |
| Năm nằm trong 2016–2025; venue ∈ {cav 221, lics 187, kr 151, lpnmr 37} | Đúng |
| Author token chứa chữ số hoặc trùng tên venue | 0 |
| Author token là hậu tố tên (`Jr.`, `II`…), dấu hiệu tên bị cắt đôi | 0 |
| Author token chỉ có một từ | 2 (`Govind`, `Krishna` trong id 2538). Đây là cách viết tên ngắn của nguồn (train có `R. Govind`), không phải lỗi tách |
| Authors có segment rỗng (ví dụ `,Xinwei Chai`) | test 7, train 22. Đây là đặc điểm của dữ liệu nguồn |
| Title chứa dấu phẩy (đã ghép lại) | 34 |
| Chuỗi `", "` trong file | 0: mọi khoảng trắng sau dấu phẩy đã bị bỏ. Title ghép lại có dạng `A,B` |
| Line ending | CRLF (596), không có newline cuối file |
| Thứ tự id trong `Submission.csv` | Trùng thứ tự `Test.csv` |

**Giới hạn không kiểm chứng được:**
- Khoảng trắng gốc sau dấu phẩy trong title. Khôi phục bằng `", "` là **[Suy luận]** dựa trên format của train.
- Một tác giả có tên chứa dấu phẩy sẽ bị tách thành hai token. Không phát hiện trường hợp nào, nhưng không thể loại trừ hoàn toàn.

**Probe leakage (train):** trong mỗi nhóm (venue, year), id tăng thì label có xu hướng giảm. Spearman trung bình có trọng số là −0.091.
Permutation test (300 lần) cho z ≈ −4.6, p < 1/300. Một phần do các bài front matter nằm cuối mỗi nhóm; sau khi loại chúng,
hiệu ứng yếu hơn nhưng vẫn còn. Vì test id xen kẽ trong cùng các khoảng, `id` hay vị trí có thể mang tín hiệu về label.
Đó là **artifact của cách dựng dataset**, xem Q-10.
