# 첫 전투방의 천장빛과 전경 식생 연결

- 바닥 아래 공기에서 둥글게 퍼지던 빛을 걷어내고, 천장 빛줄기의 바닥 도달 범위를 바닥 이끼와 전경 잎의 색 보정에 함께 사용한다. 밝은 부분이 잎 윗면에서 아래로 줄고 원래 외곽과 알파가 유지되도록 기존 식생을 활용한다. [맵 미술 지침](../../../../MAP_VISUAL_GUIDE.md#7-조명과-접지감)
- 전경 식생 끝이 바닥 가장자리에서 빛을 받도록 배치한다. 세 발판과 충돌 판정은 기존 값을 사용한다.
- 원경에는 중경 비석의 크기와 기울기를 달리한 세 실루엣을 배치한다. 원본 알파를 보존하고 RGB를 동굴 공기색에 가깝게 섞어 가까운 비석보다 대비를 낮춘다.
- [바닥 전투](../../../../docs/combat-room-lighting-gameplay.png)와 [상단 시점](../../../../docs/combat-room-lighting-ceiling.png)은 같은 구도의 SDL 화면으로 확인한다. 하강 입구와 수정탄은 `./.venv/Scripts/python.exe tools/preview_combat_atmosphere.py --projectiles --animate --output-dir .cache/foreground-light-with-ruins`로 확인할 수 있다.
