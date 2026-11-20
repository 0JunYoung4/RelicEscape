---
memoc: true
type: worklog
actor: codex
date: 2026-11-20
---
# 천장 앞 종유석 그림자

- 내장 image_gen으로 투명 배경의 거의 검은 불규칙한 종유석 실루엣을 생성했다. `assets/terrain/opening-cave-stalactite-shadow-v1.png`와 제작 프롬프트를 저장했다.
- `OpeningCave.draw_foreground`를 캐릭터 이후/HUD 이전에 연결해 천장 앞을 가린다. 반전 연결하고 캐릭터의 일반 점프 영역을 가리지 않는 크기로 배치했다. 수평 천장 충돌은 변경하지 않았다.
- PNG 2172×724 RGBA, alpha 0~255 확인. SDL 입구·중앙·문양문 렌더 확인 및 동굴 테스트 4개 통과.
