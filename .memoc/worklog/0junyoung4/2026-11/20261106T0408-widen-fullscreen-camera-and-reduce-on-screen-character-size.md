---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-06T04:08:39
updated: 2026-11-06T04:08:39
status: active
tags:
  - memoc
  - memoc/worklog
---
# Widen fullscreen camera and reduce on screen character size

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-06T04:08:39

## Summary

- 전체화면을 유지하고 CAMERA_ZOOM을 0.5→1/3로 조정했다. 시야는 2880×1620으로 가로·세로 1.5배 넓고 캐릭터·지형 표시 크기는 2/3다.
- 카메라 변경에 맞춰 기존 화면·히트박스 투영 검사의 기대값과 설명을 갱신했다. 물리·충돌·이동 속도는 유지했다.

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
- `tests/test_player.py`
- `tests/test_display.py`

## Verification

- unittest 40개, py_compile, git diff --check, memoc lint-wiki 통과.
- 실제 2560×1440 전체화면 렌더를 확인했다. 월드 시야 2880×1620, 기본 캐릭터 환산 높이 약 124px이다.
- 장시간 직접 조작 체감 및 다른 모니터 실행은 미검증이다.

## Follow-up

- 사용자 체감에 따라 CAMERA_ZOOM을 추가 조정한다.

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
