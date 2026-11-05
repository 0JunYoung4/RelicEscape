---
memoc: true
type: state
scope: project-memory
created: 2026-11-05T03:23:05
updated: 2026-11-05T03:23:05
status: active
tags:
  - memoc
  - memoc/state
---
# Decisions

Durable project decisions live here. Keep entries short, dated, and useful to future agents.

## Decision Log

- 2026-11-05: 첫 구현은 기본 캐릭터 좌우 걷기·Shift 달리기까지로 제한하고 점프·충돌은 다음 단계로 둔다. 이동량은 초당 속도와 경과 시간으로 계산한다.
- 기존 PNG를 보존하고 런타임 잘라 그리기·배율·발 기준점으로 세 동작을 연결한다. 왼쪽은 임시 반전이며 전용 왼쪽 에셋이 필요하다.
- 2026-11-05: 사용자의 횡스크롤·넓은 카메라 요청을 반영해 월드 좌표와 화면 좌표를 분리했다. 창 960×540 유지, 카메라 배율 0.5로 시작하며 캐릭터는 약 70px 높이다. 조작·상태 텍스트는 제거한다.
