---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-11T16:40:00
updated: 2026-11-11T16:40:00
status: active
tags:
  - memoc
  - memoc/worklog
---
# 푸른 도트 귀환 연출 적용

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done

## Summary

- 성공한 유물 귀환 시 출발·도착 자세를 각각 캡처한다. 출발지에서 2×2 도트가 흩어지고 유물 위치에서 다시 모인다. 연출은 0.59초이며 이동·중력은 계속 적용한다.

## Verification

- 전체 자동 테스트 56개 통과. SDL 소프트웨어 렌더 및 Windows Direct3D에서 연출이 재생되고 끝난 뒤 일반 자세가 표시되는 것을 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
