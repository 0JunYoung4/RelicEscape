---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-17T01:32:14
updated: 2026-11-17T01:32:14
status: active
tags:
  - memoc
  - memoc/worklog
---
# 유물 순간이동 출발점 문양

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-17T01:32:14

## Summary

- `E` 순간이동 출발점에 3초간 문양을 남기고, 유물을 들고 `Q`를 누르면 해당 위치와 자세로 한 번 복귀한다.
- 만료되거나 사용한 문양은 0.85초 동안 픽셀로 흩어져 휴대 중인 플레이어 또는 화면에 투영된 현재 유물 위치에 모인다.

## Verification

- 게임 루프에서 Q 한 번 사용, 만료 이후 입력, 설치 중 입력, 휴대·설치 상태별 흡수 위치를 확인했다. SDL 화면에서 문양과 분해·흡수 프레임을 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
