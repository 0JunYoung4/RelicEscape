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
# Project Rules

Durable user and project preferences live here. Update when the user gives a rule that should persist across sessions.

## Operating Rules

- Keep `AGENTS.md` and `CLAUDE.md` as short entry files; durable context belongs under `.memoc/`.
- Do not track generated output folders such as `out/`, `.next/`, `dist/`, `build/` unless the user explicitly asks.
- Update `.memoc/04-handoff.md` after substantial work so the next agent can resume quickly.
- Use `.memoc/05-done-checklist.md` before saying substantial work is complete.

## Agent Behavior Preferences

- Be factual and operational in memory docs.
- Keep memory notes concise; do not paste temporary command output unless it changes future work.
- Preserve user changes and avoid reverting unrelated work.
- State unverified parts honestly in the final answer and handoff.

## Project-Specific Rules

- memoc 프로젝트 루트는 실제 게임 저장소 `RelicEscape`이다. 상위 `2DGP`는 두 프로젝트를 담는 폴더다.
- 기존 `AGENTS.md`의 언어, 캐릭터 원본, 발표 파일 위치와 이름 규칙을 따른다.
- 계획과 구현 완료를 구분하고, 확정 규칙과 제안·미정 항목을 구분한다.
- 게임은 횡스크롤을 기본으로 하고, 넓은 카메라 구도로 캐릭터를 작게 보여준다. 왼쪽 위 조작·상태 디버그 텍스트는 최종 화면에 표시하지 않는다. 현재 프로토타입에서도 제거했다.
- 숙이기는 낮은 통로를 기어가기 위한 형태다. 왼손으로 땅을 짚어 체중을 지지하고 정글도는 오른손에 유지한다.
- 히트박스 확인 단축키는 Ctrl+H다. 기본 상태에서는 숨기고 디버그 확인 시에만 테두리를 표시한다.
