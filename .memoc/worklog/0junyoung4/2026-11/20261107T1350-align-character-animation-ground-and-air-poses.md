---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T13:50:31
updated: 2026-11-07T13:50:31
status: active
tags:
  - memoc
  - memoc/worklog
---
# Align character animation ground and air poses

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T13:50:31

## Summary

- 달리기·지상 베기의 디딤 위치, 점프·공중 베기의 골반 높이, 숙임·기어가기 전환의 크기와 기준점을 맞췄다.

## Changed Files

- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`
- `assets/sprites/player/air-attack-right-draft-v3.json`
- `assets/sprites/player/attack-right-draft-v2.json`
- `assets/sprites/player/crawl-right-draft-v2.json`
- `assets/sprites/player/jump-right-draft-v1.json`
- `assets/sprites/player/run-right-v1.json`
- `player.py`

## Verification

- 단위 검사 45개와 58프레임 양방향 SDL 렌더 116회를 통과했다. 디딤·벽 접점과 공중 및 숙임 전환 높이를 비교했다.
- 기존 PNG 36개의 SHA-256 일치를 확인했다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
