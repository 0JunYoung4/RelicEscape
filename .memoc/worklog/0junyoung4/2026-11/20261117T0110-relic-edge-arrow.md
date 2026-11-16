---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-17T01:10:00
updated: 2026-11-17T01:10:00
status: active
tags:
  - memoc
  - memoc/worklog
---
# 화면 밖 유물 방향 표시

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-17T01:10:00

## Summary

- 화면 밖 유물의 투영 위치를 기준으로 화면 가장자리에 청록색 화살표를 표시한다. 화면에 다시 들어오거나 회수하면 숨긴다.

## Verification

- SDL 렌더에서 상하좌우·대각선 배치와 화면 안에서 표시되지 않는 것을 확인했다. 게임 루프에서 설치·레일·석궁 유물 표시와 귀환 후 숨김을 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
