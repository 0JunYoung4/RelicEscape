# 석판 방패 바위 병사 걷기 모션

2026-11-23, Codex.

- 새 콘셉트 `assets/concepts/shield-stone-soldier-v5.png`의 두 청동 띠, 잠금 홈과 푸른 눈을 기준으로 걷기 시트를 다시 만들었다. HK-GP34에서 참고한 방패 방향의 판독성을 유지했다.
- `assets/sprites/enemies/shield-stone-soldier-walk-right-v2`는 오른쪽을 보는 투명 8프레임 시트와 프레임별 시간·발 기준점 JSON이다. 방패를 가슴 가까이 든 자세, 짧은 보폭, 착지 직후 체중을 싣는 긴 박자를 적용했다. 한 주기는 1.44초이며 표시 높이 시안은 120 월드 단위다.
- `docs/shield-stone-soldier-walk-v2-preview.gif`에서 8프레임 반복과 시간을 검사했다. 발 위치와 방패 전면을 정렬했고, SDL 소프트웨어 렌더에서 좌우 2회 반복을 확인했다. 몬스터의 로직과 충돌 설정은 게임에 연결하기 전이다.
