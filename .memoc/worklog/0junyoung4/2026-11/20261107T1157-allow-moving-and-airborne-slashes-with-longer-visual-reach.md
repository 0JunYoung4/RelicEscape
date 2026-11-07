---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T11:57:06
updated: 2026-11-07T11:57:06
status: active
tags:
  - memoc
  - memoc/worklog
---
# Allow moving and airborne slashes with longer visual reach

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T11:57:06

## Summary

- 베기 시계와 방향을 이동 상태에서 분리해 걷기·달리기·점프 중에도 X를 받도록 했다.
- 몸을 앞으로 기울이고 칼을 늘린 v2 타격 프레임을 적용했다. 발 중심에서 칼끝까지 보이는 거리는 311px에서 403px로 늘었다.

## Changed Files

- `memoc/02-current-project-state.md`
- `.memoc/06-project-rules.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/player.md`
- `README.md`
- `main.py`
- `player.py`
- `tests/test_player.py`
- `assets/sprites/player/attack-right-draft-v1.json`
- `assets/sprites/player/attack-right-draft-v1.png`
- `assets/sprites/player/attack-right-draft-v2.json`

## Verification

- unittest 42개, py_compile, git diff --check, memoc lint-wiki 통과.
- SDL 게임 루프에서 이동과 점프 중 X 및 타격 프레임을 확인했다. 실시간 수동 조작감은 추가 확인 대상이다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
