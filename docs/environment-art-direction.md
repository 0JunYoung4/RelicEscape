# 이끼 동굴 구간의 미술 방향

시작 동굴과 처음 추락해 깨어나는 착지방은 기존 모습으로 유지한다. 옆 이끼 통로로 넘어간 뒤부터 새 표현을 적용한다. 사용자가 제공한 녹색 거리 참고 이미지의 명암·깊이·지형 가장자리 표현을 바탕으로 이끼 통로, 전투방, 전투방 아래 하강 통로의 표현을 통일한다.

- 지형의 속은 검은 덩어리로 가리고, 통행 가능한 표면과 벽의 얇은 가장자리만 읽히게 한다. 바닥 아래 전체를 밝게 보여주지 않는다.
- 거대한 밝은 각진 바위 면 대신 작은 둥근 돌, 잎, 이끼가 모인 테두리를 쓴다. 공중 발판의 아래는 불규칙한 돌·뿌리 실루엣으로 연결한다.
- 멀리 물러난 청록·남색 숲 동굴 배경은 지형보다 느리게 움직인다. 가까운 천장에는 검은 뿌리와 덩굴을 두고, 작은 포자가 떠다니도록 한다.
- 발딛는 돌 표면선을 기존 충돌 상면에 맞춘다. 방 배치, 발판 높이, 출입구, 중앙 등장, 전멸 개방과 덮개112/접근 조명 동작은 유지한다.

기존 벽 이미지는 폭360·주기 높이1536으로 확대해 풀과 자갈을 읽을 수 있게 한다. 발판 이미지는 그대로 유지한다. 각진 모서리는 투명 덩굴을 겹쳐 가리되 문틀 끝에는 별도 덩굴을 붙이지 않는다. 바닥과 천장은 자갈·이끼의 작은 높낮이가 보이도록 하고 반드시 직선으로 만들지 않는다. 실제 이동 경계는 유지한다. [덩굴로 가린 모서리](green-corner-foliage-entry.png) · [기존 착지방 유지](landing-original-preserved.png).

## 적용 범위와 확인 화면

- [이끼 통로](green-style-gallery.png) · [이동과 배경 시차 GIF](green-style-gallery-parallax.gif)
- [전투방 최신 모습](combat-atmosphere-combat.png) · [전후 비교](combat-atmosphere-comparison.jpg) · [하강 통로](combat-atmosphere-shaft.png)
- [기존 시작 동굴 유지](green-style-opening.png) · [기존 문양 유지](green-style-sigil.png)

공통 렌더링은 `moss_art.py`의 `MossCaveArt`가 담당하고 `lower_caves.py`에서 사용한다. `opening_cave.py`는 변경 전 상태로 복원했다. 배경 시차는 지형 이동의0.16배다. 천장 덩굴은 지형과 같은 월드 좌표에 고정한다. 잎과 뿌리는 장식이며 실제 충돌 상면은 바꾸지 않는다.

천장 덩굴을 화면 상단에 붙이거나 천장의 화면 진입 여부에 따라 배치 기준을 바꾸지 않는다. 이끼 통로는 기존 포자 영역 상단과 같은 `GALLERY_CEILING_Y=900`, 전투방은 실제 천장 `COMBAT_CEILING_Y`에 배치한다. 천장 위는 검게 채우고, 기존 불규칙한 아래 윤곽은 유지한다. 카메라는 두 구간 모두 캐릭터의 가로·세로 위치를 따라가며 천장을 보이게 하려는 높이 제한을 사용하지 않는다. 지상에서는 발밑 여백을 확보하고, 하강 통로는 기존 추적을 유지한다. [통로 지상](ceiling-vines-gallery-floor.png) · [통로 발판](ceiling-vines-gallery-platform.png) · [전투방 지상](ceiling-vines-combat-floor.png) · [전투방 상승](ceiling-vines-combat-high.png) · [높이별 비교 GIF](ceiling-vines-follow.gif).

## 전투방의 깊이와 조명 개선

전투방에는 뿌리가 감싼 비대칭 폐아치를 낮은 대비의 중경으로 추가했다. 먼 숲은 더 어두운 청록색으로 눌렀고, 좌우의 어둠 강도를 다르게 해 중앙 전투 공간을 남겼다. 오른쪽 위에서 중앙으로 퍼지는 부드러운 사선 빛줄기와 약한 대기광을 겹쳤다. 포자는32개에서18개로 줄였다. 빛은 배경에 합성하므로 적·캐릭터·유물과 지형의 검은 속을 하얗게 덮지 않는다.

