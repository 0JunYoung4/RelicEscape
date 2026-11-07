---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:45:19
updated: 2026-11-07T16:45:19
status: active
tags:
  - memoc
  - memoc/worklog
---
# Shorten attack recovery and buffer late attacks

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:45:19

## Summary

- 가로 베기 마무리를 35ms, 공중 아래 베기 마무리를 10ms 줄였다. 마지막 50ms의 X를 한 번 보관해 종료 시 다음 베기로 연결한다.

## Changed Files

- `player.py`
- `tests/test_player.py`
- `assets/sprites/player/attack-right-draft-v2.json`
- `assets/sprites/player/air-attack-right-draft-v3.json`
- `assets/sprites/player/air-down-attack-right-draft-v4.json`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`

## Verification

- 검사 51개 통과. 60fps SDL 게임 루프에서 예약한 지상·공중 아래 베기의 후속 입력이 한 번씩 이어지는 것을 확인했다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
