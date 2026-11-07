---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:53:22
updated: 2026-11-07T16:53:22
status: active
tags:
  - memoc
  - memoc/worklog
---
# Use the normal jump pose from crouch

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:53:22

## Summary

- 숙임에서 도약한 첫 프레임부터 점프 모션을 사용한다. ↓/S는 공중 시선에 반영하고 천장 공간에 맞춰 충돌 상자 크기를 결정한다.

## Changed Files

- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`
- `player.py`
- `tests/test_player.py`

## Verification

- `python -m unittest discover -s tests` 51개 통과. SDL 게임 루프에서 ↓ 유지 중 Space 입력, 도약 프레임 렌더링, 착지 후 숙임 복귀를 확인했다.
- `memoc lint-wiki` 오류와 경고 0개.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
