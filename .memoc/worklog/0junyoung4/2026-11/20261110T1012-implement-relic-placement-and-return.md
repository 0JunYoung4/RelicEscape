---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-10T10:12:00
updated: 2026-11-10T10:12:00
status: active
tags:
  - memoc
  - memoc/worklog
---
# Implement relic placement and return

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-10T10:12:00

## Summary

- `E`로 지상·공중 발 좌표에 설치하고 다시 누르면 그 좌표로 귀환해 자동 회수한다. 귀환 프레임의 속도와 점프 추진을 초기화하고 설치 당시의 숙임 상태를 복원한다.
- A안 12×12 월드 스프라이트를 1.2초 동안 24단계로 최대 2px 띄워 그린다. 부유는 표시 위치에만 적용한다.
- 사용자 피드백에 따라 유물 표시점을 설치 당시 몸통 높이로 올렸다. 귀환 기준점은 발 위치다.

## Verification

- 자동 검사 55개 통과. 지상·공중 입력, 고정 좌표, 회수, 귀환 뒤 중력, 낮은 천장 아래 숙임 복원을 확인했다. SDL 소프트웨어 렌더에서 부유 높이 차이 2px와 루프를 확인했다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
