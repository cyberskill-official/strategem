# COV-018 implementation notes

## Landed

- `LocalCoreClient.convert_input` + `CalendarConvertError` (VI messages)
- API `POST /api/v1/calendar/convert`
- Query form modes: Gregorian | Lunar | Bát tự → convert via CORE before cast

## Status

`ready_to_review` — HITL required. Agent will not set `done`.
