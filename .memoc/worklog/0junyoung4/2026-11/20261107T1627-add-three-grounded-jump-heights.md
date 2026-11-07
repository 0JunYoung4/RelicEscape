---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:27:49
updated: 2026-11-07T16:27:49
status: active
tags:
  - memoc
  - memoc/worklog
---
# Add three grounded jump heights

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:27:49

## Summary

- 바닥·발판 점프를 Space 유지 시간에 따라 90·145·202.5 높이로 나눴다. 착지 입력 버퍼로 예약한 짧은 탭도 짧게 재점프한다.

## Changed Files

- `main.py`
- `player.py`
- `tests/test_player.py`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`

## Verification

- 단위 검사 49개 통과. 30·60·144fps에서 세 높이와 착지 버퍼, SDL 게임 루프의 키다운·홀드·릴리스를 확인했다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