가까운 전경에는 큰 잎과 굽은 뿌리를 좌우 다른 높이·크기로 배치했다. 월드 천장에 고정하고 천장보다 높은 부분은 잘라, 카메라가 상승해도 화면 위로 다시 붙거나 위치가 바뀌지 않는다. 중앙과 하단의 전투·착지 공간은 비웠다. 기존 발판·벽·적4마리·충돌·덮개112·개방과 접근 조명·카메라 규칙은 유지한다. 시작 동굴·최초 착지방·이끼 통로에는 적용하지 않는다.

`combat_scenery.py`의 `CombatScenery`가 중경·명암·빛줄기·전경을 맡는다. `MossCaveArt.combat_scenery()`는 전투방에 처음 필요할 때 자산을 읽는다. 전투방 배경 색조는 그리기 후 원래 값으로 되돌려 통로로 나가도 색이 변하지 않는다. 새 효과는 지면 아래로 그리지 않으며 호출자의 SDL 클립과 블렌드 상태를 보존한다.

[지상](combat-atmosphere-floor.png) · [적4마리와 전투 시야](combat-atmosphere-combat.png) · [상승 시점](combat-atmosphere-high.png) · [하강](combat-atmosphere-shaft.png) · [카메라 높이 변화 GIF](combat-atmosphere-camera.gif) · [개선 전후 비교](combat-atmosphere-comparison.jpg).

SDL 소프트웨어 렌더로 위 화면과 GIF를 생성해 확인했다. 재생성은 `.\.venv\Scripts\python.exe tools/preview_combat_atmosphere.py --animate`. 장시간 수동 키 조작과 실기기별 프레임 성능은 별도 확인 사항이다.

## 새 생성 자산

모두 내장 imagegen으로 생성했다. 원본, 투명 경계 크롭, 메타데이터, 정확한 생성 프롬프트를 `assets/terrain/`에 저장했다.

유물 획득 전 통로의 지면 기둥은 `green-cavern-ground-pillar-v2` 전용 이미지를 사용한다. 사용자 지정 할로우 나이트 녹색 거리 참고의 깔끔한 윤곽·거의 검은 청록색 돌몸체·둥근 잎과 이끼·감긴 덩굴을 반영했다. 직사각형 돌몸체의 실제 폭140·높이242는 유지하고 JSON의 `collision_rect`로 윗면과 양옆을 맞춘다. 바닥보다 먼저 그려 밑동이 바닥 식생 속에 묻히도록 한다. v1은 비교 초안이며 게임에서는 v2만 사용한다. [적용 화면](green-ground-pillar-gallery.png) · [기둥 위 착지](green-ground-pillar-standing.png) · [확대 화면](green-ground-pillar-closeup.png).

| 용도 | PNG | 프롬프트 |
| --- | --- | --- |
| 푸른 원경 | [배경](../assets/terrain/green-cavern-background-v1.png) | [프롬프트](../assets/terrain/green-cavern-background-v1.prompt.txt) |
| 이끼 바닥·덮개 | [바닥](../assets/terrain/green-cavern-floor-v1.png) | [프롬프트](../assets/terrain/green-cavern-floor-v1.prompt.txt) |
| 벽·기둥·입구 봉쇄 | [벽](../assets/terrain/green-cavern-wall-v1.png) | [프롬프트](../assets/terrain/green-cavern-wall-v1.prompt.txt) |
| 뿌리가 매달린 발판 | [발판](../assets/terrain/green-cavern-platform-v1.png) | [프롬프트](../assets/terrain/green-cavern-platform-v1.prompt.txt) |
| 천장 전경 실루엣 | [전경](../assets/terrain/green-cavern-canopy-v1.png) | [프롬프트](../assets/terrain/green-cavern-canopy-v1.prompt.txt) |
| 모서리 덩굴 장식 | [덩굴](../assets/terrain/green-cavern-corner-ivy-v1.png) | [프롬프트](../assets/terrain/green-cavern-corner-ivy-v1.prompt.txt) |
| 유물 통로의 지면 기둥 | [기둥](../assets/terrain/green-cavern-ground-pillar-v2.png) | [프롬프트](../assets/terrain/green-cavern-ground-pillar-v2.prompt.txt) |
| 전투방 중경 폐아치 | [중경](../assets/terrain/green-combat-midground-ruins-v1.png) | [프롬프트](../assets/terrain/green-combat-midground-ruins-v1.prompt.txt) |
| 전투방 근접 뿌리와 큰 잎 | [전경](../assets/terrain/green-combat-foreground-roots-v1.png) | [프롬프트](../assets/terrain/green-combat-foreground-roots-v1.prompt.txt) |

