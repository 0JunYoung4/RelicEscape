---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-07T17:12:18
updated: 2026-11-07T17:12:18
status: active
tags:
  - memoc
  - memoc/worklog
---
# Draft a 16-frame sword dust idle animation

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-07T17:12:18

## Summary

- 승인된 기본 캐릭터를 기준으로 칼날을 확인하고 손목을 털어 먼지를 떨어뜨리는 16프레임 투명 스프라이트 시트를 만들었다.

## Changed Files

- `.memoc/02-current-project-state.md`
- `.memoc/session-summary.md`
- `assets/sprites/player/idle-sword-dust-right-draft-v1.png`
- `assets/sprites/player/idle-sword-dust-right-draft-v1.prompt.txt`

## Verification

- 시트 4×4 배치와 알파를 확인했다. 16개 프레임의 발 위치를 맞춘 1.42초 GIF를 생성해 먼지 털기 자세를 확인했다.

## Follow-up

- 다리 풀기 모션을 제작한 뒤 대기 시간과 무작위 재생을 연동한다.

## Related

- [Activity](../../../activity.md)
- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
