---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-17T01:42:20
updated: 2026-11-17T01:42:20
status: active
tags:
  - memoc
  - memoc/worklog
---
# 유물 출발점 문양 이미지 적용

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-17T01:42:20

## Summary

- `relic-departure-sigil-v3.png`를 선형 필터링으로 표시해 부드러운 경계를 살린다.
- 같은 PNG를 24×24로 샘플링해 흡수 픽셀의 위치, 색, 불투명도를 가져온다.

## Verification

- 게임 루프에서 출발점 문양과 설치한 유물로 흐르는 입자를 SDL 화면으로 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
