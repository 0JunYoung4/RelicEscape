---
memoc: true
type: worklog
scope: opening-cutscene
actor: codex
status: complete
---
# 문양 조사 애니메이션 16프레임 확장

- 요청에 따라 걷기 4→8, 관찰/손 뻗기 4→8로 확대. 기존 시트와 승인 SD v3를 참조해 내장 image_gen으로 4×4 투명 v2 PNG 생성, 원본 보존 및 JSON/프롬프트 저장.
- JSON의 16개 영역과 머리/발 기준점을 분석해 기존 신장과 지면에 맞춤. 걷기 11fps로 주기 유지, 손 뻗기 총 1.18초와 자동 이동 속도 유지.
- ANIMATION_DATA를 v2로 전환하고 단계 검사 프레임 기대값 갱신. 관련 4개 테스트 통과, SDL 걷기·접촉 자세 확인 및 6초 GIF 재생성.
- 후속: 접촉 후 빛·흔들림·붕괴·수직 추락은 아직 미구현.
- 최종 검증: 전체 82개 테스트 통과. 16개 프레임이 서로 다르고 이미지 경계 안에 있으며 발 기준점 정상, 기존 걷기 주기와 손 뻗기 시간 동일. 문서 상대 링크와 git diff --check 통과. 세션 요약 675B. memoc CLI는 기존 오프라인 캐시 부재로 사용 불가하여 링크를 직접 검사했다.

관련: [동굴 구현](../../../wiki/project/opening-cave.md), [인계](../../../04-handoff.md).
