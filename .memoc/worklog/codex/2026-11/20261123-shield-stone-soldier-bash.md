# 석판 방패 바위 병사 밀쳐치기 모션

2026-11-23, Codex.

- `assets/concepts/shield-stone-soldier-v5.png`를 바탕으로 방패를 몸에 붙이고 웅크리는 준비, 앞발을 디디는 밀쳐치기, 자세를 버텼다가 방패를 거두는 회복을 8프레임으로 제작했다. HK-GP34의 방패 방향 판독성을 참고했다.
- `assets/sprites/enemies/shield-stone-soldier-bash-right-v1`에 오른쪽 투명 시트, 로더용 JSON, 생성 프롬프트를 기록했다. 뒤꿈치와 지면 기준선을 맞췄다. 1.05초의 단발 모션이며 그림 기준 타격 자세는 5~6프레임(510~740ms)이다.
- `docs/shield-stone-soldier-bash-preview.gif`에서 8프레임 재생을 확인했다. SDL 소프트웨어 렌더에서 좌우 방향과 타격 시점의 프레임 전환을 검사했다. 공격 판정은 아직 게임에 연결하기 전이다.
