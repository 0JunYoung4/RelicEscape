---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T17:17:50
updated: 2026-11-07T17:17:50
status: active
tags:
  - memoc
  - memoc/worklog
---
# Extend the sword dust idle to two wipes

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T17:17:50

## Summary

- 기존 칼날 닦기 자세를 재배치해 두 번 쓸어내는 24프레임 초안을 만들었다. 두 동작 사이에 손을 거두는 자세를 잠깐 유지한다.

## Changed Files

- `.memoc/02-current-project-state.md`
- `.memoc/session-summary.md`
- `assets/sprites/player/idle-sword-dust-right-draft-v3.png`
- `assets/sprites/player/idle-sword-dust-right-draft-v3.json`

## Verification

- GIF 24프레임과 2.1초 모션을 확인했다. 게임 애니메이션 클래스로 전체 프레임을 좌우 방향에 그렸다.

## Follow-up

- 다리 풀기 모션과 무작위 대기 재생을 연결할 때 v3를 사용한다.

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
