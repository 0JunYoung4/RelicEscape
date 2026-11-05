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
- 2026-11-05: 사용자가 승인한 점프 초안을 저장하고 적용하도록 요청했다. 8프레임을 원본 그대로 보존하며 중간 동작은 수직 속도와 착지 상태로 선택한다. Space를 기본 키로 연결하고 공중 재점프는 허용하지 않는 초기 구현으로 둔다.
