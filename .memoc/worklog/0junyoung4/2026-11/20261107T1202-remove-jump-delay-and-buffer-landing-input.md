---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T12:02:43
updated: 2026-11-07T12:02:43
status: active
tags:
  - memoc
  - memoc/worklog
---
# Remove jump delay and buffer landing input

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T12:02:43

## Summary

- 0.06초 준비 대기와 착지 중 Space 차단을 제거하고, 0.10초 안의 착지 전 입력을 접촉 시 처리했다.
- 착지 자세는 입력이 없을 때 표시하며, 점프 준비 그림은 재생 순서에서 건너뛴다.

## Changed Files

- `memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/04-handoff.md`
- `.memoc/06-project-rules.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/player.md`
- `README.md`
- `main.py`
- `player.py`
- `tests/test_player.py`
- `assets/sprites/player/attack-right-draft-v1.json`

## Verification

- unittest 44개, py_compile, git diff --check, memoc lint-wiki 통과.
- SDL 게임 루프에서 첫 점프 즉시 상승, 착지 직전 입력의 접촉 프레임 도약, 착지 모션 직후 입력의 즉시 상승을 확인했다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
