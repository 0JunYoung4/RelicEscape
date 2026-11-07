---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:49:08
updated: 2026-11-07T16:49:08
status: active
tags:
  - memoc
  - memoc/worklog
---
# Allow jumps from a crouched stance

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:49:08

## Summary

- 숙인 상태에서도 Space로 즉시 도약한다. ↓/S를 유지하면 낮은 자세를 사용하고, 해제하면 천장 공간이 확보된 뒤 몸을 편다.

## Changed Files

- `player.py`
- `tests/test_player.py`
- `tests/test_wall_movement.py`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`

## Verification

- 검사 51개와 SDL 게임 루프의 숙임·도약·착지를 확인했다. 낮은 천장은 충돌 상자 위쪽에서 상승을 멈춘다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
