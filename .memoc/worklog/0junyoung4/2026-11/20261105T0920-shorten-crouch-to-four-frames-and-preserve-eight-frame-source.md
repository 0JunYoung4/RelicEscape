---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-05T09:20:41
updated: 2026-11-05T09:20:41
status: active
tags:
  - memoc
  - memoc/worklog
---
# Shorten crouch to four frames and preserve eight frame source

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-05T09:20:41

## Summary

- 숙이기·일어서기를 4프레임·0.15초로 단축하고 원본의 1·3·5·8번째 자세를 사용한다.
- 기존 8프레임 PNG·JSON은 reference/crouch-8frame-v1/에 분리 보관했다. 빠른 정의는 해당 PNG를 재사용한다.

## Changed Files

- `memoc/00-project-brief.md`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/04-handoff.md`
- `.memoc/06-project-rules.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/player.md`
- `README.md`
- `docs/PLAYER_SPRITES.md`
- `main.py`
- `player.py`

## Verification

- unittest 14개, memoc lint-wiki, git diff --check 통과.
- 원본 두 파일의 이동 전후 SHA256 일치 확인. 30/60/144fps 프레임 순서·0.15초 완료·유지·역방향 및 기존 점프 검사 통과.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
