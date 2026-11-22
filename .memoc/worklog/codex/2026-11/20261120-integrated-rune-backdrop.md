---
memoc: true
type: worklog
actor: codex
date: 2026-11-20
---
# 문양 벽을 포함한 통합 뒷배경 시안

- 사용자 요청으로 별도 문양 석판과 배경의 괴리감을 줄이는 한 장의 통합 배경을 내장 image_gen으로 제작했다.
- `opening-cave-backdrop-v2.png`를 수정 대상으로, 도트 문양 벽을 디자인 참조로 사용해 암벽에 직접 새긴 문양으로 표현했다.
- `archive/unused-assets/2026-11-23/assets/terrain/opening-cave-backdrop-rune-v1.png`와 프롬프트 저장. 시각 검토 및 Pillow 디코딩 확인.
- 게임 코드에는 적용하지 않았다. 적용 시 문양 위치와 바닥/천장 마스크의 가림을 실제 렌더로 맞춰야 한다.
