---
memoc: true
type: core
scope: project-memory
created: 2026-11-05T03:23:05
updated: 2026-11-05T03:23:05
status: active
tags:
  - memoc
  - memoc/core
---
# Project Brief

This is the shortest project summary for a fresh agent. Keep it factual and easy to scan.

## Identity

<!-- memoc:identity:start -->
- Project name: `RelicEscape`
- Detected stack: Not detected
<!-- memoc:identity:end -->

## Current Direction

- Python·pico2D 기반 2D 횡스크롤 유적 탈출 게임. 설치한 유물의 현재 위치로 순간이동하는 능력이 핵심이다.
- 기획 기준은 [초기 기획서](../docs/INITIAL_DESIGN.md) v1.1이며, 구현 11/3~30, 최종 검증 12/1~6을 계획한다.

## How To Approach

- Start from `session-summary.md`; search before opening more files.
- Open status, handoff, rules, map, project wiki, or knowledge wiki only when the task needs them.
- After durable work, update the smallest relevant memory set.
- Do not treat generated output folders as source unless the user explicitly asks.

## Next Useful Work

- 1주차(11/3~9): 지형 충돌·벽 이동 구현에 이어 유물 설치와 순간이동 구현, 조작 체감 확인.

## Important Notes

- 2026-11-06: 걷기·달리기·점프·숙이기·기어가기, 지형 충돌·벽 슬라이드·벽점프를 실행할 수 있다. 시험 맵은 낮은 발판·세로벽 두 개·공중 발판으로 구성한다. Ctrl+H로 캐릭터·지형 경계를 확인한다.
- 실행 환경: Windows, Python 3.13.15, pico2D 1.5.1. 설치 의존성은 `requirements.txt` 참조.
