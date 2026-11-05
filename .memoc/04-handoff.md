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

- 기본 이동에 0.5배 횡스크롤 카메라를 연결했다. 월드 범위 6400, 뷰 너비 1920, 기본 캐릭터 약 70px. 조작·상태 텍스트 제거.

## Next Steps

- 사용자와 확대된 시야·캐릭터 크기·이동 체감을 확인한 뒤 점프·중력·지형 충돌을 구현한다.

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

## Not Verified

- 새 카메라로 실제 키를 길게 눌렀을 때의 조작 감각과 노트북 실행. 이전 UI 검사에서는 사용자 조작이 감지되어 자동 키 입력은 진행하지 않았다.

## Resume Notes

- `.\.venv\Scripts\python.exe main.py`로 실행. A/D·방향키 이동, Shift 달리기, Esc 종료.
- 이미지 PNG는 보존했다. 왼쪽은 임시 반전이므로 정글도 손까지 보존하는 전용 에셋은 별도 준비한다.
- 카메라 배율은 `main.py`의 `CAMERA_ZOOM`, 시험 맵 너비는 `WORLD_WIDTH`에서 조정한다. 실행 중인 이전 창은 재실행해야 변경이 반영된다.

## Suggested Reads

Search first, then open only files named above.
