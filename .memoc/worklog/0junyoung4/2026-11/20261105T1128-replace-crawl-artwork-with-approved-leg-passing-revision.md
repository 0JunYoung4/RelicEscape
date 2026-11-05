---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-05T11:28:28
updated: 2026-11-05T11:28:28
status: active
tags:
  - memoc
  - memoc/worklog
---
# Replace crawl artwork with approved leg passing revision

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-05T11:28:28

## Summary

- 승인한 다리 교차 수정본을 crawl-right-draft-v2.png와 JSON으로 저장하고 실행 버전을 교체했다.
- 기존 크기에 맞춰 배율 140/466과 지면 기준점 405/404를 적용했다. v1은 비교용으로 보존했다.

## Changed Files

- `memoc/00-project-brief.md`
- `.memoc/02-current-project-state.md`
- `.memoc/03-decisions.md`
- `.memoc/04-handoff.md`
- `.memoc/session-summary.md`
- `.memoc/wiki/knowledge/lint.md`
- `.memoc/wiki/project/player.md`
- `README.md`
- `docs/PLAYER_SPRITES.md`
- `player.py`
- `tests/test_player.py`
- `assets/sprites/player/crawl-right-draft-v1.json`

## Verification

- unittest 18개, memoc lint-wiki, git diff --check 통과.
- 승인 원본과 복사 해시 일치, 양방향 8프레임 반복·정지·숙이기·점프 검사 및 게임 렌더 표시 확인.
- 실제 조작 체감과 노트북 실행은 추가 확인 대상이다.

## Follow-up

_None._

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
