---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T16:36:20
updated: 2026-11-07T16:36:20
status: active
tags:
  - memoc
  - memoc/worklog
---
# Tighten attack timing and add directional slash trail

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T16:36:20

## Summary

- 가로 베기 전환 프레임에 이동 자세를 연결하고, 지상·공중 가로·공중 아래 타격 자세를 각각 100·105·90ms로 앞당겼다.
- pixelfx 외부 체크아웃은 권한과 DNS 문제로 실행하지 못해 SDL에서 75ms 검기를 별도로 그린다.

## Changed Files

- `player.py`
- `slash_effect.py`
- `assets/sprites/player/attack-right-draft-v2.json`
- `assets/sprites/player/air-attack-right-draft-v3.json`
- `assets/sprites/player/air-down-attack-right-draft-v4.json`
- `tests/test_player.py`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/project/player.md`

## Verification

- 단위 검사 49개와 60fps SDL 게임 루프에서 세 공격의 타격 프레임·검기 동기화 및 방향 반전을 확인했다. 확대 렌더에서 칼끝과 검기의 위치를 비교했다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
