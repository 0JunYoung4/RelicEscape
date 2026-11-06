---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-06T04:04:35
updated: 2026-11-06T04:04:35
status: active
tags:
  - memoc
  - memoc/worklog
---
# Fix wall grip support and start in desktop fullscreen

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-06T04:04:35

## Summary

- 벽 슬라이드 프레임을 손 접점에 맞춰 잘라 그리도록 JSON 기준점·폭을 보정하고, 높이 140의 지지 벽이 있을 때만 슬라이드하도록 제한했다. 상단 몸통 접촉 벽점프는 유지했다.
- 기본 데스크톱 전체화면과 F11 창 전환(1280×720)을 추가했다. 내부 960×540 논리 화면·카메라 구도 유지 및 화면비 여백 지우기를 적용했다.

## Changed Files

- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/04-handoff.md`
- `.memoc/06-project-rules.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/player.md`
- `README.md`
- `main.py`
- `player.py`
- `tests/test_wall_movement.py`
- `assets/sprites/player/wall-slide-right-draft-v4.json`
- `tests/test_display.py`

## Verification

- unittest 40개, py_compile, git diff --check, memoc lint-wiki 통과.
- 실제 Windows SDL 출력이 모니터와 같은 2560×1440 전체화면 및 1280×720 창으로 전환됨을 확인했다. 벽 접점과 상단 일반 낙하 렌더도 확인했다.
- 장시간 직접 플레이와 노트북·다른 모니터 실행은 미검증이다.

## Follow-up

- 벽 이동 조작 체감 확인과 낮은 통로·유물 구현을 이어간다.

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
