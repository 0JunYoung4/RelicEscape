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

- 오프닝은 문양 조사 E 이후 자동 연출이며 이때 주인공은 무기를 들지 않는다. 관찰·느린 접근·손 접촉 뒤 균열 발광·흔들림·바닥 붕괴·수직 추락으로 연결한다. 순서대로 제작하며 현재 구현은 접촉 자세까지다.

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

- 문양 벽의 외곽 연결부는 유지하되 균열은 문양 안쪽에 한정하지 않고 석재 벽 전체의 위·아래·양옆에 분포시킨다. 엔딩에서 이 문양 벽을 부수고 탈출할 계획이므로 큰 조각으로 갈라질 수 있는 구조적인 금으로 표현한다. 초기에는 아직 무너지거나 뚫리지 않은 상태다.

- 기존 벽과 문양 벽을 합칠 때 원본 배경을 처음부터 다시 그리지 않는다. 기존 암벽을 그대로 보존하고 문양이 들어가는 국소 영역만 편집·합성한다.

- 문양 벽과 후면 암벽의 재질·그림체가 분리되어 보이지 않게 한다. 최신 요청은 후면 배경에 문양 벽까지 함께 그린 통합 이미지 시안이다.

- 시작 동굴 끝에는 문양 벽을 두고 그 앞에서 이동을 막는다. 바닥 이미지를 세워 별도의 끝벽을 만들지 않는다. 문양 벽 뒤로 걷는 통로를 남기지 않는다.

- 동굴에서는 캐릭터를 강조하도록 위쪽 천장/종유석과 후면 암벽을 충분히 어둡게 하고, 캐릭터는 기존 밝기를 유지한다.

- 시작 동굴은 입구가 낮고 좁으며 문양 벽 쪽으로 갈수록 천장이 완만하게 높아져 넓어진다. 이전 수평 천장 지침을 대체한다. 종유석과 실제 충돌도 같은 높이 변화를 따라간다.
- 게임용 문양 벽은 큰 문양 형태를 유지하고 미세 질감을 줄인 굵은 도트로 주변 지형과 밀도를 맞춘다. 원본 타이틀은 유지한다.

- 동굴 암벽은 같은 방향의 큰 사선 바위결이 규칙적으로 반복되지 않게 한다. 크기·방향이 다양한 바위와 짧고 불규칙한 균열을 사용한다.

- 시작 동굴은 작고 낮은 어둡고 습한 공간이다. 뒷배경을 거대한 공동·먼 바위 풍경·깊은 안개로 표현하지 않고, 플레이어 뒤에 가까운 젖은 암벽이 보이게 한다.

- memoc 프로젝트 루트는 실제 게임 저장소 `RelicEscape`이다. 상위 `2DGP`는 두 프로젝트를 담는 폴더다.
- 기존 `AGENTS.md`의 언어, 캐릭터 원본, 발표 파일 위치와 이름 규칙을 따른다.
- 플레이어 얼굴은 기본 스프라이트처럼 검은 도트 눈만 그린다. 코와 입은 생략한다.
- 계획과 구현 완료를 구분하고, 확정 규칙과 제안·미정 항목을 구분한다.
- 게임은 횡스크롤을 기본으로 한다. 2026-11-20 사용자 수정: 일반 탐험은 가까운 카메라로 공간감을 강조하고, 넓은 구도는 일부 유물 활용이 많은 맵과 보스전에서 사용한다. 왼쪽 위 조작·상태 디버그 텍스트는 표시하지 않는다.
- 일반 탐험의 현재 기본 카메라는 0.5배다. 기존 장치 시험 맵의 1/3배를 본편의 상시 구도로 사용하지 않는다. 실제 지형은 시험 지형보다 크고 두껍게 만들며, 벽점프 구간은 조작이 성립하는 간격을 별도로 설계한다. 현재 시험 지형의 크기·간격을 본 맵의 기준으로 삼지 않는다.
- 숙이기는 낮은 통로를 기어가기 위한 형태다. 왼손으로 땅을 짚어 체중을 지지하고 정글도는 오른손에 유지한다.
- 히트박스 확인 단축키는 Ctrl+H다. 기본 상태에서는 숨기고 디버그 확인 시에만 테두리를 표시한다.
- 기본 공격 키는 X다. 가로 베기의 검기 이펙트는 캐릭터 스프라이트와 별도로 제작한다.
- 기본 실행은 전체화면으로 한다. 카메라 거리는 일반 탐험/유물 활용/보스전의 용도에 맞추고 F11로 1280×720 창 모드 전환을 제공한다. 벽 슬라이드 그림은 실제 벽 접점에 맞추고 상단에서 허공을 잡는 자세가 나오지 않게 한다.
- 벽 슬라이드는 3프레임 정도의 빠른 전환을 지향한다. 시선은 벽 반대쪽의 도약 위치를 살피되 약간 아래를 향하고, 한 손은 위쪽을 잡아 버틴다. 그 팔과 가까운 다리는 굽혀 벽을 밀어낼 준비를 하고 반대 다리는 아래로 뻗어 낙하를 억제하는 자세다. 칼은 기본 원본 비율을 유지한다.
