# 이끼 동굴 구간의 미술 방향

시작 동굴과 처음 추락해 깨어나는 착지방은 기존 모습으로 유지한다. 옆 이끼 통로로 넘어간 뒤부터 새 표현을 적용한다. 사용자가 제공한 녹색 거리 참고 이미지의 명암·깊이·지형 가장자리 표현을 바탕으로 이끼 통로, 전투방, 전투방 아래 하강 통로의 표현을 통일한다.

- 지형의 속은 검은 덩어리로 가리고, 통행 가능한 표면과 벽의 얇은 가장자리만 읽히게 한다. 바닥 아래 전체를 밝게 보여주지 않는다.
- 거대한 밝은 각진 바위 면 대신 작은 둥근 돌, 잎, 이끼가 모인 테두리를 쓴다. 공중 발판의 아래는 불규칙한 돌·뿌리 실루엣으로 연결한다.
- 멀리 물러난 청록·남색 숲 동굴 배경은 지형보다 느리게 움직인다. 가까운 천장에는 검은 뿌리와 덩굴을 두고, 작은 포자가 떠다니도록 한다.
- 발딛는 돌 표면선을 기존 충돌 상면에 맞춘다. 방 배치, 발판 높이, 출입구, 중앙 등장, 전멸 개방과 덮개112/접근 조명 동작은 유지한다.

기존 벽 이미지는 폭360·주기 높이1536으로 확대해 풀과 자갈을 읽을 수 있게 한다. 발판 이미지는 그대로 유지한다. 각진 모서리는 투명 덩굴을 겹쳐 가리되 문틀 끝에는 별도 덩굴을 붙이지 않는다. 바닥과 천장은 자갈·이끼의 작은 높낮이가 보이도록 하고 반드시 직선으로 만들지 않는다. 실제 이동 경계는 유지한다. [덩굴로 가린 모서리](green-corner-foliage-entry.png) · [기존 착지방 유지](landing-original-preserved.png).

## 적용 범위와 확인 화면

- [이끼 통로](green-style-gallery.png) · [이동과 배경 시차 GIF](green-style-gallery-parallax.gif)
- [전투방](green-style-combat.png) · [전투방 전체](green-style-combat-map.png) · [하강 통로](green-style-shaft.png)
- [기존 시작 동굴 유지](green-style-opening.png) · [기존 문양 유지](green-style-sigil.png)

공통 렌더링은 `moss_art.py`의 `MossCaveArt`가 담당하고 `lower_caves.py`에서 사용한다. `opening_cave.py`는 변경 전 상태로 복원했다. 배경 시차는 지형 이동의0.16배, 전경은1.04배다. 잎과 뿌리는 장식이며 실제 충돌 상면은 바꾸지 않는다.

## 새 생성 자산

모두 내장 imagegen으로 생성했다. 원본, 투명 경계 크롭, 메타데이터, 정확한 생성 프롬프트를 `assets/terrain/`에 저장했다.

| 용도 | PNG | 프롬프트 |
| --- | --- | --- |
| 푸른 원경 | [배경](../assets/terrain/green-cavern-background-v1.png) | [프롬프트](../assets/terrain/green-cavern-background-v1.prompt.txt) |
| 이끼 바닥·덮개 | [바닥](../assets/terrain/green-cavern-floor-v1.png) | [프롬프트](../assets/terrain/green-cavern-floor-v1.prompt.txt) |
| 벽·기둥·입구 봉쇄 | [벽](../assets/terrain/green-cavern-wall-v1.png) | [프롬프트](../assets/terrain/green-cavern-wall-v1.prompt.txt) |
| 뿌리가 매달린 발판 | [발판](../assets/terrain/green-cavern-platform-v1.png) | [프롬프트](../assets/terrain/green-cavern-platform-v1.prompt.txt) |
| 천장 전경 실루엣 | [전경](../assets/terrain/green-cavern-canopy-v1.png) | [프롬프트](../assets/terrain/green-cavern-canopy-v1.prompt.txt) |
| 모서리 덩굴 장식 | [덩굴](../assets/terrain/green-cavern-corner-ivy-v1.png) | [프롬프트](../assets/terrain/green-cavern-corner-ivy-v1.prompt.txt) |

사용자 참고 이미지7장은 [참고 폴더](references/green-cavern-style/)에 보관했다.
