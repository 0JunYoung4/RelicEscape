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

- 1주차(11/3~9): 이동·점프 구현에 이어 발판·벽 충돌·벽 이동·유물 설치와 순간이동 구현.

## Important Notes

- 2026-11-05: `main.py`에서 대기·걷기·Shift 달리기·Space 점프와 평평한 바닥 착지를 실행할 수 있다. 점프 이미지는 승인한 8프레임 초안이다.
- 실행 환경: Windows, Python 3.13.15, pico2D 1.5.1. 설치 의존성은 `requirements.txt` 참조.
