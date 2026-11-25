# 이끼 동굴 구간의 미술 방향

새 맵과 기존 구역의 미술 수정은 [맵 장식 23종과 레이어 제작·렌더링 기준](reference-production-guide.md#맵-미술-제작과-렌더링-기준)을 따른다.

## 전투방 하강 입구

열린 덮개 아래에 보이던 사각형과 가로 이음을 없애기 위해, 불규칙한 돌출 암벽과 뿌리, 먼 청록 배경을 한 장으로 연결한 [하강 이미지 v2](../assets/terrain/moss-combat-descent-shaft-v2.png)를 사용한다. [HK-GP18](references/hollow-knight-silksong/index.html#HK-GP18)의 이끼 가장자리와 검은 암반, [HK-GP22](references/hollow-knight-silksong/index.html#HK-GP22)의 비대칭 돌출부와 뒤쪽 깊이를 참고해 내장 image_gen으로 만들었다. [생성 프롬프트](../assets/terrain/moss-combat-descent-shaft-v2.prompt.txt).

입구 위와 양옆, 더 깊은 하단은 점차 어두워지고, 덮개가 움직일 때만 열린 폭에 맞춰 자른다. 바닥 장식은 양쪽과 덮개에 나눠 그려 열린 구멍 위로 잔디 띠가 남지 않게 했다. 기존 덮개 두께, 개방 시간, 실제 충돌과 A파트 전환을 따른다. [수정 후 실제 화면](combat-shaft-v7-open.png).

마지막 골렘을 처치하면 0.5초 동안 돌벽과 바닥 덮개가 멈춘다. 위쪽 발판에 있어도 틈이 보이도록 카메라를 낮춘 다음, 닫힌 덮개 왼쪽에서 0.6초 동안 청록빛이 서서히 밝아진다. 개방이 시작되면 빛은 움직이는 덮개 끝을 따라가며 사라진다. 하강로의 암벽은 덮개가 열린 뒤 접근할 때 드러난다.

## 첫 맵 하강 착지 이후부터 첫 보스 B1까지의 오브젝트 시안

2026-11-23 사용자 지정 범위는 **첫 맵 전투방 이후 하강 착지 → 하단 연습길 → 왼쪽 첫 보스 B1 입구**다. 이 구간용으로 착지 지점 폐기둥 잔해, 벽점프 연습 돌기둥, 짧은 돌다리 발판, 가시 덩굴, 보스 전실 길잡이 석등, B1 입구 폐아치의 투명 PNG 6종을 생성했다. [이미지·프롬프트 목록](../assets/structures/map1-lower-route/README.md)과 [자산 명세](../assets/structures/map1-lower-route/manifest.json)에 배치 후보·참고 ID·해시를 기록했다.

기존 이끼 동굴·유물 제단을 형태와 재질 기준으로 삼고 HK-GP18·HK-CT-05·SS-MG-02·SS-MG-03·SS-MF-04의 식생 외곽, 안전 착지면, 기둥 경계와 작은 조명을 참고했다. 개별 PNG의 원본 알파를 보존했으며 가장자리의 약한 반투명 표현도 남아 있다. 이미지 시안이며 게임 배치·충돌·회복/저장 기능은 미적용이다. 석등은 왼쪽 B1 방향을 안내하는 장식이다.

시작 동굴과 처음 추락해 깨어나는 착지방은 기존 모습으로 유지한다. 옆 이끼 통로로 넘어간 뒤부터 새 표현을 적용한다. 사용자가 제공한 녹색 거리 참고 이미지의 명암·깊이·지형 가장자리 표현을 바탕으로 이끼 통로, 전투방, 전투방 아래 하강 통로의 표현을 통일한다.

- 지형의 속은 검은 덩어리로 가리고, 통행 가능한 표면과 벽의 얇은 가장자리만 읽히게 한다. 바닥 아래 전체를 밝게 보여주지 않는다.
- 거대한 밝은 각진 바위 면 대신 작은 둥근 돌, 잎, 이끼가 모인 테두리를 쓴다. 공중 발판의 아래는 불규칙한 돌·뿌리 실루엣으로 연결한다.
- 멀리 물러난 청록·남색 숲 동굴 배경은 지형보다 느리게 움직인다. 가까운 천장에는 검은 뿌리와 덩굴을 두고, 작은 포자가 떠다니도록 한다.
- 발딛는 돌 표면선을 기존 충돌 상면에 맞춘다. 방 배치, 발판 높이, 출입구, 중앙 등장, 전멸 개방과 덮개112/접근 조명 동작은 유지한다.

기존 벽 이미지는 폭360·주기 높이1536으로 확대해 풀과 자갈을 읽을 수 있게 한다. 발판 이미지는 그대로 유지한다. 각진 모서리는 투명 덩굴을 겹쳐 가리되 문틀 끝에는 별도 덩굴을 붙이지 않는다. 바닥과 천장은 자갈·이끼의 작은 높낮이가 보이도록 하고 반드시 직선으로 만들지 않는다. 실제 이동 경계는 유지한다. [덩굴로 가린 모서리](green-corner-foliage-entry.png) · [기존 착지방 유지](landing-original-preserved.png).

## 적용 범위와 확인 화면

- [이끼 통로](green-style-gallery.png) · [이동과 배경 시차 GIF](green-style-gallery-parallax.gif)
- [전투방 수정탄 발사 장면](combat-readability-projectiles.png) · [조정 전후 비교](combat-readability-comparison.jpg) · [높은 발판 시점](combat-readability-high.png)
- [기존 시작 동굴 유지](green-style-opening.png) · [기존 문양 유지](green-style-sigil.png)

공통 렌더링은 `moss_art.py`의 `MossCaveArt`가 담당하고 `lower_caves.py`에서 사용한다. `opening_cave.py`는 변경 전 상태로 복원했다. 배경 시차는 지형 이동의0.16배다. 천장 덩굴은 지형과 같은 월드 좌표에 고정한다. 잎과 뿌리는 장식이며 실제 충돌 상면은 바꾸지 않는다.

천장 덩굴을 화면 상단에 붙이거나 천장의 화면 진입 여부에 따라 배치 기준을 바꾸지 않는다. 이끼 통로는 기존 포자 영역 상단과 같은 `GALLERY_CEILING_Y=900`, 전투방은 실제 천장 `COMBAT_CEILING_Y`에 배치한다. 천장 위는 검게 채우고, 기존 불규칙한 아래 윤곽은 유지한다. 카메라는 두 구간 모두 캐릭터의 가로·세로 위치를 따라가며 천장을 보이게 하려는 높이 제한을 사용하지 않는다. 지상에서는 발밑 여백을 확보하고, 하강 통로는 기존 추적을 유지한다. [통로 지상](ceiling-vines-gallery-floor.png) · [통로 발판](ceiling-vines-gallery-platform.png) · [전투방 지상](ceiling-vines-combat-floor.png) · [전투방 상승](ceiling-vines-combat-high.png) · [높이별 비교 GIF](ceiling-vines-follow.gif).

## 전투방 전용 원경과 식생

원경 한 장에 뿌리가 파고든 부서진 석조 고리, 층층이 멀어지는 안개, 왼쪽 천장 틈에서 들어오는 빛을 담았다. 중앙 공중은 남청색 면을 넓게 남겨 골렘과 수정탄이 드러난다. 지면 양끝에는 크기와 방향을 달리한 호박빛 열매 식생을 배치해 청록 원경에 따뜻한 색을 더했다. [HK-GP05](references/hollow-knight-silksong/index.html#HK-GP05) · [SS-MG-04](references/hollow-knight-silksong/index.html#SS-MG-04) · [SS-HH-06](references/hollow-knight-silksong/index.html#SS-HH-06)

두 원화는 내장 imagegen으로 생성했고 원본을 게임에 사용한다. 원경은 지형보다 느리게 이동하고 식생은 바닥에 고정된다. `.\.venv\Scripts\python.exe tools/preview_combat_atmosphere.py --projectiles --prefix relic-grotto --output-dir .cache/relic-grotto`로 공벌레 단계, 수정탄, 상승, 덮개 틈새와 하강 장면을 렌더링할 수 있다.

### 앞서 조정한 전투방의 명암

이전 미술은 오른쪽 상단 사선 빛과 대비를 낮춘 중경 폐아치를 사용했다. 포자를 18개에서 8개로 줄이고 천장 뿌리를 벽 쪽으로 당겼다. 두 골렘의 실제 발사 코드로 수정탄을 만들어 같은 카메라와 비행 시점에서 비교했다. [당시 전후 비교](combat-readability-comparison.jpg) · [당시 수정탄 화면](combat-readability-projectiles.png)

### 이전 전투방 미술 기록

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
| 전투방 석조 고리 원경 | [원경](../assets/terrain/moss-combat-relic-grotto-v1.png) | [프롬프트](../assets/terrain/moss-combat-relic-grotto-v1.prompt.txt) |
| 전투방 호박빛 열매 | [식생](../assets/terrain/moss-combat-seedpods-v1.png) | [프롬프트](../assets/terrain/moss-combat-seedpods-v1.prompt.txt) |
| 이전 전투방 중경 폐아치 | [중경](../assets/terrain/green-combat-midground-ruins-v1.png) | [프롬프트](../assets/terrain/green-combat-midground-ruins-v1.prompt.txt) |
| 전투방 근접 뿌리와 큰 잎 | [전경](../assets/terrain/green-combat-foreground-roots-v1.png) | [프롬프트](../assets/terrain/green-combat-foreground-roots-v1.prompt.txt) |

이전 중경 폐아치와 근접 뿌리는 투명 원본 PNG이며, 용도·크기·고정점은 각 PNG와 같은 이름의 JSON에 기록했다. 덮개 틈새 빛은 SDL의 색·알파 메시로 그린다.

사용자 참고 이미지7장은 [참고 폴더](references/green-cavern-style/)에 보관했다.

## 유물 획득 구조물 디자인 시안

첫 유물 지점에 놓을 구조물 v1은 이끼와 덩굴에 잠식된 **깨진 육각 봉인석과 낮은 받침대**다. 기존 순간이동 문양의 육각 외곽과 짝을 이룬 홈을 돌에 새겼다. 윗부분을 비대칭으로 부수고, 유물이 놓이는 중앙은 식생 없이 비워 시선을 모은다. 맵의 어두운 청록색 돌·둥근 잎·정돈된 손그림 윤곽을 따른다.

현재는 **실제 게임의 유물 뒤 배경 오브젝트로 적용했다**. 장식이며 이동을 막는 충돌은 없다. 높이380월드, 바닥에 묻히는 기준점과 기존 유물 높이100을 메타데이터에 기록했다. 구조물 PNG에는 유물을 넣지 않아 기존 유물 획득 동작과 분리된다.

[투명 구조물 PNG](../assets/concepts/relic-acquisition-shrine-v1.png) · [원본](../assets/concepts/relic-acquisition-shrine-v1-source.png) · [정확한 내장 imagegen 프롬프트](../assets/concepts/relic-acquisition-shrine-v1.prompt.txt) · [배치 메타데이터](../assets/concepts/relic-acquisition-shrine-v1.json) · [기본 배율 배치 시안](relic-acquisition-shrine-v1-gallery.png) · [확대 배치 시안](relic-acquisition-shrine-v1-closeup.png).

최신 조명 시안 v2는 천장의 작은 틈에서 내려오는 청백색 빛이 봉인석의 깨진 상단을 지나 유물을 비추도록 수정했다. 유물의 밝은 청색 중심과 작은 후광, 받침대·주변 이끼의 반사광, 빛줄기 속 먼지를 강조하고 주변 동굴은 어둡게 정리했다. v1 배치 화면을 내장 imagegen으로 편집한 **전체 장면 콘셉트 이미지**다. 게임은 `relic_shrine.py`의 SDL 조명으로 청백색 사선 빛줄기·작은 유물 후광·바닥 반사광·22개 먼지 입자를 실시간 표현한다. 월드 좌표에 고정되며 획득 후 후광은 사라지고 천장 빛은 55%로 약해진다. 기존 구조물 PNG를 그대로 사용한다. [조명 시안 v2](../assets/concepts/relic-acquisition-shrine-lighting-v2.png) · [정확한 편집 프롬프트](../assets/concepts/relic-acquisition-shrine-lighting-v2.prompt.txt) · [출처·상태 메타데이터](../assets/concepts/relic-acquisition-shrine-lighting-v2.json).

실제 게임 SDL 배치 미리보기 재생성: `.\.venv\Scripts\python.exe tools/preview_relic_shrine.py`. 실제 LowerCaves 렌더러·유물·캐릭터를 사용해 `docs/relic-shrine-runtime-{gallery,closeup,collected}.png`를 저장한다. 이 명령은 imagegen 조명 시안 v2를 재생성하지 않는다.

## 녹색 거리 추가 조사 자료

녹색 거리39장·비교 지역6장, 총45장의 [이미지 갤러리](references/hollow-knight-greenpath/index.html)와 [이미지별 분석 목록](references/hollow-knight-greenpath/README.md)을 추가했다. [맵·텍스처·몬스터 종합 분석](hollow-knight-greenpath-study.md), [전경 그림자·배경층·조명 상세 분석](hollow-knight-layer-lighting-study.md), 대표8장의 영역 주석과 확대 자료를 함께 제공한다. 모든 이미지에 출처·저장 해상도·해시를 기록했다. 자료집의 적용안과 조명 수치는 후속 제작 제안이며 현재 승인된 미술·충돌·카메라 규칙을 변경하지 않는다.

## 두 게임 통합 제작 데이터

기존45장에 신규199장을 더한 [통합 검색 갤러리244장](references/hollow-knight-silksong/index.html)은 할로우 나이트128장·실크송116장, 게임별36개 지역을 다룬다. 이미지마다 공간 구성·재질·앞뒤 깊이·조명·적용 구역·제작 패턴·자산 명세·출처를 연결했다. 전경 그림자처럼 보이는 큰 실루엣, 검은 지형 내부, 중경, 원경, 대기광을 구별해서 기록한다.

[프로젝트 제작 가이드](reference-production-guide.md)에 전투방·유물 지점·하강·맵2 중앙 홀·장치 구역·최종 보스방의 추천 자료와 다음 제작 순서를 정리했다. 제작 패턴20개·자산 명세20개, 대표12장의49개 영역 주석을 제공하며 [JSON](references/hollow-knight-silksong/analysis.json)·[CSV](references/hollow-knight-silksong/catalog.csv)·검색 CLI로 재사용할 수 있다. [현재 두 맵과의 대응](references/hollow-knight-silksong/project-targets.json)에서 기존 ‘문양의 성소’ 분류는 맵2 최종 보스방의 문양·제단에 대응한다. 독립된 세 번째 맵을 추가하는 자료가 아니다.

원작 이미지는 참고 자료로 보관하고 우리 게임의 외형은 승인된 자산과 고유 문양으로 제작한다. 시각적 영역 주석은 실제 충돌·엔진 레이어의 정답이 아니며, 이번 통합 조사는 게임 코드·맵 배치·현재 조명 동작을 변경하지 않았다.
