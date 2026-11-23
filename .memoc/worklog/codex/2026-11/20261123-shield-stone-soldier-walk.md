# 방패 바위 병사 걷기 모션

2026-11-23, Codex.

- `assets/concepts/shield-stone-soldier-v4.png`를 바탕으로 내장 ImageGen에서 오른쪽을 보는 걷기 자세 8개를 제작했다. HK-GP05·HK-GP31의 방향과 큰 실루엣을 읽는 원리를 참고했다. 방패는 거의 고정하고 짧은 보폭으로 두 발을 교대한다.
- `assets/sprites/enemies/shield-stone-soldier-walk-right-v1`에 투명 시트, 원본 프롬프트, 로더용 JSON을 저장했다. 방패 오른쪽 끝과 디딘 발 높이를 기준으로 프레임을 정렬했다. 표시 높이 120 월드 단위는 시안 값이다.
- `docs/shield-stone-soldier-walk-preview.gif`는 1.28초 반복 미리보기다. 디코딩 후 8프레임과 재생 시간을 확인했고, SDL 소프트웨어 렌더에서 2회 반복 및 좌우 표시를 확인했다. 몬스터 동작과 충돌은 게임에 연결하기 전이다.
