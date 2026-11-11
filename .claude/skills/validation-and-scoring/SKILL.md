---
name: validation-and-scoring
description: Interpret the official metric (relevance Q, coverage R, harmonic mean), make sure the member's scorer is correct (own implementation checked against test cases T1-T9, or the optional tools/score.py), reason about a leakage-safe validation design given the verified data facts, separate achievable reference points from oracle bounds, and interpret local vs Public leaderboard gaps and noise. Use when writing or checking a scorer, designing validation, or asking "metric này tính sao / validate thế nào".
---

# validation-and-scoring

## Mục đích
Mọi con số dùng để ra quyết định đều được tính **đúng metric**, trên validation **không leak**, và được diễn giải kèm mức nhiễu.
Protocol cụ thể do thành viên tự thiết kế.

## Khi nào dùng
Khi viết hoặc nghi ngờ scorer; khi thiết kế validation; khi Public LB lệch local; khi cần biết một cải thiện có thật hay không.

## Khi nào KHÔNG dùng
Kiểm tra format file nộp (dùng `submission-management`); tối ưu model (dùng `independent-experiment`).

## Ngữ cảnh cần có
Dữ liệu đã đọc đúng (`dataset-integrity`). Chỉ chấm trên label của **validation lấy từ train**.

## Tài liệu liên quan
[evaluation (nguyên văn)](../../../docs/reference/competition-pages/evaluation.md) · [08](../../../docs/08-methodology.md) · [11](../../../docs/11-testing-evaluation.md) ·
[ADR-0005](../../../docs/decisions/0005-metric-definition-source.md) · [references/interpretation.md](references/interpretation.md) · [tools/score.py](../../../tools/README.md)

## Quy trình
1. **Scorer:** có hai lựa chọn, đều được.
   - Dùng `tools/score.py` (import `score_split`). Chạy `python -I tools/score.py selftest` để thấy ALL PASS.
   - Tự viết theo [11 §1](../../../docs/11-testing-evaluation.md#1-đặc-tả-offline-scorer), rồi kiểm tra bằng T1–T9 (sai số ≤ 5e-7).
     Chú ý tie-break theo `str(id)`, quy ước R = 0 khi P = 0, và báo lỗi khi priority âm, NaN hay inf.
2. **Thiết kế validation:** dựa trên các dữ kiện ở [11 §2](../../../docs/11-testing-evaluation.md#2-local-validation): split chính thức 298 bài,
   có bài trùng, có distribution shift, có artifact `id`. Agent cùng thành viên tự chọn cách chia và cách chấm, và ghi lý do (Rules §7 yêu cầu giải thích được).
   Sau đó giữ cố định protocol khi so sánh các phương án.
3. **Chống leakage:** rà [07 §5](../../../docs/07-data-processing.md#5-leakage-checklist) cho thiết kế đã chọn.
4. **Mốc tham chiếu:** xem các mốc đã tính ở [08 §1](../../../docs/08-methodology.md#các-mốc-tham-chiếu-đã-tính-xác-minh). Mốc ORACLE không phải baseline.
5. **Diễn giải:** theo [references/interpretation.md](references/interpretation.md): phân loại con số, mức nhiễu, chênh lệch giữa local và Public.

## Output
Scorer đã được kiểm tra; mô tả protocol và lý do chọn; Score/Q/R kèm độ biến thiên.

## Acceptance criteria
Scorer qua T1–T9; mọi so sánh dùng cùng partition và cùng cách chấm; báo cáo đủ Q và R (NFR-03).

## Lỗi và escalation
Scorer không qua test case: dừng so sánh. Public lệch local nhiều: kiểm tra shift, leakage, nhiễu; không tune theo Public.
Có tin mới về định nghĩa Coverage (Q-01): báo thành viên.

## Ràng buộc
Không dùng nhãn ẩn hay thông tin Public/Private (INT-01..03).

## Ví dụ
- "Viết hàm metric giúp mình" → cài theo 11 §1, test T1–T9, đối chiếu với `tools/score.py` trên vài file ngẫu nhiên.
- "Model mới hơn 0.004, có thật không?" → so với std của protocol (08 §1 cho thấy khoảng 0.014–0.023 trên subset 298 bài).
