# 석판 방패 바위 병사 정면 방어 모션

2026-11-23, Codex.

- `assets/concepts/shield-stone-soldier-v5.png`를 바탕으로 방패와 몸이 함께 뒤로 밀리고, 뒷발을 디딘 뒤 방어 자세로 돌아오는 8프레임을 제작했다. HK-GP34의 정면 방패 실루엣을 참고했다.
- `assets/sprites/enemies/shield-stone-soldier-block-right-v1`에 오른쪽 투명 시트, 로더용 JSON, 생성 프롬프트를 저장했다. 지면 기준선을 맞췄으며, 방패 앞면은 시트 기준 최대 23px 뒤로 움직인다. 총 0.68초, 충격 40ms, 버티기 시작 180ms다.
- `docs/shield-stone-soldier-block-preview.gif`의 8프레임과 재생 시간을 확인했다. SDL에서 좌우 렌더와 충격·디딤 전환을 검증했다. 정면 방어 로직은 연결 전이다.
