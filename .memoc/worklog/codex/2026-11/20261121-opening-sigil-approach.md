---
memoc: true
type: worklog
scope: opening-cutscene
actor: codex
status: complete
---
# 문양 조사 후 맨손 접근과 손 뻗기

- 요청: E 이후 조작 없는 오프닝 중 무기 없이 관찰·느린 접근·손 접촉까지 우선 제작.
- 승인 SD v3와 기존 걷기를 참조해 내장 image_gen으로 투명 4×2 시트 8프레임 생성. PNG는 보존하고 JSON으로 영역·발 기준점·재생 시간을 맞춤. 제작 프롬프트 저장.
- `opening_cutscene.SigilApproach`: 거리/접지 검사, 기존 공격 초기화, 관찰·자동 이동·손 뻗기·접촉 유지. 큰 dt와 리셋 지원.
- 동굴 루프: E 표시/입력, 연출 중 일반 조작 차단과 맨손 시트 표시, R 리셋. Esc/F11 유지.
- 검증: 전체 unittest 82개 통과. 새 테스트 4개로 시작 조건, 단계/종점, 큰 dt/리셋, 실제 루프 입력 차단 확인. SDL 6초 GIF와 접촉 스크린샷으로 발 정렬과 최종 자세 확인.
- 후속: 강한 빛·흔들림·붕괴·수직 추락. 현재는 touch에서 유지.
- 문서 확인: 변경 문서의 상대 링크와 위키 허브 연결 정상, 세션 요약 664B, git diff --check 통과. memoc lint-wiki는 로컬 패키지/오프라인 캐시 부재(ENOTCACHED)로 실행 불가하여 링크를 직접 검사했다.

관련: [동굴 구현](../../../wiki/project/opening-cave.md), [인계](../../../04-handoff.md).
