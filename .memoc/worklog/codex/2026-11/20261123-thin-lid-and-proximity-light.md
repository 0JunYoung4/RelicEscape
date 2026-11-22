# 얇은 상판·고정 턱과 접근 조명

- 사용자 수정: 바닥 전체가 움직이는 느낌 제거. 얇은 윗덮개만 이동하고 아래 폭을 좁혀 고정 부분과 자연스럽게 연결. 추가 수정: 덮개와 동시에 밝히지 말고 열린 구멍에 접근할 때 점차 밝힌다.
- 새 상판은220×18(기존300×80), 고정 돌 받침은352×64. 입구220 아래18 지점부터 폭180 통로로 이어지고 받침은 정지한다. 같은 바닥 재질 내장 imagegen으로 각각 생성.
- 원본/알파 크롭/JSON/정확한 프롬프트: assets/terrain/moss-combat-floor-cover-v2* 및 moss-combat-shaft-rim-v1*. 기존 수직 통로v1은 폭180과 착지-960에 환산해 재사용.
- 그림과 충돌 모두 상판/고정 턱/하강 벽으로 분리. 열린 뒤 양옆 고정 턱 지지·부분 개방 좌우 지지·중앙 낙하 검사 유지. 덮개 밑 바닥 비침을 차단하고 고정 턱은 어둠으로 연결.
- shaft_visibility는 덮개 완전 개방 후 플레이어 발에서 입구까지 거리240 이내일 때 거리별 smoothstep 밝기를 목표로0.7초 속도로 보간한다. 높은 발판/먼 지점에서는 검게 유지. 방 입장/재시작 때 초기화, 회복 중에도 시간 갱신. 벽 속 검정은 조명에 영향받지 않는다.
- 관련28개 검사 통과. 실제 SDL 닫힘→먼 위치에서 개방/검정 유지→걷기 접근→밝기 증가 미리보기: archive/unused-assets/2026-11-23/docs/combat-shaft-v3-approach.gif.

생성 파일(내장 imagegen):

- [얇은 덮개 PNG](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-floor-cover-v2.png) · [프롬프트](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-floor-cover-v2.prompt.txt)
- [고정 턱 PNG](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-shaft-rim-v1.png) · [프롬프트](../../../../archive/unused-assets/2026-11-23/assets/terrain/moss-combat-shaft-rim-v1.prompt.txt)

- 최종 전체165개 테스트(66.462초), 컴파일 통과. 전체 방·새 착지 화면 갱신.
