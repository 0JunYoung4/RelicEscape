---
memoc: true
type: worklog
scope: opening-cutscene
actor: codex
status: complete
---
# 조사 중 위를 향하는 시선

- 사용자 요청에 따라 기존 v2를 내장 image_gen으로 편집해 고개와 눈 방향을 살짝 오른쪽 위로 조정했다. 무기 없는 16프레임과 동작 순서 유지.
- v3 PNG/JSON/제작 프롬프트 저장. 발 접점과 몸통 가로 기준을 맞추고 기존 신장 배율·걷기 주기·손 뻗기 1.18초 유지. 소비 코드의 JSON 경로만 v3로 변경.
- 관련 unittest 4개 통과. SDL 동굴 접촉 스크린샷과 GIF로 올려다보는 방향, 발 정렬 확인. 전체 테스트는 직전 v2에서 82개 통과했으며 이번에는 관련 테스트만 실행했다.
- 다음 빛/흔들림/바닥 붕괴/추락은 미구현. memoc CLI는 기존 오프라인 캐시 부재로 사용할 수 없어 문서 링크를 직접 검사한다.

관련: [동굴 구현](../../../wiki/project/opening-cave.md), [인계](../../../04-handoff.md).
