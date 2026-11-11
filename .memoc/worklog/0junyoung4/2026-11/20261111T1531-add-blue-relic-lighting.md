---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-11T15:31:00
updated: 2026-11-11T15:31:00
status: active
tags:
  - memoc
  - memoc/worklog
---
# 유물의 푸른 조명 구현

actor: 0junyoung4
actor_source: git config user.name
status: done
created: 2026-11-11T15:31:00

## Summary

- 어두운 유적 맵에 유물의 푸른 조명을 합성한다. 유물과 후광에 같은 부유 위치를 적용한다. 회수하면 기본 밝기로 돌아간다.

## Verification

- 자동 테스트 56개 통과. SDL 소프트웨어 렌더에서 기본 밝기 감소, 유물 주변 바닥·벽의 푸른빛, 원거리 밝기와 회수 후 밝기를 확인했다. Windows Direct3D 1280×720 출력에서도 조명의 적용·회수를 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
