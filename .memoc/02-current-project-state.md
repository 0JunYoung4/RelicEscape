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

- 2026-11-05: 실제 Git 프로젝트인 `RelicEscape`에 memoc 초기화 완료. 기존 `AGENTS.md` 지침을 보존했다.
- 2026-11-05: `main.py`와 `player.py`에 기본 캐릭터 표시, 좌우 걷기·Shift 달리기, 화면 경계, 포커스 해제 시 정지를 구현했다.
- Windows/Python 3.13.15/pico2D 1.5.1에서 실행 확인. 걷기 8프레임·달리기 16프레임과 source-v3 대기 원본을 사용한다.
- 자동 입력·이동 검사 및 50가지 프레임/방향 렌더링 검사 통과. 실제 데스크톱 창 표시 확인.
- 횡스크롤 적용: 960×540 창, 카메라 0.5배(1920×1080 월드 범위), 캐릭터 약 70px, 시험 맵 가로 6400. 화면 중앙 추적 및 맵 양 끝 제한.
- 왼쪽 위 조작·상태 텍스트 제거. 새 카메라의 추적·경계·배율·텍스트 부재 및 50종 렌더 검사 통과.

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

- 1주차(11/3~9) 남은 구현: 점프·중력·지형 충돌·벽 슬라이드·벽점프·유물 설치와 순간이동.
- 실제 키를 길게 누르는 플레이 감각·카메라 배율 체감과 노트북 실행 확인. 왼쪽 전용 이미지는 미제작이며 현재 좌우 반전으로 표시한다.

## Completed Tasks

See `.memoc/worklog/` for full shared activity history.

## Commands

- PowerShell: 프로젝트 폴더에서 `. .\.memoc\env.ps1`
- 메모리 조회: `.\.memoc\bin\memoc.cmd summary`
- 설치: `python -m venv .venv`, `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`
- 게임 실행: `.\.venv\Scripts\python.exe main.py`
- 기본 검사: `.\.venv\Scripts\python.exe -m py_compile main.py player.py`, `.\.venv\Scripts\python.exe -m pip check`

## Notes

- 진행 계획은 `docs/INITIAL_DESIGN.md` 8절, 확정 규칙은 같은 문서와 `docs/DESIGN_DISCUSSION.md` 참조.
- Codex 제한 환경에서 런타임 탐색에 실패하면 `MEMOC_RUNTIME_DIR=C:\Users\bagj6\AppData\Local\memoc\runtime`을 설정한다. 이 경로로 summary 실행을 확인했다.

## Change Log

See `.memoc/worklog/` and generated `.memoc/activity.md`.
