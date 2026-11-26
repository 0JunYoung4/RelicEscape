# 하단 동선 게임용 미술

하강로부터 C 전실까지의 [v2 구상](../../concepts/map1-route-art-v2/generation-prompts.md)을 본편 지형과 장치 좌표에 맞췄다.

| 이미지 | 제작과 사용 |
| --- | --- |
| `a-far.png`, `bc-far.png` | 이전 하단 동선 작업 초안의 청록 수로 배경이다. A와 B–C의 원경으로 쓰고 A–B 절벽 아래까지 배경을 잇는다. |
| `a-terrain.png`, `c-terrain.png` | 기존 A 원화와 C 전실 원화에서 바닥 윤곽, 석주, 회수 장치, 봉인문과 석등을 보존한다. 푸른 공기를 투명 처리하고 돌의 색과 빛 닿는 부분을 조정했다. |
| `mint-light.png` | 천장 틈에서 넓어지며 바닥에서 사라지는 청록빛 이미지다. 구간별 위치와 밝기는 런타임에서 정한다. |

A·C 지형과 틈빛은 프로젝트 루트에서 `python -m tools.bake_lower_route_art`로 다시 만들 수 있다. 아치와 비석은 [첫 전투방 자산](../combat-room-v2/midground-prompts.md)을 사용한다. [본편 화면](../../../docs/map1-lower-route-runtime.jpg)
