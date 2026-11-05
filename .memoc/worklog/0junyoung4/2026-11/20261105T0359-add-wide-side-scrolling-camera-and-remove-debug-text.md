---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-05T03:59:26
updated: 2026-11-05T03:59:26
status: active
tags:
  - memoc
  - memoc/worklog
---
# Add wide side scrolling camera and remove debug text

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-05T03:59:26

## Summary

- 0.5배 카메라로 기존 대비 가로·세로 2배 넓은 범위를 보여주며 캐릭터를 약 70px 높이로 표시한다.
- 월드 좌표와 화면 좌표를 분리해 6400 너비 시험 맵에서 횡스크롤 추적과 맵 경계를 적용했다.
- 왼쪽 위 조작·상태 텍스트 제거. README·스프라이트 문서·memoc 규칙과 상태 갱신.

## Changed Files

- `memoc/00-project-brief.md`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/04-handoff.md`
- `.memoc/06-project-rules.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/README.md`
- `README.md`
- `docs/PLAYER_SPRITES.md`
- `.memoc/wiki/project/player.md`
- `assets/sprites/player/run-right-v1.json`

## Verification

- py_compile, git diff --check, memoc lint-wiki 통과.
- 카메라 중앙 추적·양 끝 제한·1920 너비 뷰·70px 캐릭터·텍스트 부재 및 이동 검사 통과.
- SDL에서 전체 프레임 좌우 50회 렌더링 통과. 시작·중간 렌더 이미지를 시각 확인했다. 새 카메라의 실제 장시간 키 조작 감각과 노트북 실행은 미확인.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
