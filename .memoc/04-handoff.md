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
# Agent Handoff

Last synced: 2026-11-05T03:23:05

## What Changed

- 승인한 점프 초안 PNG·프레임 JSON 저장. Space 점프, 중력, 바닥 착지와 공중 이동을 연결했다. 0.5배 횡스크롤 카메라를 유지하며 걷기 300·달리기 525로 속도를 높였다.

## Next Steps

- 사용자와 점프 높이·공중 시간·착지 체감을 확인하고 발판·벽 지형 충돌을 구현한다.

## Blockers

_None yet._

## Do Not Touch Without Asking

_None yet._

## Verified

- py_compile, pip check, git diff --check 통과.
- SDL 소프트웨어 렌더러에서 대기/걷기/달리기 전체 25프레임 × 좌우 2방향 렌더링 통과.
- 자동 검사: 속도 차이, 대기 복귀, 양쪽 Shift, 좌우 동시 입력, 포커스 해제, 화면 경계, 프레임률 독립 이동.
- 실제 데스크톱 게임 창에서 기본 캐릭터 표시 확인.
- 새 카메라의 중앙 추적, 맵 양 끝 제한, 1920 월드 단위 뷰, 약 70px 캐릭터 및 HUD 부재를 SDL 렌더 결과로 확인했다.
- `unittest discover -s tests -v` 6개 통과: 준비·상승·착지, 30/60/144fps 단계 순서·높이, 공중 재점프 방지, 공중 이동·카메라, 착지 후 이동 복귀, 양방향 렌더링.
- 승인한 생성 원본과 저장 PNG의 SHA256 일치 확인. 실제 게임 렌더의 준비·정점·착지 자세를 시각 확인했다.

## Not Verified

- 실제 키 조작에서의 점프·착지 체감과 노트북 실행. 현재 착지 판정은 평평한 시험 바닥에 한정한다.

## Resume Notes

- `.\.venv\Scripts\python.exe main.py`로 실행. A/D·방향키 이동, Shift 달리기, Space 점프, Esc 종료.
- 이미지 PNG는 보존했다. 왼쪽은 임시 반전이므로 정글도 손까지 보존하는 전용 에셋은 별도 준비한다.
- 카메라 배율은 `main.py`의 `CAMERA_ZOOM`, 시험 맵 너비는 `WORLD_WIDTH`에서 조정한다. 실행 중인 이전 창은 재실행해야 변경이 반영된다.
- 점프 초깃값은 `player.py`: JUMP_SPEED=900, GRAVITY=2000, 준비 0.06초, 착지 0.12초. 이 값은 확정된 기획 규칙이 아닌 조정 가능한 구현 초깃값이다.

## Suggested Reads

Search first, then open only files named above.
