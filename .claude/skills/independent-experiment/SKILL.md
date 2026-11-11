---
name: independent-experiment
description: Run reproducible, hypothesis-driven experiments for the member's own solution in their clone - in whatever direction the member and agent choose - with config and seed, a fixed validation protocol, a baseline of the member's choosing, Score/Q/R recording, ablations, error analysis, version tracking and an experiment-log entry. Does not prescribe models, features or baselines. Use when trying an idea, feature, model or threshold, or asked "thử ý tưởng / ghi thí nghiệm / ablation".
---

# independent-experiment

## Mục đích
Giúp thành viên khám phá **theo hướng của riêng họ** một cách có kỷ luật: mỗi thay đổi đều được kiểm chứng, ghi lại và tái lập được.
Skill này mô tả **cách làm thí nghiệm**, không nói nên thử gì.

## Khi nào dùng
Thử một ý tưởng, feature, model, ngưỡng hay policy; cần ablation hoặc phân tích lỗi cho báo cáo.

## Khi nào KHÔNG dùng
Chọn ứng viên nộp bài trong các thí nghiệm đã có (dùng `experiment-comparison`); nộp bài (dùng `submission-management`);
khi scorer chưa được kiểm tra (dùng `validation-and-scoring`).

## Ngữ cảnh cần có
Dữ liệu đọc đúng, scorer đã kiểm tra, một protocol validation cố định. Log thí nghiệm có thể dùng [template](../../../docs/templates/experiment-log.md) (tùy chọn).

## Tài liệu liên quan
[05](../../../docs/05-dataset-overview.md) (dữ kiện) · [08 §2](../../../docs/08-methodology.md#2-ràng-buộc-từ-requirements-khi-thiết-kế-lời-giải) (ràng buộc) ·
[07 §5](../../../docs/07-data-processing.md#5-leakage-checklist) · [references/experiment-checklist.md](references/experiment-checklist.md)

## Quy trình
1. **Giả thuyết:** một câu kiểm chứng được, nêu lý do (từ dữ liệu, từ metric, hay từ domain).
2. **Mốc so sánh:** rubric yêu cầu so sánh với **một baseline** trong cùng điều kiện. Thành viên tự chọn baseline và ghi lý do.
3. **Config và code:** config có seed. Mỗi lần chỉ có **một** thay đổi so với lần trước khi cần kết luận nguyên nhân.
   Viết code trong bản clone **khi thành viên đồng ý**.
4. **Chạy** trên protocol cố định, ghi Score/Q/R kèm độ biến thiên, % bài được chọn, thời gian chạy, commit.
5. **Phân tích:** ablation hoặc feature importance tùy hướng; xem các ví dụ lỗi (bài label 1 bị xếp cao, bài label cao bị loại).
6. **Kết luận:** cải thiện nhỏ hơn mức nhiễu thì coi là chưa có bằng chứng.
7. **FR-04:** ghi rõ phương pháp đã học nào thực sự tạo ra priority (Rules §2).
8. Ghi một mục vào log. Muốn nộp bài thì chuyển sang `submission-management`.

## Output
Mục log thí nghiệm, config, kết quả, và commit nếu thành viên muốn.

## Acceptance criteria
Chạy lại ra cùng số (hoặc có giải thích); không leak; có so sánh với baseline thành viên đã chọn trên cùng protocol.

## Lỗi và escalation
Không tái lập được: tìm nguồn ngẫu nhiên chưa có seed. Cải thiện bất thường lớn: nghi leakage, rà 07 §5 (gồm artifact `id`, Q-10).
Muốn dùng external data hay pretrained model: kiểm tra NFR-06 và Q-07, hỏi thành viên.

## Ràng buộc
Không sửa `data/raw/`. Không dùng Public LB làm tín hiệu train. Không lấy code hay kết quả của thành viên khác ([14](../../../docs/14-compliance-and-distribution.md)).

## Ví dụ
- "Mình muốn thử ý tưởng X" → viết giả thuyết, chọn mốc so sánh, config, chạy, ghi log, rồi ablation phần mới thêm.
- "Ghi lại thí nghiệm hôm qua" → điền log từ config và output có sẵn. Số nào thiếu thì đánh dấu `TBD`, không bịa.
