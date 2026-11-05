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
- 기획·캐릭터 기본 이미지·1차 발표 자료 준비 상태이며 실행 가능한 게임 코드는 아직 없다.
- 개발 환경은 Python·pico2D 예정이며 자동 스택 감지는 되지 않았다.

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

- 1주차(11/3~9) 목표: 이동·점프·충돌·벽 슬라이드·벽점프·유물 설치와 순간이동.
- 오늘 작업 제안: 실행 환경과 시험 방 → 이동·점프·충돌 → 시간이 남으면 유물 복귀. 일별 일정은 확정된 기획이 아닌 제안이다.

## Completed Tasks

See `.memoc/worklog/` for full shared activity history.

## Commands

- PowerShell: 프로젝트 폴더에서 `. .\.memoc\env.ps1`
- 메모리 조회: `.\.memoc\bin\memoc.cmd summary`

## Notes

- 진행 계획은 `docs/INITIAL_DESIGN.md` 8절, 확정 규칙은 같은 문서와 `docs/DESIGN_DISCUSSION.md` 참조.
- Codex 제한 환경에서 런타임 탐색에 실패하면 `MEMOC_RUNTIME_DIR=C:\Users\bagj6\AppData\Local\memoc\runtime`을 설정한다. 이 경로로 summary 실행을 확인했다.

## Change Log

See `.memoc/worklog/` and generated `.memoc/activity.md`.
