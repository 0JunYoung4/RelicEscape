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
# Current Project State

Last synced: 2026-11-05T03:23:05

## Current Status

- 2026-11-06: Ctrl+H로 캐릭터 히트박스 빨간 테두리를 켜고 끈다. 기본 숨김이며 좌우 Ctrl·같은 프레임의 빠른 누름/해제를 지원한다.
- `Player.get_hitbox()`에 월드 좌표 몸통 영역 정의: 서기 40×140, 숙임 100×80, 전환 중 보간. 이동·점프·카메라 투영 연동 검사까지 22개 통과와 표시/숨김 픽셀·게임 렌더 확인. 지형 충돌에는 아직 연결하지 않았다.
- 2026-11-05: 실제 Git 프로젝트인 `RelicEscape`에 memoc 초기화 완료. 기존 `AGENTS.md` 지침을 보존했다.
- 2026-11-05: `main.py`와 `player.py`에 기본 캐릭터 표시, 좌우 걷기·Shift 달리기, 화면 경계, 포커스 해제 시 정지를 구현했다.
- Windows/Python 3.13.15/pico2D 1.5.1에서 실행 확인. 걷기 8프레임·달리기 16프레임과 source-v3 대기 원본을 사용한다.
- 자동 입력·이동 검사 및 50가지 프레임/방향 렌더링 검사 통과. 실제 데스크톱 창 표시 확인.
- 횡스크롤 적용: 960×540 창, 카메라 0.5배(1920×1080 월드 범위), 캐릭터 약 70px, 시험 맵 가로 6400. 화면 중앙 추적 및 맵 양 끝 제한.
- 왼쪽 위 조작·상태 텍스트 제거. 새 카메라의 추적·경계·배율·텍스트 부재 및 50종 렌더 검사 통과.
- 추가 이동 체감 피드백을 반영해 걷기 240→300, 달리기 420→525 월드 단위/s로 각각 25% 높였다.
- 승인한 다리 분리·팔 상승 점프 초안을 `assets/sprites/player/jump-right-draft-v1.png`로 원본 그대로 저장하고 프레임별 JSON을 추가했다.
- Space 점프·중력·평평한 바닥 착지·공중 이동을 구현했다. 8프레임은 물리 단계에 맞춰 선택하며 공중 재점프는 없다. 자동 검사 6개 통과 및 게임 렌더 결과 시각 확인.
- 숙이기는 `crouch-right-fast-v1.json`에서 기존 1·3·5·8번째 자세만 선택해 4프레임·0.15초로 재생한다. 기존 8프레임 PNG·JSON은 `assets/sprites/player/reference/crouch-8frame-v1/`에 원본 그대로 별도 보관하며, 빠른 정의는 이 PNG를 읽는다.
- 숙인 이동은 90 월드 단위/s, Shift보다 숙이기를 우선한다. 공중 숙임·숙인 상태 점프는 없다. 완전히 숙인 상태에서 실제 좌우 이동 시 `crawl` 상태로 8프레임을 반복하고 정지·맵 끝에서는 숙인 대기로 돌아간다.
- 다리 교차 수정 초안 `crawl-right-draft-v2.png`와 JSON으로 교체했다. v1은 비교용으로 유지한다. 배율 140/466과 지면 기준점 405/404로 기존 기어가기 높이를 유지한다. 기존 점프·숙이기 및 기어가기 검사 18개 통과와 게임 렌더 시각 확인.

## Project Snapshot

<!-- memoc:snapshot:start -->
- Last synced: 2026-11-05T03:23:05
- Detected stack: Not detected

### Source Directories

- `.agents`
- `assets`
- `docs`
- `발표&기획서`
<!-- memoc:snapshot:end -->

## Open Tasks

- 1주차(11/3~9) 남은 구현: 발판·벽 지형 충돌·벽 슬라이드·벽점프·유물 설치와 순간이동.
- 낮은 통로의 천장 판정과 일어서기 제한은 아직 없다.
- 실제 키를 길게 누르는 플레이 감각·카메라 배율 체감과 노트북 실행 확인. 왼쪽 전용 이미지는 미제작이며 현재 좌우 반전으로 표시한다.

## Completed Tasks

See `.memoc/worklog/` for full shared activity history.

## Commands

- PowerShell: 프로젝트 폴더에서 `. .\.memoc\env.ps1`
- 메모리 조회: `.\.memoc\bin\memoc.cmd summary`
- 설치: `python -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- 게임 실행: `.\.venv\Scripts\python.exe main.py`
- 기본 검사: `.\.venv\Scripts\python.exe -m py_compile main.py player.py`, `.\.venv\Scripts\python.exe -m pip check`
- 점프·렌더링 회귀 검사: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`

## Notes

- 진행 계획은 `docs/INITIAL_DESIGN.md` 8절, 확정 규칙은 같은 문서와 `docs/DESIGN_DISCUSSION.md` 참조.
- Codex 제한 환경에서 런타임 탐색에 실패하면 `MEMOC_RUNTIME_DIR=C:\Users\bagj6\AppData\Local\memoc\runtime`을 설정한다. 이 경로로 summary 실행을 확인했다.

## Change Log

See `.memoc/worklog/` and generated `.memoc/activity.md`.
