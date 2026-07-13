# Product voice — Tam Thức Strategem

VI is primary. EN/ZH follow the same stance, not a separate brand.

## Allowed first-screen words (prefer)

- bức hình, câu hỏi, gợi ý, chỗ dựa, khung để nghĩ
- la bàn thời điểm / cuộc trò chuyện / nhịp lớn (metaphors)
- chậm lại, kiểm tra, mở một bước, giữ biên độ
- trên máy này, miễn phí, đi sâu hơn

## Avoid on first paint (home, cast, results story)

- la số, ban đồ, cách cục, 局, 陽遁/陰遁 (ok inside collapsed “chi tiết bàn”)
- xem mệnh, đổi đời, chắc chắn, sẽ thắng, sụp đổ, định mệnh
- raw engine ids as primary labels (`PhucNgam`, UUID under title)

## Stance

- Soft, adult, non-destiny. Never guarantee outcomes.
- One disclaimer line in chrome; medium on results; full on report/PDF.
- Classical names are tags, not the headline.

## Enforcement

- Unit test: `apps/web/tests/copy-voice.test.mjs` denylist on home/cast/results keys.
- Agents: do not introduce prophecy tone without user waiver.
