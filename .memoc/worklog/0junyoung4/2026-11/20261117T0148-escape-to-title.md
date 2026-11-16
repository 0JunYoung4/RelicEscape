---
memoc: true
type: worklog
scope: project-memory
created: 2026-11-17T01:48:33
updated: 2026-11-17T01:48:33
status: active
tags:
  - memoc
  - memoc/worklog
---
# 게임 중 Esc로 타이틀 복귀

actor: 0junyoung4
actor_source: git config user.name
branch: main
status: done
created: 2026-11-17T01:48:33

## Summary

- 시연 중 `Esc`는 동일한 창과 화면 모드로 타이틀에 복귀한다. 타이틀의 `Enter`는 초기 상태로 게임을 시작한다.
- 타이틀의 `Esc`와 두 화면의 창 닫기는 게임을 종료한다.

## Verification

- 실제 타이틀과 게임 루프 사이를 오가며 화면 모드 유지, 레일 초기화, 타이틀 종료를 검사한다.

## Related

- [Worklog](../../README.md)
- [Actor](../../../actors/0junyoung4.md)
