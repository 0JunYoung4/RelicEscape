# 첫 맵 하단 A파트 환경 시안

A파트는 전투방에서 내려온 오른쪽 착지면부터, 중앙 버튼실과 상승 레일을 지나 왼쪽 상단 출구에 도착하는 구간이다. 왼쪽 끝에서 다음 파트로 이어진다. 동선 기준은 [v3 설계도 상단](../../docs/map1-lower-route-blockout-v3.png)과 [치수 초안](../../docs/map1-lower-route-blockout-v3.md)이다.

| 이미지 | 배치 용도 | 생성 프롬프트 |
| --- | --- | --- |
| [A파트 전체 시안](map1-lower-route-a-v1.png) | 오른쪽 착지면, 두 단차, 바닥 버튼실, 상승 레일, 왼쪽 연속 발판을 한 화면에서 검토 | [프롬프트](map1-lower-route-a-v1.prompt.txt) |
| [원경 배경](../terrain/lower-route-a-backdrop-v1.png) | 먼 수로 아치와 폭포, 청록 안개, 뿌리 군집으로 이루어진 시차 배경 | [프롬프트](../terrain/lower-route-a-backdrop-v1.prompt.txt) |
| [상승 레일 지지대](../structures/map1-lower-route/lower-cave-lift-support-v1.png) | 세로 레일 뒤에 놓는 비대칭 폐기둥과 고정 철물. 원본 투명 PNG | [프롬프트](../structures/map1-lower-route/lower-cave-lift-support-v1.prompt.txt) |

오른쪽 안전 착지면의 뒤쪽에는 [기존 폐기둥 잔해](../structures/map1-lower-route/lower-cave-landing-rubble-v1.png)를, 두 단차 뒤에는 낮은 돌조각과 고사리를 배치한다. 새 지지대는 버튼실 중앙에서 레일과 살짝 어긋나게 두어 파츠의 세로 이동이 읽히게 한다. 왼쪽 석등은 보행선 뒤로 물려 놓고, 중경 조형물은 동선이나 상호작용 물체보다 대비를 낮춘다.

내장 image_gen을 사용했다. **HK-CT-05**에서 큰 수직 구조 뒤로 낮은 대비의 원경을 겹치는 구성을, **SS-MG-02**에서 열린 가운데 여백과 가장자리에 모인 식생을 참고했다. 프로젝트 이끼 통로의 검은 지형 코어와 가는 이끼 상면, 기존 폐기둥의 육각 홈과 레일의 푸른 선을 외형 기준으로 삼았다.

전체 시안은 배치 확인용이다. 구현 시 지형 충돌은 v3 설계 기준과 플레이 검증으로 결정하고, 원경·중경·기존 레일과 파츠·버튼·복구 손잡이를 독립적으로 배치한다.
