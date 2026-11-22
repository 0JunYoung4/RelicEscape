# 두꺼워진 덮개와 바닥에 이어지는 통로 입구

- 요청: 덮개 두께 소폭 증가, 통로와 기존 바닥 접합 자연스럽게 개선.
- 덮개32(기존18), 새 cover-v3. 고정 턱은 잘린 직사각 블록 대신 바닥으로 넓게 이어지는 rim-v2로 교체. 두 자산 모두 내장 imagegen, 기존 방/자산/실제 화면 참조.
- rim 알파8 경계 크롭으로 바깥 페이드 보존. 원본(2172×724), 크롭(7,188,2158,706), 윗면 anchor4/턱 anchor56/중심1078.5 사용. 윗면과 아래 암벽을 분리 렌더해 높이0/-32/-96을 맞춘다.
- 넓은 연결부 총폭1006은 양옆 바닥을 겹쳐 그리는 영역이다. 실제 상부 슬롯248/통로180/깊이960. 원본 안쪽 경계에 맞춰 슬롯·덮개·충돌 위치를 정렬했다.
- 상판만 우측 이동, 고정 턱 지지, 접근 시 밝기, 지하/벽속 암전 유지. 관련28개 검사 통과.
- 실제 SDL 닫힘/부분/개방 및 접근 GIF·전체 방·하단 착지 화면 갱신: docs/combat-shaft-v4-* 및 combat-room-current-layout.png.

생성 파일과 정확한 프롬프트(내장 imagegen):

- [덮개 PNG](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-floor-cover-v3.png) · [프롬프트](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-floor-cover-v3.prompt.txt)
- [고정 연결부 PNG](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-shaft-rim-v2.png) · [프롬프트](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-shaft-rim-v2.prompt.txt)

- 최종 전체165개 테스트(64.727초), 컴파일·diff 검사 통과.
