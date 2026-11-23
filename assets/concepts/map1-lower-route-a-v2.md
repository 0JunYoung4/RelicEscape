# 하단 A파트 v2 천장 입구와 지형

오른쪽 입구는 천장 암반의 불규칙한 틈이다. 구멍 아래에는 착지면까지 열린 공간이 있다. 왼쪽 출구 상면과 버튼실 바닥은 읽기 쉽게 유지하고, 지형 옆과 밑면은 서로 다른 크기의 암석 다각형과 짧은 경사로 나눴다. [가까이에서 본 전체 맵](../../docs/map1-lower-route-a-v2-open.png)

| 자료 | 용도 |
| --- | --- |
| [기본 맵 이미지](map1-lower-route-a-v2-plate.png) | 천장 구멍과 바위가 들어간 원본. 레일과 전경 그림자 배치용. |
| [천장 전경 그림자](../terrain/lower-route-a-ceiling-shadow-v2.png) | 구멍 앞을 가리는 별도 투명 PNG. |
| [멀리서 본 전체 맵](../../docs/map1-lower-route-a-v2-covered.png) | 그림자가 입구를 가리는 상태. |
| [접근 GIF](../../docs/map1-lower-route-a-v2.gif) | 캐릭터가 아래에서 접근하면 바위 그림자가 서서히 걷히는 예시. |

미리보기는 기존 테스트룸의 [직선 레일](../sprites/rail/relic-track-blue-v4.png), [곡선 레일](../sprites/rail/relic-track-bend-v2.png), [유물 장착 파츠](../sprites/rail/relic-carriage-v2.png)를 `rail.draw_rail`과 기존 렌더 배율로 배치했다. 그림자는 입구에 붙여 두고 캐릭터 몸통과 구멍 사이의 거리에 따라 투명도를 부드럽게 바꾼다. 그림자만 변하며 착지면이나 배경의 노출은 그대로다. 미리보기의 경로와 거리 기준은 배치 검토용이다. 실제 충돌, 카메라와 레일 조작은 플레이 가능한 맵에서 조정한다.

내장 image_gen으로 v1을 편집하고 전경 그림자를 생성했다. HK-GP18의 어두운 지형 내부와 작은 이끼 경계, HK-GP22의 평평한 윗면과 비대칭 밑부분, SS-MG-03의 전경 천장과 중경을 나누는 방법을 참고했다. [맵 편집 프롬프트](map1-lower-route-a-v2-plate.prompt.txt) · [그림자 프롬프트](../terrain/lower-route-a-ceiling-shadow-v2.prompt.txt)

SDL 미리보기는 `.\.venv\Scripts\python.exe tools/preview_lower_route_a.py`로 다시 만든다.
