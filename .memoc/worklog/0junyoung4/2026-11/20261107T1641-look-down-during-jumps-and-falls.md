---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:41:35
updated: 2026-11-07T16:41:35
status: active
tags:
  - memoc
  - memoc/worklog
---
# Look down during jumps and falls

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:41:35

## Summary

- 공중 시선 변형을 기존 점프 기준점에 맞춰 연결했다. 하강 중 자동으로 아래를 보고 상승 중에는 ↓/S로 전환한다.

## Changed Files

- `player.py`
- `tests/test_player.py`
- `assets/sprites/player/jump-right-draft-v1.json`
- `assets/sprites/player/jump-look-down-right-v1.png`
- `assets/sprites/player/jump-look-down-right-v1.prompt.txt`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`

## Verification

- 테스트 50개 통과. SDL 입력 경로에서 ↓/S 누름과 해제, 하강, 아래 베기 후 복귀, 착지를 확인했다. 사용한 5프레임의 발 위치는 원본과 1소스 픽셀 이내다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