전투방 신규2종은 내장 imagegen의 투명 원본 PNG를 편집 없이 보관하며, 원본 자체를 렌더에 사용한다. 용도·크기·고정점은 각 PNG와 같은 이름의 JSON에 기록했다. 조명은 SDL의 색·알파 메시로 그려 별도 이미지가 없다.

사용자 참고 이미지7장은 [참고 폴더](references/green-cavern-style/)에 보관했다.

## 유물 획득 구조물 디자인 시안

첫 유물 지점에 놓을 구조물 v1은 이끼와 덩굴에 잠식된 **깨진 육각 봉인석과 낮은 받침대**다. 기존 순간이동 문양의 육각 외곽과 짝을 이룬 홈을 돌에 새겼다. 윗부분을 비대칭으로 부수고, 유물이 놓이는 중앙은 식생 없이 비워 시선을 모은다. 맵의 어두운 청록색 돌·둥근 잎·정돈된 손그림 윤곽을 따른다.

현재는 **디자인 및 배치 미리보기만 제작했으며 게임에는 적용하지 않았다**. 높이380월드, 바닥에 묻히는 기준점과 기존 유물 높이100을 메타데이터에 기록했다. 구조물 PNG에는 유물을 넣지 않아 획득 시 별도로 사라질 수 있다. 향후 충돌과 상호작용 여부는 별도 구현 사항이다.

[투명 구조물 PNG](../assets/concepts/relic-acquisition-shrine-v1.png) · [원본](../assets/concepts/relic-acquisition-shrine-v1-source.png) · [정확한 내장 imagegen 프롬프트](../assets/concepts/relic-acquisition-shrine-v1.prompt.txt) · [배치 메타데이터](../assets/concepts/relic-acquisition-shrine-v1.json) · [기본 배율 배치 시안](relic-acquisition-shrine-v1-gallery.png) · [확대 배치 시안](relic-acquisition-shrine-v1-closeup.png).

최신 조명 시안 v2는 천장의 작은 틈에서 내려오는 청백색 빛이 봉인석의 깨진 상단을 지나 유물을 비추도록 수정했다. 유물의 밝은 청색 중심과 작은 후광, 받침대·주변 이끼의 반사광, 빛줄기 속 먼지를 강조하고 주변 동굴은 어둡게 정리했다. v1 배치 화면을 내장 imagegen으로 편집한 **전체 장면 콘셉트 이미지이며 실제 게임 조명이나 투명 구조물 PNG에는 아직 반영하지 않았다**. [조명 시안 v2](../assets/concepts/relic-acquisition-shrine-lighting-v2.png) · [정확한 편집 프롬프트](../assets/concepts/relic-acquisition-shrine-lighting-v2.prompt.txt) · [출처·상태 메타데이터](../assets/concepts/relic-acquisition-shrine-lighting-v2.json).

v1 SDL 배치 미리보기 재생성: `.\.venv\Scripts\python.exe tools/preview_relic_shrine.py`. 기존 공통 맵 렌더러와 실제 유물·캐릭터를 사용하며 실행 게임의 배치·충돌·획득 로직은 수정하지 않는다. 이 명령은 imagegen 조명 시안 v2를 재생성하지 않는다.

## 녹색 거리 추가 조사 자료

녹색 거리39장·비교 지역6장, 총45장의 [이미지 갤러리](references/hollow-knight-greenpath/index.html)와 [이미지별 분석 목록](references/hollow-knight-greenpath/README.md)을 추가했다. [맵·텍스처·몬스터 종합 분석](hollow-knight-greenpath-study.md), [전경 그림자·배경층·조명 상세 분석](hollow-knight-layer-lighting-study.md), 대표8장의 영역 주석과 확대 자료를 함께 제공한다. 모든 이미지에 출처·저장 해상도·해시를 기록했다. 자료집의 적용안과 조명 수치는 후속 제작 제안이며 현재 승인된 미술·충돌·카메라 규칙을 변경하지 않는다.
