---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-06T03:14:28
updated: 2026-11-06T03:14:28
status: active
tags:
  - memoc
  - memoc/worklog
---
# Add Ctrl H hitbox overlay for player poses

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-06T03:14:28

## Summary

- Ctrl+H로 기본 숨김 캐릭터 히트박스 빨간 테두리를 켜고 끄도록 구현했다.
- 서기 40×140·숙임 100×80 월드 단위의 몸통 영역을 정의하고 자세 전환·이동·점프·카메라에 연동했다. 지형 충돌 연결은 후속 작업이다.

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

## Verification

- unittest 22개, py_compile, git diff --check, memoc lint-wiki 통과.
- 좌우 Ctrl·키다운 조건·같은 프레임의 빠른 해제, 히트박스 좌표·자세·카메라 투영·기본 숨김 검사 통과.
- SDL 표시/숨김 픽셀 검사와 서기·숙임 테두리 렌더 시각 확인. 실제 키 조작 체감과 노트북 실행은 추가 확인 대상이다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
