---
memoc: true
type: wiki
scope: project-memory
status: active
tags:
  - memoc
  - memoc/project-wiki
  - memoc/wiki
  - memoc/project-doc
updated: 2026-11-05T03:54:36
created: 2026-11-05T03:54:36
confidence: medium
---
# 기본 이동 프로토타입

`main.py`는 960×540 pico2D 창, 횡스크롤 카메라와 입력·렌더 루프를 관리한다. `player.py`는 월드 위치, 바라보는 방향과 대기·걷기·달리기 애니메이션을 처리한다.

## 동작

- A/D 또는 방향키로 좌우 이동. Shift를 누르면 달린다. 좌우 동시 입력은 정지한다.
- 걷기 180 월드 단위/s, 달리기 320 월드 단위/s. 프레임 경과 시간을 곱해 이동하고 맵 양쪽 64 월드 단위 여백으로 제한한다.
- 키 상태는 이벤트 처리 후 SDL_GetKeyboardState로 읽는다. 창 포커스가 없으면 이동 입력을 0으로 처리한다.
- 바닥 높이는 월드 y=200(화면 y=100)이며 점프·중력·지형 충돌은 아직 없다.

## 카메라

- `CAMERA_ZOOM=0.5`로 가로·세로 2배 넓은 월드 범위(1920×1080)를 표시한다. 기본 캐릭터 화면 높이는 약 70px이다.
- 시험 맵 너비는 `WORLD_WIDTH=6400`이다. 캐릭터가 화면 중앙에 도달하면 카메라가 따라가며 맵 양 끝에서 멈춘다.
- 렌더링 시에만 `(월드 x - 카메라 x) × 배율`, `월드 y × 배율`로 변환한다. 애니메이션 크기와 발 기준점에도 같은 배율을 적용한다.
- 바닥 줄눈은 월드에 고정된 임시 스크롤 확인용 표시다. 조작·상태 텍스트는 표시하지 않는다.

## 이미지

- 대기: 승인된 concepts/source-v3 원본의 영역을 직접 그린다.
- 걷기: walk-right-v1.png와 JSON, 8프레임·10fps·1.5배.
- 달리기: run-right-v1.png와 JSON, 16프레임·16fps·0.5배.
- 위 이미지별 배율에 카메라 배율을 추가로 곱해 표시한다.
- JSON 좌표는 왼쪽 위 기준이다. 그릴 때 pico2D의 왼쪽 아래 기준으로 변환하고 발 기준점과 배율을 적용한다.
- PNG는 수정하지 않았다. 왼쪽은 임시 반전이므로 전용 에셋이 필요하다.

## 실행 및 검증

`.\.venv\Scripts\python.exe main.py`로 실행한다. 설치 방법은 프로젝트 README 참조.

2026-11-05에 입력·이동 자동 검사와 모든 프레임의 좌우 50회 렌더 검사를 통과했다. 카메라 변경 후에도 이동·배율·추적·맵 양 끝 제한·텍스트 부재 및 50회 렌더 검사를 통과했다. 장시간 키 조작 감각과 노트북 실행은 추가 확인 대상이다.

## Related

- [Project Wiki](README.md)
- [Current Project State](../../02-current-project-state.md)
- [Handoff](../../04-handoff.md)
