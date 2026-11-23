# 할로우 나이트와 실크송 프로젝트 참고 데이터

2026년11월23일 기준 **총244장**. 기존45장에 신규199장을 더했다. 할로우 나이트128장과 실크송116장, 게임별 지역을 구분해 총36개 지역을 다룬다. 사진의 개수는 서로 다른 방의 개수가 아니다.

- [오프라인 검색 갤러리](index.html): 게임·지역·맵 용도·재질·조명·프로젝트 적용 구역으로 검색하고 두 장 비교.
- [프로젝트 제작 가이드](../../reference-production-guide.md): 지금 무엇을 만들고 어디에 쓸지 결정하는 순서.
- [분석 JSON](analysis.json) · [한 줄 한 이미지 JSONL](analysis.jsonl) · [CSV](catalog.csv) · [출처 원장](sources.json)
- [제작 패턴20개](patterns.json) · [자산 제작 명세20개](asset-briefs.json) · [통계](statistics.json)
- [최신 두 맵의 위치·구현 상태 대응](project-targets.json): 중앙 통로는 맵2 작은 중앙 홀, 문양의 성소는 맵2 최종 보스방의 문양·제단에 대응.
- [기존 녹색 거리 자료집](../hollow-knight-greenpath/README.md)

신규199장은 실제 PNG로 저장했고 기존45장은 원래 파일을 참조해 중복 복사를 피했다. 파일 및 디코딩된 RGB 픽셀 해시로 완전 중복을 제외했다. 비슷한 구도는 dHash 거리4 이하 후보를 따로 표시한다. 이 표시는 유사도 후보이며 같은 방·같은 원본이라고 확정하는 판정은 아니다.

개별 관찰은 시각적으로 확인한 화면 내용이고, P01~P20은 RelicEscape 적용 제안이다. 시작 동굴·최초 착지방 보존, 승인된 벽·발판, 현재 전투방 배치·충돌·카메라·덮개112·접근 조명은 유지 기준이다. 게임에 적용한 항목과 미구현 제안은 각 패턴의 현재 상태에서 구별한다.

## 데이터 활용 순서

1. 필요한 프로젝트 구역을 고른다. 예: 고대 장치 구역.
2. 용도와 제작 패턴을 고른다. 예: P06 장치 경로, P05 수직 이동.
3. 이미지의 관찰과 전경/배경·조명을 확인하고 두 장을 비교한다.
4. 연결된 B01~B20 제작 명세에서 기존 자산 재사용 여부와 충돌·시야 제약을 확인한다.
5. 프로젝트 고유 자산을 제작하고 실제 이동·전투 화면에서 검증한다.

CLI 예: `.\.venv\Scripts\python.exe docs/references/hollow-knight-silksong/query_references.py --target "고대 장치 구역" --pattern P06 --limit 8`

원작 이미지와 문양은 연구용으로 보관한다. 게임에 직접 쓰는 제작 자산은 `assets/`에서 별도로 만든다. 이미지 권리는 Team Cherry 및 해당 권리자에게 있으며, Wiki의 이미지별 출처 페이지를 기록했다. 다운로드된 800px 이미지와 링크만 보관한 원본 URL을 구별한다.

## 지역별 자료

| 게임 | 지역 | 이미지 수 |
| --- | --- | ---: |
| HK | Greenpath | 39 |
| HK | Queen's Gardens | 6 |
| HK | Fog Canyon | 6 |
| HK | Fungal Wastes | 6 |
| HK | City of Tears | 6 |
| HK | Crystal Peak | 6 |
| HK | Forgotten Crossroads | 6 |
| HK | Deepnest | 6 |
| HK | Royal Waterways | 6 |
| HK | Ancient Basin | 5 |
| HK | The Abyss | 6 |
| HK | Kingdom's Edge | 6 |
| HK | The Hive | 6 |
| HK | Resting Grounds | 6 |
| HK | Howling Cliffs | 6 |
| HK | White Palace | 6 |
| SS | Moss Grotto | 6 |
| SS | Bone Bottom | 3 |
| SS | Deep Docks | 6 |
| SS | Far Fields | 6 |
| SS | Hunter's March | 6 |
| SS | Shellwood | 6 |
| SS | Greymoor | 6 |
| SS | Bellhart | 6 |
| SS | Bilewater | 6 |
| SS | Sinner's Road | 6 |
| SS | Mount Fay | 6 |
| SS | Sands of Karak | 6 |
| SS | Wormways | 6 |
| SS | Underworks | 6 |
| SS | Choral Chambers | 6 |
| SS | Whispering Vaults | 6 |
| SS | Whiteward | 5 |
| SS | High Halls | 6 |
| SS | Cogwork Core | 6 |
| SS | Memorium | 6 |

## 제작 패턴

| ID | 패턴 | 우선순위 | 적용 구역 |
| --- | --- | --- | --- |
| P01 | 검은 지형 속과 읽히는 테두리 | P0 | 이끼 통로, 전투방, 하강 통로 |
| P02 | 근접 전경과 중앙 시야 여백 | P0 | 전투방, 이끼 통로, 문양의 성소 |
| P03 | 중경과 원경의 다른 대비 | P0 | 전투방, 중앙 통로, 고대 장치 구역 |
| P04 | 목표에 모이는 빛 | P0 | 유물 획득 지점, 문양의 성소, 전투방 |
| P05 | 다음 착지면이 보이는 수직 이동 | P1 | 하강 통로, 중앙 통로, 고대 장치 구역 |
| P06 | 장치 경로와 작동부의 명료함 | P1 | 고대 장치 구역, 중앙 통로 |
| P07 | 안전면과 위험면의 다른 형태 | P1 | 고대 장치 구역, 보스 접근 구간, 하강 통로 |
| P08 | 보상의 선노출과 우회 경로 | P1 | 이끼 통로, 고대 장치 구역, 보상 포켓 |
| P09 | 지역 문턱과 문양 입구 | P1 | 중앙 통로, 고대 장치 구역, 문양의 성소 |
| P10 | 작고 명료한 휴식 포켓 | P2 | 전투 후 휴식 지점, 보상 포켓, 중앙 통로 |
| P11 | 전투방의 넓은 판독 공간 | P0 | 전투방, 보스방 |
| P12 | 재질의 군집과 빈 구간 | P1 | 이끼 통로, 전투방, 고대 장치 구역 |
| P13 | 대기광과 입자의 깊이 | P1 | 전투방, 문양의 성소, 하강 통로 |
| P14 | 기능색과 장식색의 분리 | P0 | 유물 획득 지점, 전투방, 고대 장치 구역 |
| P15 | 적 실루엣과 공격 방향 | P0 | 전투방, 보스방, 이끼 통로 |
| P16 | 방마다 하나의 큰 기억점 | P1 | 중앙 통로, 문양의 성소, 보스방, 전투방 |
| P17 | 비대칭 공간의 무게 배분 | P1 | 전투방, 중앙 통로, 보상 포켓 |
| P18 | 밝은 지역에서의 대비 반전 | P2 | 문양의 성소, 고대 장치 구역 |
| P19 | 공간 골격을 유지한 상태 변화 | P2 | 고대 장치 구역, 문양의 성소, 보스 처치 후 |
| P20 | 시야 제한과 집중 연출 | P2 | 유물 획득 연출, 보스 등장 연출 |

## 이미지별 관찰 목록

### HK-GP01 폭포 아래 벤치와 등불

[이미지 보기](../hollow-knight-greenpath/images/gp01.png) · HK / Greenpath · 휴식 포켓 · 석재, 이끼, 잎, 액체

- 관찰: 낮은 바닥과 비어 있는 중앙 위로 폭포가 높게 열린다. 큰 둥근 돌 사이에 작은 잎 덩어리를 밀집시킨다.
- 전경과 배경: 천장 덩굴은 어둡고 가까우며 폭포와 기둥은 흐리고 멀다.
- 조명: 흰 등불의 작은 광원과 넓은 청록색 수직 빛이 겹친다.
- 제작 패턴: P03, P04, P10 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 이끼 통로 · 자산 명세 B03, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9c/Screenshot_HK_Greenpath_01.png/800px-Screenshot_HK_Greenpath_01.png)

### HK-GP02 웅덩이 위 철문과 수직 샛길

[이미지 보기](../hollow-knight-greenpath/images/gp02.png) · HK / Greenpath · 위험 구간 · 석재, 이끼, 금속, 액체

- 관찰: 왼쪽 낮은 문과 오른쪽 높은 발판이 수평·수직 경로를 함께 제시한다. 철문의 얇은 선과 두꺼운 이끼 지형이 대비된다.
- 전경과 배경: 화면 위 검은 덩어리는 지형 내부이고 뒤의 낙수는 원경이다.
- 조명: 산성 액체의 밝은 수평면이 낙하 위험을 분명하게 만든다.
- 제작 패턴: P03, P05, P07 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 이끼 통로, 하강 통로 · 자산 명세 B03, B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/dd/Screenshot_HK_Greenpath_02.png/800px-Screenshot_HK_Greenpath_02.png)

### HK-GP03 산성 호수 위 유적 회랑

[이미지 보기](../hollow-knight-greenpath/images/gp03.png) · HK / Greenpath · 수평 통로 · 석재, 잎, 금속, 액체

- 관찰: 아치 두 층과 긴 수평 보행면이 반복된다. 매끈한 곡선 석재 위에 잎이 부분적으로 침식한다.
- 전경과 배경: 뒤 회랑의 기둥은 낮은 대비로 반복되고 앞 가장자리가 선명하다.
- 조명: 차가운 등불과 밝은 녹색 액체가 서로 다른 높이에 놓인다.
- 제작 패턴: P04, P12, P16 — 목표에 모이는 빛 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B04, B05, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/22/Screenshot_HK_Greenpath_03.png/800px-Screenshot_HK_Greenpath_03.png)

### HK-GP04 가시로 둘러싸인 좁은 통로

[이미지 보기](../hollow-knight-greenpath/images/gp04.png) · HK / Greenpath · 위험 구간 · 이끼, 잎, 가시

- 관찰: 위·아래 가시 사이에 열린 이동 통로가 있다. 주황·분홍 끝이 있는 뾰족한 가시가 둥근 이끼와 확실히 구별된다.
- 전경과 배경: 바깥 검은 덩어리와 안쪽 가시 테두리가 통로를 액자처럼 감싼다.
- 조명: 중앙 배경은 청록색으로 밝고 위험한 가시는 따뜻한 가장자리를 갖는다.
- 제작 패턴: P05, P07, P12 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 보스 접근 구간 · 자산 명세 B06, B09, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d0/Screenshot_HK_Greenpath_04.png/800px-Screenshot_HK_Greenpath_04.png)

### HK-GP05 이끼 기사의 평평한 전투 공간

[이미지 보기](../hollow-knight-greenpath/images/gp05.png) · HK / Greenpath · 전투 공간 · 석재, 이끼, 잎

- 관찰: 중앙 보행면을 길게 비우고 가장자리의 장식만 높인다. 돌기둥과 잎 덩어리는 촘촘하지만 전투 공간은 단순하다.
- 전경과 배경: 위 덩굴은 검은 프레임이며 뒤 기둥은 흐리다.
- 조명: 두 줄기 이상의 세로 빛이 전투 공간 뒤를 나눈다.
- 제작 패턴: P04, P11, P15 — 목표에 모이는 빛 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B04, B05, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5d/Screenshot_HK_Greenpath_05.png/800px-Screenshot_HK_Greenpath_05.png)

### HK-GP06 유적 기둥과 매달린 검은 발판

[이미지 보기](../hollow-knight-greenpath/images/gp06.png) · HK / Greenpath · 복층 공간 · 석재, 이끼, 잎

- 관찰: 중앙 위쪽의 검은 발판 아래로 큰 기둥들이 이어진다. 밝은 석재는 윤곽과 홈을 읽히게 하고 발판 속은 검게 묻힌다.
- 전경과 배경: 발판 검정은 충돌 지형의 내부이며 원경의 아치와 다르다.
- 조명: 기둥 뒤의 수직 광막과 앞쪽 작은 등불이 깊이를 만든다.
- 제작 패턴: P01, P02, P03, P16 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 방마다 하나의 큰 기억점
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B01, B02, B03, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/df/Screenshot_HK_Greenpath_06.png/800px-Screenshot_HK_Greenpath_06.png)

### HK-GP07 호넷 공간의 문양 비석

[이미지 보기](../hollow-knight-greenpath/images/gp07.png) · HK / Greenpath · 전투 공간 · 석재, 이끼, 뿌리

- 관찰: 평평한 바닥 위 큰 문양 돌 하나가 시각적 중심이 된다. 굵은 소용돌이 문양과 덩굴이 돌의 큰 형태를 보조한다.
- 전경과 배경: 뒤의 식물과 수직 줄기는 비석보다 흐리고 덜 선명하다.
- 조명: 비스듬한 밝은 기둥이 비석과 빈 전투 공간을 비춘다.
- 제작 패턴: P04, P11, P16 — 목표에 모이는 빛 / 전투방의 넓은 판독 공간 / 방마다 하나의 큰 기억점
- 적용 후보: 보스방, 문양의 성소 · 자산 명세 B04, B05, B13, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_07.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/81/Screenshot_HK_Greenpath_07.png/800px-Screenshot_HK_Greenpath_07.png)

### HK-GP08 대각선 가시와 낮은 유적 통로

[이미지 보기](../hollow-knight-greenpath/images/gp08.png) · HK / Greenpath · 위험 구간 · 석재, 이끼, 가시

- 관찰: 위에서 오른쪽 아래로 내려오는 가시가 이동 여유를 압축한다. 유적 아치의 매끈한 곡선과 가시의 뾰족한 선이 대비된다.
- 전경과 배경: 상부 검은 지형 밑으로 뿌리가 매달리고 뒤 회랑이 비친다.
- 조명: 배경은 푸르게 눌러 가시 끝과 이동면이 먼저 읽힌다.
- 제작 패턴: P05, P07, P16 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 방마다 하나의 큰 기억점
- 적용 후보: 이끼 통로, 보스 접근 구간 · 자산 명세 B06, B09, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_08.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6a/Screenshot_HK_Greenpath_08.png/800px-Screenshot_HK_Greenpath_08.png)

### HK-GP09 역 입구와 벤치

[이미지 보기](../hollow-knight-greenpath/images/gp09.png) · HK / Greenpath · 휴식 포켓 · 석재, 금속, 잎

- 관찰: 왼쪽 큰 원형 문과 오른쪽 벤치가 방향과 기능을 나눈다. 부챗살 장식·문틀·얇은 기둥은 식생보다 규칙적이다.
- 전경과 배경: 아래 전경 난간과 뒤 기둥 사이에 보행면이 놓인다.
- 조명: 문과 벤치 근처의 작은 등불이 기능 지점을 표시한다.
- 제작 패턴: P10, P16 — 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 중앙 통로 · 자산 명세 B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_09.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/98/Screenshot_HK_Greenpath_09.png/800px-Screenshot_HK_Greenpath_09.png)

### HK-GP10 낮은 천장 아래 고립된 벤치

[이미지 보기](../hollow-knight-greenpath/images/gp10.png) · HK / Greenpath · 휴식 포켓 · 석재, 이끼, 뿌리

- 관찰: 대부분을 가린 검은 천장 아래 작은 밝은 공간이 열린다. 천장의 돌 표면보다 아래로 뻗은 가는 뿌리 실루엣이 강하다.
- 전경과 배경: 검은 상부 코어와 가까운 뿌리, 푸른 배경을 구별한다.
- 조명: 벤치 주변만 낮은 대비의 푸른 빛으로 드러낸다.
- 제작 패턴: P01, P02, P03, P10 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 이끼 통로 · 자산 명세 B01, B02, B03, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_10.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c9/Screenshot_HK_Greenpath_10.png/800px-Screenshot_HK_Greenpath_10.png)

### HK-GP11 안개 협곡으로 바뀌는 경계

[이미지 보기](../hollow-knight-greenpath/images/gp11.png) · HK / Greenpath · 지역 경계 · 이끼, 잎, 구형 생물

- 관찰: 왼쪽 넓은 땅이 오른쪽 수직 낙하 틈으로 끝난다. 오른쪽 구형 식물이 잎 위주의 왼쪽과 다른 재질을 알린다.
- 전경과 배경: 검은 바닥 내부와 뒤의 식물층이 명확히 분리된다.
- 조명: 푸른 공간에 흰 둥근 발광체가 점진적으로 늘어난다.
- 제작 패턴: P03, P05, P09 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 이끼 통로, 하강 통로 · 자산 명세 B03, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Greenpath_11.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/df/Screenshot_HK_Greenpath_11.png/800px-Screenshot_HK_Greenpath_11.png)

### HK-GP12 사냥꾼의 식생 위장 은신처

[이미지 보기](../hollow-knight-greenpath/images/gp12.png) · HK / Greenpath · 랜드마크 · 잎, 생물 외곽

- 관찰: 낮은 잎 무더기에 큰 입과 눈이 묻혀 있다. 겹친 작은 잎과 큰 흰 이빨의 스케일 차이가 인상을 만든다.
- 전경과 배경: 멀리 가는 큰 줄기와 가까운 둥근 잎 덩어리가 겹친다.
- 조명: 위에서 내려오는 사선 광선은 눈과 잎 표면을 읽히게 한다.
- 제작 패턴: P04, P15, P16 — 목표에 모이는 빛 / 적 실루엣과 공격 방향 / 방마다 하나의 큰 기억점
- 적용 후보: 이끼 통로 · 자산 명세 B04, B05, B16, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_The_Hunter_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8f/Screenshot_HK_The_Hunter_01.png/800px-Screenshot_HK_The_Hunter_01.png)

### HK-GP13 쉐오의 집과 가시 경계

[이미지 보기](../hollow-knight-greenpath/images/gp13.png) · HK / Greenpath · 목표 노출 · 판형 외피, 뿌리, 가시

- 관찰: 중앙 둥근 집과 양옆 가시가 안전한 목적지를 감싼다. 집의 큰 판형 곡면 위로 덩굴이 감기고 외곽에는 날카로운 가시가 있다.
- 전경과 배경: 어두운 전경 아래로 집 입구가 밝게 열린다.
- 조명: 하얀 출입구 빛과 차가운 외부 청록빛이 대비된다.
- 제작 패턴: P07, P16 — 안전면과 위험면의 다른 형태 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B09, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Nailmaster_Sheo_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/da/Screenshot_HK_Nailmaster_Sheo_01.png/800px-Screenshot_HK_Nailmaster_Sheo_01.png)

### HK-GP14 산성 호수 위 넓은 다리

[이미지 보기](../hollow-knight-greenpath/images/gp14.png) · HK / Greenpath · 수평 통로 · 석재, 금속, 잎, 액체

- 관찰: 긴 평평한 다리가 웅덩이와 넓은 배경을 가른다. 난간·아치의 가는 선과 잎의 작은 덩어리가 공존한다.
- 전경과 배경: 다리 아래 검은 코어와 뒤의 큰 줄기는 서로 다른 깊이다.
- 조명: 등불은 국소광이고 산성 수면은 넓은 가로 발광면이다.
- 제작 패턴: P04, P05, P07 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B04, B05, B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Greenpath_South_Area.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/7f/Greenpath_South_Area.png/800px-Greenpath_South_Area.png)

### HK-GP15 우운 사당 안의 어두운 휴식 공간

[이미지 보기](../hollow-knight-greenpath/images/gp15.png) · HK / Greenpath · 휴식 포켓 · 유기적 조각, 뿌리

- 관찰: 거의 검은 입구 테두리 안에 벤치가 작게 놓인다. 안쪽 큰 조각과 긴 곡선 구조는 돌보다 나무 같은 유기 형태를 보인다.
- 전경과 배경: 입구를 두르는 검은 프레임과 뒤 벽의 푸른 층이 구분된다.
- 조명: 천장 틈의 좁은 빛이 벤치로 내려오고 주변은 깊게 어둡다.
- 제작 패턴: P01, P02, P04, P10 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 유물 획득 지점 · 자산 명세 B01, B02, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Lake_of_Unn_Shrine_Interior.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/72/Lake_of_Unn_Shrine_Interior.png/800px-Lake_of_Unn_Shrine_Interior.png)

### HK-GP16 이층 유적의 벤치 포켓

[이미지 보기](../hollow-knight-greenpath/images/gp16.png) · HK / Greenpath · 휴식 포켓 · 석재, 금속, 잎

- 관찰: 위·아래 통로 사이 오른쪽에 벤치가 놓인 작은 공간이 있다. 정교한 다리 하단 장식과 거친 잎 테두리가 겹친다.
- 전경과 배경: 전경 아래 실루엣과 여러 층의 유적 기둥이 깊이를 만든다.
- 조명: 벤치 뒤의 푸른 빛이 복잡한 건축에서 쉬는 지점을 분리한다.
- 제작 패턴: P05, P10, P16 — 다음 착지면이 보이는 수직 이동 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 중앙 통로 · 자산 명세 B06, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Greenpath_Central_Bench%282%29.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/88/Greenpath_Central_Bench%282%29.png/800px-Greenpath_Central_Bench%282%29.png)

### HK-GP17 오블 구역의 수직 발판

[이미지 보기](../hollow-knight-greenpath/images/gp17.png) · HK / Greenpath · 수직 이동 · 이끼, 석재, 뿌리

- 관찰: 작은 발판이 좌우 다른 높이로 흩어지고 긴 기둥이 시선을 세로로 끈다. 발판 가장자리의 이끼 띠와 아래 뿌리는 크기가 짧고 불규칙하다.
- 전경과 배경: 큰 뒤 줄기는 흐리고 전면의 발판·벽 가장자리는 선명하다.
- 조명: 점 형태 포자와 부드러운 청록 광막이 빈 공중을 채운다.
- 제작 패턴: P03, P05 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 하강 통로, 이끼 통로 · 자산 명세 B03, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Greenpath_Obble_Area%282%29.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/30/Greenpath_Obble_Area%282%29.png/800px-Greenpath_Obble_Area%282%29.png)

### HK-GP18 여왕의 정원으로 통하는 경계

[이미지 보기](../hollow-knight-greenpath/images/gp18.png) · HK / Greenpath · 지역 경계 · 석재, 이끼, 잎

- 관찰: 좌우 높은 벽 아래 중앙 문양석이 목적지를 표시한다. 둥근 잎 테두리와 규칙적 돌 문양이 섞인다.
- 전경과 배경: 중앙 위의 검은 코어와 먼 배경의 아치를 구분한다.
- 조명: 양옆 푸른 광막이 중앙 어두운 문양석을 감싼다.
- 제작 패턴: P01, P02, P05, P09 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B01, B02, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Greenpath_Queen%27s_Gardens_Connection.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/97/Greenpath_Queen%27s_Gardens_Connection.png/800px-Greenpath_Queen%27s_Gardens_Connection.png)

### HK-GP19 초기 개발판의 낮은 물가

[이미지 보기](../hollow-knight-greenpath/images/gp19.jpg) · HK / Greenpath · 수평 통로 · 이끼, 입자 표면, 액체

- 관찰: 낮은 보행 띠와 큰 빈 배경을 공유한다. 현재 출시판보다 알갱이·기포 같은 점묘가 두드러진다.
- 전경과 배경: 앞의 검은 덩어리와 뒤의 푸른 돌층이 겹친다.
- 조명: 사선으로 내려오는 넓은 빛과 밝은 수면이 보인다.
- 제작 패턴: P04, P12 — 목표에 모이는 빛 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로 · 자산 명세 B04, B05, B14
- [출처 페이지](https://www.teamcherry.com.au/blog/the-green-path-a-hollow-knight-tour) · [제공 이미지](https://images.squarespace-cdn.com/content/v1/606d4deb4db8c15ea53b3624/1618900856929-F475LO4VJ8XCI406TX0X/Fungus_05.jpg)

### HK-GP20 초기 개발판의 거대 유해

[이미지 보기](../hollow-knight-greenpath/images/gp20.jpg) · HK / Greenpath · 랜드마크 · 곡면 외피, 이끼

- 관찰: 작은 주인공 옆에 거대한 껍질 또는 유해가 배치된다. 큰 곡면의 몇 개 구멍만으로 낡은 생물의 규모를 만든다.
- 전경과 배경: 앞쪽 어둠과 뒤의 푸른 큰 형태 사이에 작은 캐릭터가 있다.
- 조명: 차가운 대기광이 유해의 윤곽만 드러낸다.
- 제작 패턴: P03, P12, P16 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 이끼 통로, 유물 획득 지점 · 자산 명세 B03, B14, B17
- [출처 페이지](https://www.teamcherry.com.au/blog/the-green-path-a-hollow-knight-tour) · [제공 이미지](https://images.squarespace-cdn.com/content/v1/606d4deb4db8c15ea53b3624/1618900873629-BB8YVWYVVEMOZ7XQHEAF/Fungus_04.jpg)

### HK-GP21 초기 개발판의 호숫가 난간

[이미지 보기](../hollow-knight-greenpath/images/gp21.jpg) · HK / Greenpath · 수평 통로 · 곡면 외피, 금속, 액체

- 관찰: 가느다란 다리와 넓은 물가가 수평으로 이어진다. 구멍 난 큰 유기체와 문양 수면이 초기판 특징이다.
- 전경과 배경: 앞 난간·중앙 보행면·뒤 큰 유기체가 분리된다.
- 조명: 청록빛 수면과 사선 빛이 화면 아래와 위를 연결한다.
- 제작 패턴: P04, P05, P12 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로 · 자산 명세 B04, B05, B06, B14
- [출처 페이지](https://www.teamcherry.com.au/blog/the-green-path-a-hollow-knight-tour) · [제공 이미지](https://images.squarespace-cdn.com/content/v1/606d4deb4db8c15ea53b3624/1618900771877-ZNK32GKBU2AR3OGN1EUO/Fungus_03.jpg)

### HK-GP22 비행 적과 수직 발판

[이미지 보기](../hollow-knight-greenpath/images/gp22.jpg) · HK / Greenpath · 수직 이동 · 석재, 이끼, 잎, 뿌리

- 관찰: 작은 발판 사이 공중에 돌진형 적이 놓인다. 작은 발판은 잎 테두리와 아래 뿌리로 한 덩어리가 된다.
- 전경과 배경: 오른쪽 검은 벽과 뒤 큰 식물의 대비가 뚜렷하다.
- 조명: 청록색 밝은 공간 안에 캐릭터와 비행 적이 보인다.
- 제작 패턴: P05, P15 — 다음 착지면이 보이는 수직 이동 / 적 실루엣과 공격 방향
- 적용 후보: 하강 통로, 이끼 통로 · 자산 명세 B06, B16
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/7f/7d/14249-hollow-knight-077-grub-1-verchemin-1.jpg)

### HK-GP23 잎 단서가 있는 높은 길

[이미지 보기](../hollow-knight-greenpath/images/gp23.jpg) · HK / Greenpath · 보상 포켓 · 이끼, 잎, 석재

- 관찰: 상부 통로와 아래 발판이 겹쳐 샛길의 높이 차를 보여준다. 흩어진 잎과 빽빽한 가장자리 이끼가 방향의 단서가 된다.
- 전경과 배경: 중앙 검은 지형 속과 그 아래 선명한 뿌리가 보인다.
- 조명: 화면 우측 위의 작은 밝은 영역이 열린 길을 읽히게 한다.
- 제작 패턴: P01, P02, P08, P12 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 보상의 선노출과 우회 경로 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 보상 포켓 · 자산 명세 B01, B02, B10, B14
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/8a/24/14250-hollow-knight-077-grub-1-verchemin-2-bis.jpg)

### HK-GP24 덩굴을 타격하는 장면

[이미지 보기](../hollow-knight-greenpath/images/gp24.jpg) · HK / Greenpath · 장치 공간 · 이끼, 잎, 뿌리

- 관찰: 공격이 닿는 덩굴 근처에 발판과 길이 모인다. 얇은 덩굴과 잎 조각이 무거운 지형에서 분리된다.
- 전경과 배경: 검은 상부 코어 뒤로 큰 푸른 줄기가 있다.
- 조명: 짧은 흰 공격선과 주황색 타격 광점이 배경보다 강하다.
- 제작 패턴: P04, P05, P06 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함
- 적용 후보: 이끼 통로, 고대 장치 구역 · 자산 명세 B04, B05, B06, B07, B08
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/48/77/14251-hollow-knight-077-grub-1-verchemin-2.jpg)

### HK-GP25 높은 곳의 구출 보상

[이미지 보기](../hollow-knight-greenpath/images/gp25.jpg) · HK / Greenpath · 보상 포켓 · 석재, 이끼, 잎, 병

- 관찰: 오른쪽 높은 지점의 병과 아래 발판이 목적·접근로를 나눈다. 벽의 잎 띠와 둥근 문양 돌이 반복된다.
- 전경과 배경: 앞의 검은 위쪽 천장과 아래 푸른 원경이 열린다.
- 조명: 목표 부근이 주변 잎보다 밝게 보여 보상을 찾게 한다.
- 제작 패턴: P04, P05, P08 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 보상의 선노출과 우회 경로
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B04, B05, B06, B10
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/ff/87/14252-hollow-knight-077-grub-1-verchemin-3.jpg)

### HK-GP26 잘린 덩굴 아래 이동 발판

[이미지 보기](../hollow-knight-greenpath/images/gp26.jpg) · HK / Greenpath · 장치 공간 · 이끼, 잎, 뿌리

- 관찰: 중앙 큰 발판과 옆의 작은 발판이 단계적인 이동을 만든다. 부서지는 덩굴 잎과 발판 아래 뿌리가 다른 밀도로 표현된다.
- 전경과 배경: 위 검은 천장과 뒤 청록색 여백이 충돌면을 둘러싼다.
- 조명: 착지할 발판을 둘러싼 배경이 밝아 외곽이 잘 읽힌다.
- 제작 패턴: P05, P06, P12 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 고대 장치 구역 · 자산 명세 B06, B07, B08, B14
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/22/00/14253-hollow-knight-078-grub-2-verchemin-1.jpg)

### HK-GP27 가시 위에 남는 안전 공간

[이미지 보기](../hollow-knight-greenpath/images/gp27.jpg) · HK / Greenpath · 위험 구간 · 이끼, 가시

- 관찰: 작은 안전면과 가시 바닥이 가까워 이동 판단을 요구한다. 밝고 날카로운 가시와 둥근 이끼가 재질로 분리된다.
- 전경과 배경: 오른쪽과 아래 검은 지형 내부가 통로의 끝을 만든다.
- 조명: 위험물 끝은 흐리지 않고 중앙만 청록색으로 연다.
- 제작 패턴: P05, P07, P12 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 보스 접근 구간 · 자산 명세 B06, B09, B14
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/57/30/14254-hollow-knight-078-grub-2-verchemin-2.jpg)

### HK-GP28 가시 구덩이를 건너는 발판

[이미지 보기](../hollow-knight-greenpath/images/gp28.jpg) · HK / Greenpath · 위험 구간 · 이끼, 뿌리, 가시

- 관찰: 양옆 안전면 사이 가시와 발판이 놓여 이동 순서를 만든다. 매달린 뿌리와 뾰족한 가시의 방향성이 서로 다르다.
- 전경과 배경: 상하 검은 덩어리가 가운데 밝은 통로를 감싼다.
- 조명: 경로 중앙의 부드러운 푸른 빛이 이동 공간을 드러낸다.
- 제작 패턴: P05, P07 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 하강 통로, 이끼 통로 · 자산 명세 B06, B09
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/54/53/14255-hollow-knight-078-grub-2-verchemin-3.jpg)

### HK-GP29 산성 웅덩이의 작은 섬

[이미지 보기](../hollow-knight-greenpath/images/gp29.jpg) · HK / Greenpath · 보상 포켓 · 이끼, 잎, 액체

- 관찰: 물 위 두 작은 발판과 우측 보상 높이가 단계적으로 이어진다. 떠 있는 발판의 불규칙한 잎 덩어리가 배경과 분리된다.
- 전경과 배경: 아래 수면은 넓고 상부 천장은 검은 실루엣이다.
- 조명: 밝은 액체 면과 어두운 발판의 명암 대비가 위험을 알린다.
- 제작 패턴: P04, P05, P07 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 보상 포켓, 이끼 통로 · 자산 명세 B04, B05, B06, B09
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/e8/19/14256-hollow-knight-078-grub-2-verchemin-4.jpg)

### HK-GP30 구출 직후의 작은 보상방

[이미지 보기](../hollow-knight-greenpath/images/gp30.jpg) · HK / Greenpath · 보상 포켓 · 석재, 이끼, 잎

- 관찰: 오른쪽 끝의 안전한 바닥에 캐릭터와 보상이 모인다. 둥근 돌과 잎이 좁은 방을 감싼다.
- 전경과 배경: 바닥 속은 검고 배경은 푸른 대기층으로 물러난다.
- 조명: 보상 주변의 밝기를 유지하고 위 천장은 어둡게 닫는다.
- 제작 패턴: P05, P08, P10 — 다음 착지면이 보이는 수직 이동 / 보상의 선노출과 우회 경로 / 작고 명료한 휴식 포켓
- 적용 후보: 보상 포켓, 이끼 통로 · 자산 명세 B06, B10, B12
- [출처 페이지](https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages) · [제공 이미지](https://www.monster-soluce.com/uploads/scale-max/90/5b/14257-hollow-knight-078-grub-2-verchemin-5.jpg)

### HK-GP31 이끼 돌진충의 큰 잎 덩어리

[이미지 보기](../hollow-knight-greenpath/images/gp31.png) · HK / Greenpath · 전투 공간 · 잎, 생물 외곽

- 관찰: 긴 평평한 보행면에 가로로 긴 적이 놓인다. 잎 위장 덩어리에 얼굴이 드러나 배경 식생과 몸체를 구별한다.
- 전경과 배경: 위 유적 발판의 검은 코어와 하단 적의 밝은 외곽이 대비된다.
- 조명: 차가운 빛 속에서 적 얼굴의 밝은 점이 시선을 끈다.
- 제작 패턴: P11, P12, P15 — 전투방의 넓은 판독 공간 / 재질의 군집과 빈 구간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 이끼 통로 · 자산 명세 B13, B14, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Moss_Charger_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8d/Screenshot_HK_Moss_Charger_01.png/800px-Screenshot_HK_Moss_Charger_01.png)

### HK-GP32 작은 이끼족 무리

[이미지 보기](../hollow-knight-greenpath/images/gp32.png) · HK / Greenpath · 전투 공간 · 잎, 생물 외곽

- 관찰: 낮은 통로에 비슷한 체형 둘이 배치된다. 털·잎처럼 일어난 외곽과 밝은 몸통이 특징이다.
- 전경과 배경: 검은 중간 지형 때문에 적은 아래 통로에 또렷하게 보인다.
- 조명: 큰 원형 효과 없이 몸통 명암만으로 적을 분리한다.
- 제작 패턴: P03, P11, P15 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 이끼 통로 · 자산 명세 B03, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Mosskin_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/55/Screenshot_HK_Mosskin_01.png/800px-Screenshot_HK_Mosskin_01.png)

### HK-GP33 폭발하는 이끼족의 주황 신호

[이미지 보기](../hollow-knight-greenpath/images/gp33.png) · HK / Greenpath · 전투 공간 · 생물 외곽, 입자 구름

- 관찰: 좁은 발판의 둥근 적과 주황 구름이 결합한다. 둥근 몸에 점 같은 돌기가 있고 큰 주황 덩어리가 녹색을 깨뜨린다.
- 전경과 배경: 검은 천장과 푸른 배경이 폭발 신호의 대비를 높인다.
- 조명: 따뜻한 주황색은 차가운 지역 팔레트에서 위험 신호가 된다.
- 제작 패턴: P04, P07, P14, P15 — 목표에 모이는 빛 / 안전면과 위험면의 다른 형태 / 기능색과 장식색의 분리 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 이끼 통로 · 자산 명세 B04, B05, B09, B16, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Volatile_Mosskin_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a3/Screenshot_HK_Volatile_Mosskin_01.png/800px-Screenshot_HK_Volatile_Mosskin_01.png)

### HK-GP34 방패와 긴 무기의 이끼 기사

[이미지 보기](../hollow-knight-greenpath/images/gp34.png) · HK / Greenpath · 전투 공간 · 잎, 방패, 무기

- 관찰: 낮고 긴 무기 실루엣이 이동·공격 방향을 가리킨다. 둥근 방패와 잘게 갈라진 잎 갑옷이 다른 크기로 읽힌다.
- 전경과 배경: 뒤 큰 나무줄기는 어두워 무기 윤곽을 과도하게 방해하지 않는다.
- 조명: 낮은 채도의 배경 위 밝은 갑옷과 흰 무기가 보인다.
- 제작 패턴: P11, P12, P15 — 전투방의 넓은 판독 공간 / 재질의 군집과 빈 구간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B13, B14, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Moss_Knight_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/0e/Screenshot_HK_Moss_Knight_01.png/800px-Screenshot_HK_Moss_Knight_01.png)

### HK-GP35 통로 옆 고정형 식물 적

[이미지 보기](../hollow-knight-greenpath/images/gp35.png) · HK / Greenpath · 전투 공간 · 잎, 생물 외곽

- 관찰: 좌상단 작은 식물과 아래 이동 공간이 분리된다. 배경 잎과 비슷한 형상에 얼굴·입 부분이 작게 보인다.
- 전경과 배경: 큰 검은 중앙 코어가 통로를 위아래로 나눈다.
- 조명: 푸른 주변광 위로 적의 작은 밝은 얼굴이 대비된다.
- 제작 패턴: P01, P02, P05, P15 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 다음 착지면이 보이는 수직 이동 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 이끼 통로 · 자산 명세 B01, B02, B06, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Gulka_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/cd/Screenshot_HK_Gulka_01.png/800px-Screenshot_HK_Gulka_01.png)

### HK-GP36 상하 지형 사이 바보잡이풀

[이미지 보기](../hollow-knight-greenpath/images/gp36.png) · HK / Greenpath · 위험 구간 · 잎, 이빨 외곽

- 관찰: 위아래 통로 틈의 큰 벌어진 입이 이동 경계와 겹친다. 식물 잎과 이빨의 날카로운 외곽을 함께 쓴다.
- 전경과 배경: 검은 지형 내부와 입의 밝은 면이 대비되어 위치가 드러난다.
- 조명: 밝은 입 내부가 푸른 배경에서 눈에 띈다.
- 제작 패턴: P03, P07, P15 — 중경과 원경의 다른 대비 / 안전면과 위험면의 다른 형태 / 적 실루엣과 공격 방향
- 적용 후보: 이끼 통로, 보스 접근 구간 · 자산 명세 B03, B09, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fool_Eater_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/7f/Screenshot_HK_Fool_Eater_01.png/800px-Screenshot_HK_Fool_Eater_01.png)

### HK-GP37 오블의 공중 탄막

[이미지 보기](../hollow-knight-greenpath/images/gp37.png) · HK / Greenpath · 전투 공간 · 생물 외곽, 투사체

- 관찰: 작은 발판 주변의 둥근 비행 적과 여러 발사체가 공중을 나눈다. 둥근 적 몸과 둥근 탄환이 같은 계열 형태를 쓴다.
- 전경과 배경: 뒤 수직 빛줄기는 흐리고 탄환 가장자리는 선명하다.
- 조명: 따뜻한 발사체가 차가운 청록 배경에서 강하게 보인다.
- 제작 패턴: P04, P11, P14, P15 — 목표에 모이는 빛 / 전투방의 넓은 판독 공간 / 기능색과 장식색의 분리 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B04, B05, B13, B16, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Obble_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/ca/Screenshot_HK_Obble_01.png/800px-Screenshot_HK_Obble_01.png)

### HK-GP38 모기의 가늘고 뾰족한 몸

[이미지 보기](../hollow-knight-greenpath/images/gp38.png) · HK / Greenpath · 전투 공간 · 날개, 침 외곽, 이끼

- 관찰: 왼쪽 공중의 길쭉한 적이 작은 발판 사이 경로를 가로지른다. 침 모양 주둥이와 얇은 날개가 둥근 이끼와 다른 외곽을 만든다.
- 전경과 배경: 오른쪽 검은 지형 코어가 비행 경로의 끝을 또렷하게 한다.
- 조명: 별도 강한 광원보다 가는 밝은 몸체 윤곽이 중요하다.
- 제작 패턴: P05, P11, P15 — 다음 착지면이 보이는 수직 이동 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 이끼 통로 · 자산 명세 B06, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Squit_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/11/Screenshot_HK_Squit_01.png/800px-Screenshot_HK_Squit_01.png)

### HK-GP39 가시 틈의 단단한 비행체

[이미지 보기](../hollow-knight-greenpath/images/gp39.png) · HK / Greenpath · 위험 구간 · 생물 외피, 가시

- 관찰: 위·아래 가시 사이의 비행체가 좁은 이동 공간을 차지한다. 단단한 껍질의 가시와 둥근 중앙 몸체가 위험 형태를 반복한다.
- 전경과 배경: 배경의 흐린 유적과 선명한 적 껍질이 분리된다.
- 조명: 밝은 주황색 눈과 차가운 껍질이 구별된다.
- 제작 패턴: P07, P12, P15 — 안전면과 위험면의 다른 형태 / 재질의 군집과 빈 구간 / 적 실루엣과 공격 방향
- 적용 후보: 이끼 통로, 보스 접근 구간 · 자산 명세 B09, B14, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Duranda_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c6/Screenshot_HK_Duranda_01.png/800px-Screenshot_HK_Duranda_01.png)

### HK-EX01 여왕의 정원의 큰 전경 잎

[이미지 보기](../hollow-knight-greenpath/images/ex01.png) · HK / Queen's Gardens · 수평 통로 · 석재, 잎, 꽃

- 관찰: 큰 식물과 유적 기둥이 화면 양끝을 채운다. 넓은 잎 면·작은 꽃·가느다란 건축 선이 크기로 구분된다.
- 전경과 배경: 하단의 거의 검은 큰 잎은 카메라 가까운 가림물로 읽힌다.
- 조명: 중앙 청록 빛과 점 발광 식물이 겹친다.
- 제작 패턴: P01, P02, P03 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B01, B02, B03
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/91/Screenshot_HK_Queen%27s_Gardens_01.png/800px-Screenshot_HK_Queen%27s_Gardens_01.png)

### HK-EX02 여왕의 정원의 매달린 발판

[이미지 보기](../hollow-knight-greenpath/images/ex02.png) · HK / Queen's Gardens · 수직 이동 · 석재, 금속, 잎

- 관찰: 얇은 줄과 발판이 수직 이동의 규칙을 만든다. 규칙적인 금속·돌 테두리에 자연 식물이 끼어든다.
- 전경과 배경: 앞쪽 검은 식물, 중앙 매달린 구조, 흐린 초록 배경을 구분한다.
- 조명: 여러 작은 발광체가 층마다 다른 크기로 배치된다.
- 제작 패턴: P03, P04, P05 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 고대 장치 구역, 하강 통로 · 자산 명세 B03, B04, B05, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/94/Screenshot_HK_Queen%27s_Gardens_02.png/800px-Screenshot_HK_Queen%27s_Gardens_02.png)

### HK-EX03 안개 협곡의 발광 생물과 흐린 전경

[이미지 보기](../hollow-knight-greenpath/images/ex03.png) · HK / Fog Canyon · 열린 방 · 석재, 구형 생물, 기포

- 관찰: 구불거리는 지형 사이 열린 공간에 발광 생물이 뜬다. 둥근 기포와 부드러운 생물 표면이 돌과 다른 감촉을 만든다.
- 전경과 배경: 크고 흐린 원은 가까운 입자처럼 읽히며 지형 속의 검정과 다르다.
- 조명: 흰 중심·분홍 후광·보랏빛 안개가 겹친다.
- 제작 패턴: P03, P04 — 중경과 원경의 다른 대비 / 목표에 모이는 빛
- 적용 후보: 문양의 성소, 유물 획득 지점 · 자산 명세 B03, B04, B05
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b3/Screenshot_HK_Fog_Canyon_01.png/800px-Screenshot_HK_Fog_Canyon_01.png)

### HK-EX04 버섯 황무지의 하단 실루엣

[이미지 보기](../hollow-knight-greenpath/images/ex04.png) · HK / Fungal Wastes · 수평 통로 · 버섯, 줄기

- 관찰: 천장과 바닥이 가운데 큰 푸른 빈 공간을 감싼다. 둥근 버섯 갓과 가는 줄기라는 단순 형태를 반복한다.
- 전경과 배경: 앞 하단 버섯은 검고 뒤 버섯은 청록색으로 물러난다.
- 조명: 중앙 황록색 작은 빛무리가 깊이를 만든다.
- 제작 패턴: P01, P02, P03 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B01, B02, B03
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1f/Screenshot_HK_Fungal_Wastes_01.png/800px-Screenshot_HK_Fungal_Wastes_01.png)

### HK-EX05 눈물의 도시의 층진 건축

[이미지 보기](../hollow-knight-greenpath/images/ex05.png) · HK / City of Tears · 복층 공간 · 석재, 금속

- 관찰: 긴 수평 발판과 큰 수직 기둥이 도시 깊이를 만든다. 금속 장식의 얇은 선과 돌 받침의 큰 면이 대비된다.
- 전경과 배경: 앞 난간·중앙 가로등·먼 건물의 명암 차가 뚜렷하다.
- 조명: 흰 작은 가로등 주변으로 푸른 안개가 번진다.
- 제작 패턴: P03, P04, P16 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/2b/Screenshot_HK_City_of_Tears_01.png/800px-Screenshot_HK_City_of_Tears_01.png)

### HK-EX06 수정 봉우리의 보랏빛 광막

[이미지 보기](../hollow-knight-greenpath/images/ex06.png) · HK / Crystal Peak · 복층 공간 · 수정, 석재, 금속

- 관찰: 중앙 발판과 긴 사슬이 밝은 배경 앞에 놓인다. 각진 수정과 격자 구조가 유기적 이끼와 반대되는 형태다.
- 전경과 배경: 검은 사슬·중앙 발판·보라 원경이 층으로 겹친다.
- 조명: 넓은 보라 빛과 작은 흰 등불은 서로 다른 범위를 갖는다.
- 제작 패턴: P04, P16 — 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 고대 장치 구역, 중앙 통로 · 자산 명세 B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/60/Screenshot_HK_Crystal_Peak_01.png/800px-Screenshot_HK_Crystal_Peak_01.png)

### HK-FC-01 빛기둥과 낮은 유적

[이미지 보기](images/hk-fc-01.png) · HK / Forgotten Crossroads · 수평 통로 · 석재, 식생

- 관찰: 낮은 긴 발판 뒤에 세로 기둥과 식물 군집이 반복된다.
- 전경과 배경: 하단 검은 잎 앞에 선명한 상면, 뒤에 흐린 아치가 놓인다.
- 조명: 가느다란 수직 광막이 중앙의 빈 공간을 나눈다.
- 제작 패턴: P01, P03, P12 — 검은 지형 속과 읽히는 테두리 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B01, B03, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f0/Screenshot_HK_Forgotten_Crossroads_01.png/800px-Screenshot_HK_Forgotten_Crossroads_01.png)

### HK-FC-02 사슬 옆 작은 누각

[이미지 보기](images/hk-fc-02.png) · HK / Forgotten Crossroads · 장치 공간 · 금속, 석재

- 관찰: 큰 사슬과 중간 발판, 지붕 있는 구조물이 다른 높이로 겹친다.
- 전경과 배경: 가까운 사슬은 검고 뒤 기둥은 푸르게 물러난다.
- 조명: 작은 흰 등불과 차가운 배경광을 분리한다.
- 제작 패턴: P03, P06, P16 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 방마다 하나의 큰 기억점
- 적용 후보: 고대 장치 구역 · 자산 명세 B03, B07, B08, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/89/Screenshot_HK_Forgotten_Crossroads_02.png/800px-Screenshot_HK_Forgotten_Crossroads_02.png)

### HK-FC-03 상하층의 둥근 출입구

[이미지 보기](images/hk-fc-03.png) · HK / Forgotten Crossroads · 복층 공간 · 석재, 금속

- 관찰: 윗 통로 아래 여러 둥근 문이 있어 같은 공간의 높이 차가 읽힌다.
- 전경과 배경: 상부 검은 지형 코어와 하부 문 표면이 구별된다.
- 조명: 푸른 빛이 열린 통로만 드러낸다.
- 제작 패턴: P01, P05, P09 — 검은 지형 속과 읽히는 테두리 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B01, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/40/Screenshot_HK_Forgotten_Crossroads_03.png/800px-Screenshot_HK_Forgotten_Crossroads_03.png)

### HK-FC-04 큰 문과 따뜻한 등불

[이미지 보기](images/hk-fc-04.png) · HK / Forgotten Crossroads · 지역 경계 · 석재, 뼈

- 관찰: 양옆 높은 선이 중앙의 밝은 문으로 모인다.
- 전경과 배경: 외곽 검은 실루엣이 문 앞 넓은 바닥을 감싼다.
- 조명: 흰 보라색 문과 양옆 주황빛이 크기 차를 만든다.
- 제작 패턴: P04, P09, P16 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b5/Screenshot_HK_Forgotten_Crossroads_04.png/800px-Screenshot_HK_Forgotten_Crossroads_04.png)

### HK-FC-05 큰 껍질 건물의 문

[이미지 보기](images/hk-fc-05.png) · HK / Forgotten Crossroads · 랜드마크 · 껍질, 석재

- 관찰: 커다란 뾰족 곡면 건물 한 점이 평평한 길의 중심이 된다.
- 전경과 배경: 앞쪽 가는 난간과 뒤 큰 건물의 덩어리 크기가 다르다.
- 조명: 건물 전체보다 문틈만 흰색으로 밝다.
- 제작 패턴: P04, P09, P16 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6f/Screenshot_HK_Forgotten_Crossroads_05.png/800px-Screenshot_HK_Forgotten_Crossroads_05.png)

### HK-FC-06 감염색으로 바뀐 회랑

[이미지 보기](images/hk-fc-06.png) · HK / Forgotten Crossroads · 전투 공간 · 석재, 유기체

- 관찰: 같은 계열 유적 위에 주황 덩어리가 붙어 지역 상태가 달라 보인다.
- 전경과 배경: 검은 보행면 위 밝은 주황 형체가 분리된다.
- 조명: 차가운 회랑 안 주황색이 강한 신호를 만든다.
- 제작 패턴: P15, P19 — 적 실루엣과 공격 방향 / 공간 골격을 유지한 상태 변화
- 적용 후보: 전투방, 보스방 · 자산 명세 B16, B19
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Forgotten_Crossroads_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/82/Screenshot_HK_Forgotten_Crossroads_06.png/800px-Screenshot_HK_Forgotten_Crossroads_06.png)

### HK-FW-02 폭포 아래 작은 발판

[이미지 보기](images/hk-fw-02.png) · HK / Fungal Wastes · 위험 구간 · 버섯, 석재, 액체

- 관찰: 수면 위 중앙 발판과 오른쪽 높은 턱이 이동 순서를 만든다.
- 전경과 배경: 두꺼운 검은 지형 속과 뒤 점무늬 식물이 분리된다.
- 조명: 세로 낙수와 밝은 수평 액체가 만난다.
- 제작 패턴: P05, P07, P13 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 대기광과 입자의 깊이
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f5/Screenshot_HK_Fungal_Wastes_02.png/800px-Screenshot_HK_Fungal_Wastes_02.png)

### HK-FW-03 액체 위 쌍둥이 섬

[이미지 보기](images/hk-fw-03.png) · HK / Fungal Wastes · 위험 구간 · 버섯, 석재, 액체

- 관찰: 넓은 액체 사이 두 안전면과 높은 작은 발판이 보인다.
- 전경과 배경: 앞쪽 식물은 검고 뒤 식물 군집은 밝고 흐리다.
- 조명: 황록색 수면이 안전면의 어두운 외곽을 드러낸다.
- 제작 패턴: P05, P07, P18 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/07/Screenshot_HK_Fungal_Wastes_03.png/800px-Screenshot_HK_Fungal_Wastes_03.png)

### HK-FW-04 작은 밝은 둥지

[이미지 보기](images/hk-fw-04.png) · HK / Fungal Wastes · 보상 포켓 · 버섯, 석재

- 관찰: 돌과 버섯이 둘러싼 작은 공간 중앙에 밝은 덩어리가 놓인다.
- 전경과 배경: 주변 검은 코어가 작은 중앙 포켓을 감싼다.
- 조명: 국소 황금빛이 주변보다 훨씬 밝다.
- 제작 패턴: P04, P08 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/58/Screenshot_HK_Fungal_Wastes_04.png/800px-Screenshot_HK_Fungal_Wastes_04.png)

### HK-FW-05 높은 버섯과 작은 건물

[이미지 보기](images/hk-fw-05.png) · HK / Fungal Wastes · 랜드마크 · 버섯, 석재, 금속

- 관찰: 크기가 다른 버섯과 문양 건물이 평평한 바닥 위에 놓인다.
- 전경과 배경: 가까운 식물과 뒤 포자 무리의 크기 차가 있다.
- 조명: 뒤의 작은 빛무리는 건물의 선명한 선보다 약하다.
- 제작 패턴: P03, P12, P16 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b3/Screenshot_HK_Fungal_Wastes_05.png/800px-Screenshot_HK_Fungal_Wastes_05.png)

### HK-FW-06 산성 웅덩이를 잇는 다리

[이미지 보기](images/hk-fw-06.png) · HK / Fungal Wastes · 수평 통로 · 석재, 금속, 액체

- 관찰: 가느다란 다리와 문양 기둥이 액체 위 길을 잇는다.
- 전경과 배경: 위 검은 지형 아래 가시 테두리와 뒤 유적이 겹친다.
- 조명: 밝은 수면과 낮은 대비의 배경으로 다리 윤곽을 읽힌다.
- 제작 패턴: P07, P09, P16 — 안전면과 위험면의 다른 형태 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로 · 자산 명세 B09, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fungal_Wastes_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/4f/Screenshot_HK_Fungal_Wastes_06.png/800px-Screenshot_HK_Fungal_Wastes_06.png)

### HK-CT-02 분수와 먼 기둥

[이미지 보기](images/hk-ct-02.png) · HK / City of Tears · 랜드마크 · 석재, 물, 금속

- 관찰: 수평 바닥 뒤 분수와 높은 건축이 공간 규모를 만든다.
- 전경과 배경: 하단 검은 난간과 뒤 흐린 도시 기둥이 여러 깊이로 읽힌다.
- 조명: 청색의 낮은 대비와 작은 물빛이 중심을 만든다.
- 제작 패턴: P03, P13, P16 — 중경과 원경의 다른 대비 / 대기광과 입자의 깊이 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B15, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/25/Screenshot_HK_City_of_Tears_02.png/800px-Screenshot_HK_City_of_Tears_02.png)

### HK-CT-03 큰 창 아래 벤치

[이미지 보기](images/hk-ct-03.png) · HK / City of Tears · 휴식 포켓 · 석재, 유리, 금속

- 관찰: 매우 큰 창 아래 작은 벤치가 놓여 크기 차가 강조된다.
- 전경과 배경: 앞쪽 바닥은 선명하고 양옆 구조는 어둡게 감싼다.
- 조명: 창의 넓은 푸른빛과 작은 흰 등불이 겹친다.
- 제작 패턴: P04, P10, P16 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b5/Screenshot_HK_City_of_Tears_03.png/800px-Screenshot_HK_City_of_Tears_03.png)

### HK-CT-04 반복 창과 긴 회랑

[이미지 보기](images/hk-ct-04.png) · HK / City of Tears · 수평 통로 · 석재, 유리, 금속

- 관찰: 아치와 창의 반복 위에 긴 한 줄 보행면이 이어진다.
- 전경과 배경: 가까운 프레임과 먼 창 면의 대비가 다르다.
- 조명: 균일한 청색 창빛 안 작은 등불을 띄엄띄엄 둔다.
- 제작 패턴: P03, P12, P18 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로 · 자산 명세 B03, B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/2a/Screenshot_HK_City_of_Tears_04.png/800px-Screenshot_HK_City_of_Tears_04.png)

### HK-CT-05 도시의 수직 연결

[이미지 보기](images/hk-ct-05.png) · HK / City of Tears · 수직 이동 · 석재, 금속

- 관찰: 좌우 다른 높이의 짧은 발판과 깊은 중앙 틈이 연결된다.
- 전경과 배경: 선명한 발판 뒤에 낮은 대비의 큰 창들이 반복된다.
- 조명: 등불은 작은 지점, 배경은 넓은 푸른 면으로 구분된다.
- 제작 패턴: P03, P05, P06 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B06, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1d/Screenshot_HK_City_of_Tears_05.png/800px-Screenshot_HK_City_of_Tears_05.png)

### HK-CT-06 작은 문양빛과 어두운 바닥

[이미지 보기](images/hk-ct-06.png) · HK / City of Tears · 목표 노출 · 석재, 금속

- 관찰: 화면 왼쪽의 밝은 원형 문양에 주변 구조가 모인다.
- 전경과 배경: 앞의 검은 둥근 가림물과 뒤의 문양빛이 겹친다.
- 조명: 밝은 국소 문양을 중심으로 나머지 공간은 어둡다.
- 제작 패턴: P02, P04, P08 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_City_of_Tears_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/93/Screenshot_HK_City_of_Tears_06.png/800px-Screenshot_HK_City_of_Tears_06.png)

### HK-CP-02 수정과 공업 발판

[이미지 보기](images/hk-cp-02.png) · HK / Crystal Peak · 장치 공간 · 수정, 석재, 목재

- 관찰: 상하 높이가 다른 발판과 사다리형 구조 사이에 수정이 자란다.
- 전경과 배경: 검은 지형 속과 앞 사슬, 뒤의 밝은 수정 면을 구분한다.
- 조명: 보랏빛 넓은 배경 앞 실제 발판은 어둡게 읽힌다.
- 제작 패턴: P05, P06, P18 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역 · 자산 명세 B06, B07, B08, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9d/Screenshot_HK_Crystal_Peak_02.png/800px-Screenshot_HK_Crystal_Peak_02.png)

### HK-CP-03 두 등불 아래 벤치

[이미지 보기](images/hk-cp-03.png) · HK / Crystal Peak · 휴식 포켓 · 석재, 금속, 수정

- 관찰: 낮은 벤치 위 두 등불과 높은 검은 발판이 놓인다.
- 전경과 배경: 앞쪽 큰 검은 가림물과 뒤 둥근 벽의 선명도가 다르다.
- 조명: 작은 등불의 중심과 보라색 대기광이 분리된다.
- 제작 패턴: P04, P10, P13, P14 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 대기광과 입자의 깊이 / 기능색과 장식색의 분리
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B15, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/0f/Screenshot_HK_Crystal_Peak_03.png/800px-Screenshot_HK_Crystal_Peak_03.png)

### HK-CP-04 수정 방의 작은 기둥들

[이미지 보기](images/hk-cp-04.png) · HK / Crystal Peak · 수평 통로 · 수정, 석재

- 관찰: 평평한 바닥 위 짧은 기둥들이 간격을 두고 반복된다.
- 전경과 배경: 상하 검은 코어 사이로 각진 벽 패턴이 드러난다.
- 조명: 배경 보라색을 낮춰 작은 기둥의 상면을 읽힌다.
- 제작 패턴: P01, P12 — 검은 지형 속과 읽히는 테두리 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B01, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d0/Screenshot_HK_Crystal_Peak_04.png/800px-Screenshot_HK_Crystal_Peak_04.png)

### HK-CP-05 거대한 수정 면

[이미지 보기](images/hk-cp-05.png) · HK / Crystal Peak · 재질 상세 · 수정

- 관찰: 발판보다 수정의 각진 면과 크기 차가 화면 대부분을 차지한다.
- 전경과 배경: 앞의 선명한 수정 끝과 뒤의 흐린 밝은 면이 겹친다.
- 조명: 흰 중심과 넓은 분홍 보라색 번짐이 재질을 만든다.
- 제작 패턴: P12, P18 — 재질의 군집과 빈 구간 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역 · 자산 명세 B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e3/Screenshot_HK_Crystal_Peak_05.png/800px-Screenshot_HK_Crystal_Peak_05.png)

### HK-CP-06 수정 구덩이 옆 통로

[이미지 보기](images/hk-cp-06.png) · HK / Crystal Peak · 위험 구간 · 수정, 목재, 석재

- 관찰: 오른쪽 작은 안전면과 아래 수정 군집 사이 여유가 좁다.
- 전경과 배경: 가까운 검은 천장과 뒤 밝은 수정 면이 대비된다.
- 조명: 밝은 위험 재질을 실제 안전 발판과 다른 실루엣으로 구별한다.
- 제작 패턴: P05, P07, P18 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Crystal_Peak_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b5/Screenshot_HK_Crystal_Peak_06.png/800px-Screenshot_HK_Crystal_Peak_06.png)

### HK-DN-01 뿌리와 잔해의 평평한 길

[이미지 보기](images/hk-dn-01.png) · HK / Deepnest · 수평 통로 · 뿌리, 껍질, 뼈

- 관찰: 낮은 잔해 위로 여러 굵은 뿌리가 지나간다.
- 전경과 배경: 거의 검은 앞 뿌리와 푸른 뒤 벽이 겹친다.
- 조명: 넓고 약한 청색 대기광만 남긴다.
- 제작 패턴: P02, P03, P12 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/48/Screenshot_HK_Deepnest_01.png/800px-Screenshot_HK_Deepnest_01.png)

### HK-DN-02 가시 사이 좁은 기둥

[이미지 보기](images/hk-dn-02.png) · HK / Deepnest · 위험 구간 · 석재, 뿌리, 가시

- 관찰: 바닥의 긴 가시 위에 짧고 좁은 안전 기둥이 있다.
- 전경과 배경: 앞 검은 줄기와 뒤 부드러운 벽 사이 안전면이 놓인다.
- 조명: 가시 끝과 기둥 상면이 주변보다 밝다.
- 제작 패턴: P05, P07 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/41/Screenshot_HK_Deepnest_02.png/800px-Screenshot_HK_Deepnest_02.png)

### HK-DN-03 무너진 지형 아래 먼 문

[이미지 보기](images/hk-dn-03.png) · HK / Deepnest · 지역 경계 · 석재, 금속, 뿌리

- 관찰: 위의 큰 검은 덩어리 아래에 먼 출입구가 보인다.
- 전경과 배경: 가까운 코어가 위를 가리고 건물 입구는 뒤로 물러난다.
- 조명: 입구의 작은 밝은 면이 어두운 길의 방향을 표시한다.
- 제작 패턴: P01, P03, P09 — 검은 지형 속과 읽히는 테두리 / 중경과 원경의 다른 대비 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B01, B03, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f5/Screenshot_HK_Deepnest_03.png/800px-Screenshot_HK_Deepnest_03.png)

### HK-DN-04 실로 둘러싼 높은 건물

[이미지 보기](images/hk-dn-04.png) · HK / Deepnest · 수직 이동 · 실, 석재, 껍질

- 관찰: 중앙의 높은 문과 양옆 작은 발판이 세로 구성을 만든다.
- 전경과 배경: 앞 가는 실과 뒤의 흐린 빈 공간을 분리한다.
- 조명: 문틈은 흰색이고 주변은 차가운 보라색 안개다.
- 제작 패턴: P04, P05, P16 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B04, B05, B06, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/43/Screenshot_HK_Deepnest_04.png/800px-Screenshot_HK_Deepnest_04.png)

### HK-DN-05 긴 뿌리 사이 낮은 벤치

[이미지 보기](images/hk-dn-05.png) · HK / Deepnest · 휴식 포켓 · 뿌리, 석재

- 관찰: 평평한 바닥에 벤치가 작게 있고 큰 뿌리가 주변을 감싼다.
- 전경과 배경: 앞쪽 검은 줄기가 큰 프레임, 뒤쪽 바위가 작은 질감이다.
- 조명: 한쪽 뒤의 푸른 밝기가 벤치 주변 여백을 드러낸다.
- 제작 패턴: P02, P10, P17 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓 / 비대칭 공간의 무게 배분
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B03, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c7/Screenshot_HK_Deepnest_05.png/800px-Screenshot_HK_Deepnest_05.png)

### HK-DN-06 어두운 좌우 기둥과 중앙 의자

[이미지 보기](images/hk-dn-06.png) · HK / Deepnest · 랜드마크 · 껍질, 석재

- 관찰: 뾰족한 중앙 구조 하나를 좌우 긴 형태가 감싼다.
- 전경과 배경: 앞 검은 선과 뒤 회색 공간이 극단적으로 분리된다.
- 조명: 낮은 회색 조명에서 중앙 외곽만 또렷하다.
- 제작 패턴: P02, P11, P16 — 근접 전경과 중앙 시야 여백 / 전투방의 넓은 판독 공간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B13, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Deepnest_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/14/Screenshot_HK_Deepnest_06.png/800px-Screenshot_HK_Deepnest_06.png)

### HK-QG-03 덩굴이 감싼 휴식점

[이미지 보기](images/hk-qg-03.png) · HK / Queen's Gardens · 휴식 포켓 · 잎, 덩굴, 석재

- 관찰: 낮은 벤치 위로 긴 덩굴이 내려오고 중앙은 비어 있다.
- 전경과 배경: 앞의 굵은 검은 줄기와 뒤 부드러운 초록 공간이 겹친다.
- 조명: 부드러운 넓은 빛과 작은 흰 점이 공존한다.
- 제작 패턴: P02, P10, P13 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓 / 대기광과 입자의 깊이
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B12, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/74/Screenshot_HK_Queen%27s_Gardens_03.png/800px-Screenshot_HK_Queen%27s_Gardens_03.png)

### HK-QG-04 가시 벽 옆 매달린 발판

[이미지 보기](images/hk-qg-04.png) · HK / Queen's Gardens · 위험 구간 · 금속, 잎, 가시

- 관찰: 가느다란 매달린 발판 옆으로 높은 가시 벽이 이어진다.
- 전경과 배경: 검은 코어와 가까운 식물 뒤로 초록 원경이 열린다.
- 조명: 가시의 따뜻한 끝을 청록 배경에서 구분한다.
- 제작 패턴: P05, P06, P07 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B07, B08, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9c/Screenshot_HK_Queen%27s_Gardens_04.png/800px-Screenshot_HK_Queen%27s_Gardens_04.png)

### HK-QG-05 가려진 작은 쉼터

[이미지 보기](images/hk-qg-05.png) · HK / Queen's Gardens · 휴식 포켓 · 목재, 덩굴, 잎

- 관찰: 큰 교차 줄기 뒤 좁은 공간에 벤치가 놓인다.
- 전경과 배경: 전경의 긴 선이 중앙을 나누지만 기능점은 틈으로 보인다.
- 조명: 약한 뒤쪽 빛만 남겨 작은 포켓을 드러낸다.
- 제작 패턴: P02, P10 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/4b/Screenshot_HK_Queen%27s_Gardens_05.png/800px-Screenshot_HK_Queen%27s_Gardens_05.png)

### HK-QG-06 식생과 유적이 만나는 길

[이미지 보기](images/hk-qg-06.png) · HK / Queen's Gardens · 지역 경계 · 잎, 석재, 금속

- 관찰: 큰 잎 군집에서 오른쪽 유적 건축으로 재질이 바뀐다.
- 전경과 배경: 하단 검은 풀과 중앙 잎, 뒤 밝은 초록 면이 분리된다.
- 조명: 흰 등불이 재질 전환 부근의 주목점이 된다.
- 제작 패턴: P03, P09, P12 — 중경과 원경의 다른 대비 / 지역 문턱과 문양 입구 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B11, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Queen%27s_Gardens_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/17/Screenshot_HK_Queen%27s_Gardens_06.png/800px-Screenshot_HK_Queen%27s_Gardens_06.png)

### HK-FCY-02 산성 웅덩이 위 작은 섬

[이미지 보기](images/hk-fcy-02.png) · HK / Fog Canyon · 위험 구간 · 액체, 유기체, 석재

- 관찰: 밝은 수면 위 짧은 중앙 발판과 오른쪽 턱이 있다.
- 전경과 배경: 검은 지형 코어와 둥근 뒤 식물이 다른 깊이를 만든다.
- 조명: 분홍 후광과 황록 수면이 서로 다른 범위로 빛난다.
- 제작 패턴: P05, P07, P13 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 대기광과 입자의 깊이
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c3/Screenshot_HK_Fog_Canyon_02.png/800px-Screenshot_HK_Fog_Canyon_02.png)

### HK-FCY-03 가시 뿌리와 푸른 수면

[이미지 보기](images/hk-fcy-03.png) · HK / Fog Canyon · 위험 구간 · 뿌리, 가시, 액체

- 관찰: 큰 뿌리의 아래 가시와 평평한 수면 사이 틈이 열린다.
- 전경과 배경: 앞쪽 검은 낮은 실루엣과 뒤의 흐린 둥근 입자가 겹친다.
- 조명: 밝은 수평 수면과 분홍 보라색 산란광을 분리한다.
- 제작 패턴: P02, P07, P13 — 근접 전경과 중앙 시야 여백 / 안전면과 위험면의 다른 형태 / 대기광과 입자의 깊이
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B02, B09, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9b/Screenshot_HK_Fog_Canyon_03.png/800px-Screenshot_HK_Fog_Canyon_03.png)

### HK-FCY-04 초록 정원과 층진 발판

[이미지 보기](images/hk-fcy-04.png) · HK / Fog Canyon · 지역 경계 · 잎, 석재, 금속

- 관찰: 계단처럼 이어지는 유적 발판 주변에 큰 식물이 놓인다.
- 전경과 배경: 앞쪽 검은 식물과 뒤의 넓은 잎 면이 크기로 나뉜다.
- 조명: 초록 지역광에 작고 흰 발광점이 흩어진다.
- 제작 패턴: P03, P05, P09 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8f/Screenshot_HK_Fog_Canyon_04.png/800px-Screenshot_HK_Fog_Canyon_04.png)

### HK-FCY-05 밝은 안개 속 중앙 건물

[이미지 보기](images/hk-fcy-05.png) · HK / Fog Canyon · 랜드마크 · 석재, 유기체, 식생

- 관찰: 커다란 문 하나를 낮은 식생과 주변 기둥이 둘러싼다.
- 전경과 배경: 앞의 검은 풀과 중앙 문, 뒤 흐린 큰 형태가 겹친다.
- 조명: 강한 분홍 흰 안개 앞에 건물 윤곽이 어둡게 남는다.
- 제작 패턴: P04, P13, P16 — 목표에 모이는 빛 / 대기광과 입자의 깊이 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B15, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/ec/Screenshot_HK_Fog_Canyon_05.png/800px-Screenshot_HK_Fog_Canyon_05.png)

### HK-FCY-06 발광 용기와 실내 통로

[이미지 보기](images/hk-fcy-06.png) · HK / Fog Canyon · 장치 공간 · 유리, 금속, 액체

- 관찰: 높이가 다른 실내 통로 뒤에 큰 수직 용기들이 있다.
- 전경과 배경: 검은 상부 코어와 낮은 대비의 뒤 실내 구조가 분리된다.
- 조명: 녹색 용기 면과 약한 실내 대기광이 겹친다.
- 제작 패턴: P03, P06, P12 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 재질의 군집과 빈 구간
- 적용 후보: 고대 장치 구역 · 자산 명세 B03, B07, B08, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Fog_Canyon_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9f/Screenshot_HK_Fog_Canyon_06.png/800px-Screenshot_HK_Fog_Canyon_06.png)

### HK-RW-01 물가 위 세로 빛

[이미지 보기](images/hk-rw-01.png) · HK / Royal Waterways · 수평 통로 · 물, 석재, 금속

- 관찰: 낮은 지면과 작은 중앙 구조 위로 긴 빛이 내려온다.
- 전경과 배경: 앞의 검은 뿌리와 뒤 푸른 관이 층을 이룬다.
- 조명: 천장 틈의 좁은 빛을 중앙에 집중한다.
- 제작 패턴: P02, P04, P13 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B02, B04, B05, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/90/Screenshot_HK_Royal_Waterways_01.png/800px-Screenshot_HK_Royal_Waterways_01.png)

### HK-RW-02 철문 뒤 푸른 통로

[이미지 보기](images/hk-rw-02.png) · HK / Royal Waterways · 지역 경계 · 금속, 석재

- 관찰: 길고 낮은 바닥 뒤에 세 개의 철문 윤곽이 반복된다.
- 전경과 배경: 앞쪽 검은 기둥과 뒤 밝은 청록 면이 분리된다.
- 조명: 작은 흰 광점과 넓은 푸른 후경광이 공존한다.
- 제작 패턴: P03, P09, P12 — 중경과 원경의 다른 대비 / 지역 문턱과 문양 입구 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B11, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/36/Screenshot_HK_Royal_Waterways_02.png/800px-Screenshot_HK_Royal_Waterways_02.png)

### HK-RW-03 목재 발판과 가시 천장

[이미지 보기](images/hk-rw-03.png) · HK / Royal Waterways · 위험 구간 · 목재, 가시, 석재

- 관찰: 짧은 발판들이 높은 가시 천장 아래 흩어진다.
- 전경과 배경: 굵은 검은 전경과 뒤 회색 안개가 대비된다.
- 조명: 낮은 회색 배경빛으로 발판과 가시 외곽을 읽힌다.
- 제작 패턴: P05, P06, P07 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B07, B08, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1b/Screenshot_HK_Royal_Waterways_03.png/800px-Screenshot_HK_Royal_Waterways_03.png)

### HK-RW-04 물가의 돔 구조물

[이미지 보기](images/hk-rw-04.png) · HK / Royal Waterways · 랜드마크 · 금속, 석재, 물

- 관찰: 중앙 둥근 건물과 양옆 높은 장식이 큰 형태를 만든다.
- 전경과 배경: 앞 검은 보행면과 뒤 회색 구조의 크기가 다르다.
- 조명: 두 흰 등불이 중앙 구조물의 위치를 표시한다.
- 제작 패턴: P04, P16, P17 — 목표에 모이는 빛 / 방마다 하나의 큰 기억점 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9d/Screenshot_HK_Royal_Waterways_04.png/800px-Screenshot_HK_Royal_Waterways_04.png)

### HK-RW-05 어두운 통로 안 작은 벤치

[이미지 보기](images/hk-rw-05.png) · HK / Royal Waterways · 휴식 포켓 · 금속, 석재

- 관찰: 큰 관 옆 작은 벤치가 낮은 지면에 놓인다.
- 전경과 배경: 앞 검은 코어 사이로 안쪽 푸른 작은 공간이 열린다.
- 조명: 벤치 양옆의 작은 청색 빛이 안전한 포켓을 드러낸다.
- 제작 패턴: P04, P10 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1a/Screenshot_HK_Royal_Waterways_05.png/800px-Screenshot_HK_Royal_Waterways_05.png)

### HK-RW-06 깊은 물 위 줄기 실루엣

[이미지 보기](images/hk-rw-06.png) · HK / Royal Waterways · 수평 통로 · 물, 뿌리

- 관찰: 매우 낮은 수면 위에 길고 어두운 줄기들이 겹친다.
- 전경과 배경: 앞의 검은 세로줄과 뒤의 희미한 녹색 물빛이 분리된다.
- 조명: 수면의 가는 밝은 선과 아래 넓은 번짐이 다르다.
- 제작 패턴: P02, P03, P13 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Royal_Waterways_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/83/Screenshot_HK_Royal_Waterways_06.png/800px-Screenshot_HK_Royal_Waterways_06.png)

### HK-AB-01 큰 껍질 문과 둥근 바닥

[이미지 보기](images/hk-ab-01.png) · HK / Ancient Basin · 지역 경계 · 껍질, 석재

- 관찰: 화면을 차지하는 껍질 문 아래 낮은 보행면이 이어진다.
- 전경과 배경: 앞의 가는 검은 장식이 중앙 문과 겹친다.
- 조명: 낮은 회색 빛이 문양의 홈과 외곽만 드러낸다.
- 제작 패턴: P09, P12, P16 — 지역 문턱과 문양 입구 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B11, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Ancient_Basin_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3f/Screenshot_HK_Ancient_Basin_01.png/800px-Screenshot_HK_Ancient_Basin_01.png)

### HK-AB-02 깊은 구덩이의 작은 빛

[이미지 보기](images/hk-ab-02.png) · HK / Ancient Basin · 목표 노출 · 뿌리, 껍질, 석재

- 관찰: 아래 작은 밝은 지점 위로 사선 줄기가 모인다.
- 전경과 배경: 위의 어두운 벽과 아래 밝은 작은 공간이 대비된다.
- 조명: 흰 청색 국소빛이 깊은 틈의 중심을 표시한다.
- 제작 패턴: P04, P05, P08 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 보상의 선노출과 우회 경로
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B06, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Ancient_Basin_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8c/Screenshot_HK_Ancient_Basin_02.png/800px-Screenshot_HK_Ancient_Basin_02.png)

### HK-AB-03 희미한 실내와 중앙 등불

[이미지 보기](images/hk-ab-03.png) · HK / Ancient Basin · 복층 공간 · 석재, 금속

- 관찰: 기둥과 작은 발판 사이에 세로로 큰 빈 공간이 남는다.
- 전경과 배경: 앞의 검은 덩굴과 뒤 회색 구조를 분리한다.
- 조명: 중앙 흰 등불 하나가 주변 넓은 어둠과 대비된다.
- 제작 패턴: P03, P04, P05 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B04, B05, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Ancient_Basin_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/95/Screenshot_HK_Ancient_Basin_03.png/800px-Screenshot_HK_Ancient_Basin_03.png)

### HK-AB-04 위아래 흰 가시 사이

[이미지 보기](images/hk-ab-04.png) · HK / Ancient Basin · 위험 구간 · 가시, 석재

- 관찰: 좁은 통로 양쪽을 밝고 날카로운 가시가 감싼다.
- 전경과 배경: 검은 긴 뿌리와 뒤 회색 벽 사이에 가시가 선명하다.
- 조명: 흰 가시 끝이 낮은 채도 배경보다 먼저 보인다.
- 제작 패턴: P07, P18 — 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Ancient_Basin_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9f/Screenshot_HK_Ancient_Basin_04.png/800px-Screenshot_HK_Ancient_Basin_04.png)

### HK-AB-05 암흑 속 작은 붉은 방

[이미지 보기](images/hk-ab-05.png) · HK / Ancient Basin · 전투 공간 · 유기체, 석재

- 관찰: 대부분 검은 화면 안 작은 적과 보행면만 보인다.
- 전경과 배경: 큰 검은 코어가 작은 플레이 공간을 둘러싼다.
- 조명: 주황 적의 신호가 주변보다 훨씬 밝다.
- 제작 패턴: P04, P15, P20 — 목표에 모이는 빛 / 적 실루엣과 공격 방향 / 시야 제한과 집중 연출
- 적용 후보: 전투방, 보스방 · 자산 명세 B04, B05, B16, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Ancient_Basin_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/47/Screenshot_HK_Ancient_Basin_05.png/800px-Screenshot_HK_Ancient_Basin_05.png)

### HK-AY-01 거대 관 옆 매달린 길

[이미지 보기](images/hk-ay-01.png) · HK / The Abyss · 수직 이동 · 석재, 껍질

- 관찰: 오른쪽 큰 관 옆으로 짧은 발판이 다른 높이에 놓인다.
- 전경과 배경: 앞 검은 줄기와 뒤의 흐린 원형 벽무늬가 겹친다.
- 조명: 약한 회색빛으로 발판과 뒤 거대 형체를 구별한다.
- 제작 패턴: P03, P05 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c9/Screenshot_HK_Abyss_01.png/800px-Screenshot_HK_Abyss_01.png)

### HK-AY-02 가시로 둘러싼 작은 착지면

[이미지 보기](images/hk-ay-02.png) · HK / The Abyss · 위험 구간 · 가시, 석재

- 관찰: 작은 돌 발판 위와 아래에 흰 가시가 있다.
- 전경과 배경: 발판 속 검정과 뒤 큰 돌 표면의 대비가 다르다.
- 조명: 가시 끝만 밝아 실제 안전면이 짧게 보인다.
- 제작 패턴: P05, P07 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/66/Screenshot_HK_Abyss_02.png/800px-Screenshot_HK_Abyss_02.png)

### HK-AY-03 그림자 형체와 넓은 바닥

[이미지 보기](images/hk-ay-03.png) · HK / The Abyss · 전투 공간 · 뼈, 석재

- 관찰: 높이가 다른 작은 발판 아래 낮은 바닥이 열린다.
- 전경과 배경: 앞의 뼈무더기와 뒤 큰 둥근 면이 크기로 분리된다.
- 조명: 낮은 회색 대기광 속 밝은 눈 같은 작은 신호가 보인다.
- 제작 패턴: P03, P11, P15 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/36/Screenshot_HK_Abyss_03.png/800px-Screenshot_HK_Abyss_03.png)

### HK-AY-04 세 기둥 사이의 깊이

[이미지 보기](images/hk-ay-04.png) · HK / The Abyss · 수직 이동 · 뼈, 석재, 뿌리

- 관찰: 높이가 다른 좁은 기둥이 중앙 틈을 나눈다.
- 전경과 배경: 앞 검은 줄기와 뒤의 부드러운 세로 면이 겹친다.
- 조명: 뒤의 희미한 회색빛이 기둥 외곽을 드러낸다.
- 제작 패턴: P02, P05, P07 — 근접 전경과 중앙 시야 여백 / 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B02, B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/25/Screenshot_HK_Abyss_04.png/800px-Screenshot_HK_Abyss_04.png)

### HK-AY-05 탑에서 뻗는 큰 광선

[이미지 보기](images/hk-ay-05.png) · HK / The Abyss · 조명 상세 · 석재, 금속

- 관찰: 큰 탑의 높은 지점에서 넓은 사선 빛이 뻗는다.
- 전경과 배경: 검은 탑이 밝은 광선 앞의 큰 실루엣으로 남는다.
- 조명: 작은 광원 입구에서 멀리 갈수록 넓어지는 강한 빛이다.
- 제작 패턴: P04, P16, P18 — 목표에 모이는 빛 / 방마다 하나의 큰 기억점 / 밝은 지역에서의 대비 반전
- 적용 후보: 문양의 성소, 유물 획득 지점 · 자산 명세 B04, B05, B17, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6e/Screenshot_HK_Abyss_05.png/800px-Screenshot_HK_Abyss_05.png)

### HK-AY-06 작은 방 안 큰 백색 광원

[이미지 보기](images/hk-ay-06.png) · HK / The Abyss · 목표 노출 · 금속, 석재

- 관찰: 좁은 포켓을 밝은 수직 타원 구조가 거의 채운다.
- 전경과 배경: 검은 바깥 지형과 작은 안쪽 기능점이 극단적으로 나뉜다.
- 조명: 광원 중심은 희고 주변 후광은 부드럽다.
- 제작 패턴: P04, P08, P18 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 밝은 지역에서의 대비 반전
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B10, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Abyss_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b3/Screenshot_HK_Abyss_06.png/800px-Screenshot_HK_Abyss_06.png)

### HK-KE-01 밝은 뿌리 옆 발판 사다리

[이미지 보기](images/hk-ke-01.png) · HK / Kingdom's Edge · 수직 이동 · 뿌리, 석재

- 관찰: 짧은 발판들이 큰 세로 관과 밝은 뿌리 사이에 흩어진다.
- 전경과 배경: 앞의 작은 검은 발판과 뒤 큰 곡면의 크기가 다르다.
- 조명: 밝은 흰 뿌리와 낮은 채도 대기광을 구별한다.
- 제작 패턴: P03, P05, P18 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B06, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3e/Screenshot_HK_Kingdom%27s_Edge_01.png/800px-Screenshot_HK_Kingdom%27s_Edge_01.png)

### HK-KE-02 밝은 배경과 검은 앞 가시

[이미지 보기](images/hk-ke-02.png) · HK / Kingdom's Edge · 위험 구간 · 뼈, 가시, 석재

- 관찰: 넓은 바닥의 앞·뒤에 서로 다른 크기의 날카로운 형체가 있다.
- 전경과 배경: 아래의 검은 앞 가시와 뒤의 희고 큰 뿌리가 대비된다.
- 조명: 밝은 원경 위 플레이 경계는 어둡게 읽힌다.
- 제작 패턴: P02, P07, P18 — 근접 전경과 중앙 시야 여백 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B02, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/14/Screenshot_HK_Kingdom%27s_Edge_02.png/800px-Screenshot_HK_Kingdom%27s_Edge_02.png)

### HK-KE-03 거대한 뒤 관과 좁은 발판

[이미지 보기](images/hk-ke-03.png) · HK / Kingdom's Edge · 수직 이동 · 석재, 껍질

- 관찰: 두 큰 뒤 구조 사이로 작은 발판들이 올라간다.
- 전경과 배경: 배경 구조는 크고 부드러우며 발판은 작고 선명하다.
- 조명: 흰 뿌리의 넓은 빛이 다음 발판의 외곽을 드러낸다.
- 제작 패턴: P03, P05 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/20/Screenshot_HK_Kingdom%27s_Edge_03.png/800px-Screenshot_HK_Kingdom%27s_Edge_03.png)

### HK-KE-04 거대한 유해의 입구

[이미지 보기](images/hk-ke-04.png) · HK / Kingdom's Edge · 랜드마크 · 뼈, 껍질

- 관찰: 큰 머리 같은 유해가 작은 문보다 훨씬 크게 배치된다.
- 전경과 배경: 앞 검은 돌기 사이에 거대한 중경 실루엣이 놓인다.
- 조명: 매우 낮은 청색 빛으로 큰 외곽만 드러낸다.
- 제작 패턴: P03, P09, P16 — 중경과 원경의 다른 대비 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c4/Screenshot_HK_Kingdom%27s_Edge_04.png/800px-Screenshot_HK_Kingdom%27s_Edge_04.png)

### HK-KE-05 낮은 가시 틈과 검은 천장

[이미지 보기](images/hk-ke-05.png) · HK / Kingdom's Edge · 위험 구간 · 가시, 석재

- 관찰: 양옆 안전면 사이의 가시 틈 위로 큰 천장이 내려온다.
- 전경과 배경: 앞 검은 돌기와 뒤 둥근 벽이 통로를 감싼다.
- 조명: 중앙의 약한 회색 여백이 통과 공간을 드러낸다.
- 제작 패턴: P02, P07 — 근접 전경과 중앙 시야 여백 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B02, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/ee/Screenshot_HK_Kingdom%27s_Edge_05.png/800px-Screenshot_HK_Kingdom%27s_Edge_05.png)

### HK-KE-06 낡은 천막 아래 휴식

[이미지 보기](images/hk-ke-06.png) · HK / Kingdom's Edge · 휴식 포켓 · 천, 목재, 뼈

- 관찰: 낮은 바닥 위 커다란 천막이 작은 휴식점을 감싼다.
- 전경과 배경: 앞의 검은 지지대와 뒤 열린 밝은 공간이 겹친다.
- 조명: 넓고 약한 바깥빛과 작은 내부 밝기가 대비된다.
- 제작 패턴: P02, P10, P16 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Kingdom%27s_Edge_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/de/Screenshot_HK_Kingdom%27s_Edge_06.png/800px-Screenshot_HK_Kingdom%27s_Edge_06.png)

### HK-HI-01 벌집 기하와 넓은 바닥

[이미지 보기](images/hk-hi-01.png) · HK / The Hive · 수평 통로 · 밀랍, 석재

- 관찰: 육각 벽면과 규칙적인 큰 기둥이 수평 공간을 채운다.
- 전경과 배경: 앞 검은 코어와 뒤 황금빛 벽 패턴이 분리된다.
- 조명: 넓은 금색 지역광에 작은 밝은 결정 모서리가 있다.
- 제작 패턴: P12, P18 — 재질의 군집과 빈 구간 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로 · 자산 명세 B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/63/Screenshot_HK_Hive_01.png/800px-Screenshot_HK_Hive_01.png)

### HK-HI-02 중앙 고치와 황금 안개

[이미지 보기](images/hk-hi-02.png) · HK / The Hive · 랜드마크 · 밀랍, 유기체

- 관찰: 높은 중앙 물체와 바닥의 낮은 덩어리가 수직 축을 만든다.
- 전경과 배경: 검은 둘레와 뒤 밝은 육각 벽이 대비된다.
- 조명: 백색에 가까운 중앙 빛과 넓은 황금빛 산란이 겹친다.
- 제작 패턴: P04, P13, P16 — 목표에 모이는 빛 / 대기광과 입자의 깊이 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B15, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8e/Screenshot_HK_Hive_02.png/800px-Screenshot_HK_Hive_02.png)

### HK-HI-03 밝은 벽 앞의 작은 발판

[이미지 보기](images/hk-hi-03.png) · HK / The Hive · 수직 이동 · 밀랍, 석재

- 관찰: 여러 작은 발판과 비행 적이 밝은 육각 배경 앞에 놓인다.
- 전경과 배경: 앞의 어두운 발판과 뒤의 매우 밝은 반복벽이 분리된다.
- 조명: 밝은 지역에서 작은 어두운 실루엣이 이동 경계가 된다.
- 제작 패턴: P05, P15, P18 — 다음 착지면이 보이는 수직 이동 / 적 실루엣과 공격 방향 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B06, B16, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fd/Screenshot_HK_Hive_03.png/800px-Screenshot_HK_Hive_03.png)

### HK-HI-04 큰 기둥 사이 비행 공간

[이미지 보기](images/hk-hi-04.png) · HK / The Hive · 전투 공간 · 밀랍, 석재

- 관찰: 좁은 발판과 크기가 다른 비행체가 세로 틈을 채운다.
- 전경과 배경: 앞 검은 큰 기둥과 뒤 흐린 금빛 면이 겹친다.
- 조명: 적의 밝은 얼굴과 뒤의 넓은 황금빛은 범위가 다르다.
- 제작 패턴: P05, P11, P15 — 다음 착지면이 보이는 수직 이동 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B06, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3e/Screenshot_HK_Hive_04.png/800px-Screenshot_HK_Hive_04.png)

### HK-HI-05 밀랍 천장의 긴 실루엣

[이미지 보기](images/hk-hi-05.png) · HK / The Hive · 수평 통로 · 밀랍

- 관찰: 종유석 같은 긴 밀랍이 상단을 불규칙하게 가린다.
- 전경과 배경: 검은 큰 천장 덩어리 아래 밝은 가는 끝들이 내려온다.
- 조명: 아래 금빛 여백과 어두운 천장이 강하게 대비된다.
- 제작 패턴: P01, P02, P12 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B01, B02, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/14/Screenshot_HK_Hive_05.png/800px-Screenshot_HK_Hive_05.png)

### HK-HI-06 빛나는 뒤 형체와 긴 전투면

[이미지 보기](images/hk-hi-06.png) · HK / The Hive · 전투 공간 · 밀랍, 유기체

- 관찰: 평평한 바닥 뒤에 커다란 밝은 형체가 놓인다.
- 전경과 배경: 앞 보행면은 어둡고 뒤 형체는 크고 흐리다.
- 조명: 따뜻한 전체빛 속에서 앞쪽 공격 공간은 단순하다.
- 제작 패턴: P03, P11, P18 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 밝은 지역에서의 대비 반전
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B13, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Hive_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a4/Screenshot_HK_Hive_06.png/800px-Screenshot_HK_Hive_06.png)

### HK-RG-01 어둠 속 큰 수직 창

[이미지 보기](images/hk-rg-01.png) · HK / Resting Grounds · 목표 노출 · 석재, 금속

- 관찰: 큰 밝은 수직 형태 아래 작은 지면이 모인다.
- 전경과 배경: 앞 검은 기둥과 중앙 창, 뒤 안개가 층을 만든다.
- 조명: 좁고 긴 흰 빛이 주변 어둠의 중심이다.
- 제작 패턴: P04, P08, P16 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B10, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/ae/Screenshot_HK_Resting_Grounds_01.png/800px-Screenshot_HK_Resting_Grounds_01.png)

### HK-RG-02 묘석과 떠 있는 짧은 발판

[이미지 보기](images/hk-rg-02.png) · HK / Resting Grounds · 복층 공간 · 석재, 금속

- 관찰: 큰 묘석과 작은 발판이 높이 차를 보여준다.
- 전경과 배경: 앞 검은 풀과 뒤 푸른 둥근 형체가 분리된다.
- 조명: 큰 청색 면 위 작은 흰 입자가 떠 있다.
- 제작 패턴: P03, P05, P13 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B06, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a5/Screenshot_HK_Resting_Grounds_02.png/800px-Screenshot_HK_Resting_Grounds_02.png)

### HK-RG-03 낮고 어두운 묘지 통로

[이미지 보기](images/hk-rg-03.png) · HK / Resting Grounds · 수평 통로 · 석재, 뼈

- 관찰: 거의 검은 상부 코어 아래 좁은 통로가 이어진다.
- 전경과 배경: 가까운 검은 묘석과 뒤 보랏빛 무늬가 겹친다.
- 조명: 매우 낮은 보라색 대기광으로 길의 실루엣을 읽힌다.
- 제작 패턴: P01, P02, P20 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 시야 제한과 집중 연출
- 적용 후보: 중앙 통로 · 자산 명세 B01, B02, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e6/Screenshot_HK_Resting_Grounds_03.png/800px-Screenshot_HK_Resting_Grounds_03.png)

### HK-RG-04 작은 따뜻한 방의 인물

[이미지 보기](images/hk-rg-04.png) · HK / Resting Grounds · 휴식 포켓 · 석재, 유기체

- 관찰: 큰 검은 공간 안 둥근 작은 방과 인물이 있다.
- 전경과 배경: 밝은 안쪽 방을 검은 코어가 둘러싼다.
- 조명: 국소 주황색 후광이 기능점과 주변 재질을 함께 드러낸다.
- 제작 패턴: P04, P10, P15 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 적 실루엣과 공격 방향
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/dc/Screenshot_HK_Resting_Grounds_04.png/800px-Screenshot_HK_Resting_Grounds_04.png)

### HK-RG-05 긴 회랑의 작은 무덤들

[이미지 보기](images/hk-rg-05.png) · HK / Resting Grounds · 수평 통로 · 석재, 금속

- 관찰: 작은 무덤과 가는 기둥이 평평한 바닥에 반복된다.
- 전경과 배경: 하단 검은 실루엣과 뒤 청색 무덤 무늬가 나뉜다.
- 조명: 작은 흰 입자와 낮은 대비의 푸른 지역광이 겹친다.
- 제작 패턴: P03, P12, P13 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B03, B14, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/96/Screenshot_HK_Resting_Grounds_05.png/800px-Screenshot_HK_Resting_Grounds_05.png)

### HK-RG-06 밝은 세로 틈의 유령 형체

[이미지 보기](images/hk-rg-06.png) · HK / Resting Grounds · 시네마틱 효과 · 석재, 유기체

- 관찰: 중앙 세로 빛 속 형체가 주변 지형보다 크게 드러난다.
- 전경과 배경: 양옆 검은 지형과 뒤의 부드러운 밝은 면이 대비된다.
- 조명: 흰 청색 중심과 넓은 후광이 시선을 모은다.
- 제작 패턴: P04, P13, P20 — 목표에 모이는 빛 / 대기광과 입자의 깊이 / 시야 제한과 집중 연출
- 적용 후보: 유물 획득 연출, 보스 등장 연출 · 자산 명세 B04, B05, B15, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Resting_Grounds_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9d/Screenshot_HK_Resting_Grounds_06.png/800px-Screenshot_HK_Resting_Grounds_06.png)

### HK-HC-01 절벽 끝의 작은 등불

[이미지 보기](images/hk-hc-01.png) · HK / Howling Cliffs · 지역 경계 · 석재, 금속

- 관찰: 왼쪽 짧은 지면이 오른쪽 넓은 빈 공간으로 끝난다.
- 전경과 배경: 앞 돌 테두리와 뒤 흐린 큰 곡면이 분리된다.
- 조명: 작은 흰 등불이 절벽 경계를 표시한다.
- 제작 패턴: P04, P05, P09 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/80/Screenshot_HK_Howling_Cliffs_01.png/800px-Screenshot_HK_Howling_Cliffs_01.png)

### HK-HC-02 고리처럼 둘러싼 돌 통로

[이미지 보기](images/hk-hc-02.png) · HK / Howling Cliffs · 복층 공간 · 석재

- 관찰: 큰 둥근 지형 속 빈 공간과 작은 발판이 겹친다.
- 전경과 배경: 검은 지형 코어와 푸른 뒤 바위 면이 나뉜다.
- 조명: 낮은 청색빛이 상면과 통과 공간을 드러낸다.
- 제작 패턴: P01, P05, P12 — 검은 지형 속과 읽히는 테두리 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B01, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/4f/Screenshot_HK_Howling_Cliffs_02.png/800px-Screenshot_HK_Howling_Cliffs_02.png)

### HK-HC-03 큰 잔해와 안개 낀 바깥

[이미지 보기](images/hk-hc-03.png) · HK / Howling Cliffs · 랜드마크 · 뼈, 껍질, 석재

- 관찰: 낮은 바닥 위 큰 잔해가 먼 공간을 향해 누워 있다.
- 전경과 배경: 앞 검은 선과 뒤 흐린 큰 구조가 크기로 분리된다.
- 조명: 차가운 회색 안개가 먼 윤곽의 대비를 낮춘다.
- 제작 패턴: P03, P13, P16 — 중경과 원경의 다른 대비 / 대기광과 입자의 깊이 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B15, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/ec/Screenshot_HK_Howling_Cliffs_03.png/800px-Screenshot_HK_Howling_Cliffs_03.png)

### HK-HC-04 천장 틈 아래 단일 빛

[이미지 보기](images/hk-hc-04.png) · HK / Howling Cliffs · 수평 통로 · 석재

- 관찰: 평평한 바닥과 낮은 천장 사이 중앙 여백이 있다.
- 전경과 배경: 하단 검은 풀과 위 검은 코어가 공간을 감싼다.
- 조명: 좁은 천장 틈의 흰 청색 광막이 중앙으로 내려온다.
- 제작 패턴: P01, P02, P04 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛
- 적용 후보: 중앙 통로 · 자산 명세 B01, B02, B04, B05
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/eb/Screenshot_HK_Howling_Cliffs_04.png/800px-Screenshot_HK_Howling_Cliffs_04.png)

### HK-HC-05 푸른 나비와 작은 발판

[이미지 보기](images/hk-hc-05.png) · HK / Howling Cliffs · 목표 노출 · 석재, 식생

- 관찰: 작은 발판 옆 밝은 나비 무리가 방향을 만든다.
- 전경과 배경: 앞의 검은 나비와 뒤 푸른 형체가 크기·밝기로 나뉜다.
- 조명: 작은 발광 나비들이 한쪽 길을 강조한다.
- 제작 패턴: P04, P05, P08 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 보상의 선노출과 우회 경로
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B06, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/bf/Screenshot_HK_Howling_Cliffs_05.png/800px-Screenshot_HK_Howling_Cliffs_05.png)

### HK-HC-06 발광 나비가 채운 세로 공간

[이미지 보기](images/hk-hc-06.png) · HK / Howling Cliffs · 수직 이동 · 석재, 식생

- 관찰: 발판 여러 개 사이에 큰 크기 차의 나비들이 떠 있다.
- 전경과 배경: 가까운 큰 어두운 나비와 뒤 작은 빛을 구별한다.
- 조명: 푸른 발광점은 배경과 발판의 깊이를 나눈다.
- 제작 패턴: P05, P08, P13 — 다음 착지면이 보이는 수직 이동 / 보상의 선노출과 우회 경로 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B06, B10, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_Howling_Cliffs_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9a/Screenshot_HK_Howling_Cliffs_06.png/800px-Screenshot_HK_Howling_Cliffs_06.png)

### HK-WP-01 밝은 창 앞의 왕좌

[이미지 보기](images/hk-wp-01.png) · HK / White Palace · 랜드마크 · 석재, 금속, 유리

- 관찰: 중앙 왕좌와 큰 아치가 단순한 대칭 축을 만든다.
- 전경과 배경: 어두운 중앙 물체와 밝은 뒤 창이 대비된다.
- 조명: 백색 지역광 속에도 왕좌의 홈과 윤곽을 남긴다.
- 제작 패턴: P04, P16, P18 — 목표에 모이는 빛 / 방마다 하나의 큰 기억점 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B17, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fb/Screenshot_HK_White_Palace_01.png/800px-Screenshot_HK_White_Palace_01.png)

### HK-WP-02 흰 식생과 좁은 길

[이미지 보기](images/hk-wp-02.png) · HK / White Palace · 수평 통로 · 석재, 금속, 식생

- 관찰: 낮은 길 위에 흰 식물과 둥근 공중 형체가 있다.
- 전경과 배경: 앞 어두운 가림과 뒤의 흰 식생이 서로 다른 깊이다.
- 조명: 밝은 지역에서 앞의 어두운 테두리로 길을 읽힌다.
- 제작 패턴: P01, P12, P18 — 검은 지형 속과 읽히는 테두리 / 재질의 군집과 빈 구간 / 밝은 지역에서의 대비 반전
- 적용 후보: 중앙 통로 · 자산 명세 B01, B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d1/Screenshot_HK_White_Palace_02.png/800px-Screenshot_HK_White_Palace_02.png)

### HK-WP-03 큰 흰 아치 아래 제단

[이미지 보기](images/hk-wp-03.png) · HK / White Palace · 목표 노출 · 석재, 금속, 유리

- 관찰: 검은 상부 코어 아래 밝은 중앙 제단과 발판이 놓인다.
- 전경과 배경: 검은 지형 내부와 뒤 흰 창을 명확하게 나눈다.
- 조명: 넓은 백색광 가운데 작은 구조의 외곽을 유지한다.
- 제작 패턴: P01, P04, P18 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 밝은 지역에서의 대비 반전
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B01, B04, B05, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/ac/Screenshot_HK_White_Palace_03.png/800px-Screenshot_HK_White_Palace_03.png)

### HK-WP-04 톱니 원판과 검은 천장

[이미지 보기](images/hk-wp-04.png) · HK / White Palace · 위험 구간 · 금속, 석재, 식생

- 관찰: 큰 원형 위험 형체와 낮은 안전면이 가까이 놓인다.
- 전경과 배경: 위의 검은 코어와 아래 밝은 배경이 반대 명암을 만든다.
- 조명: 밝은 원판 테두리를 주변 식생과 다른 형태로 읽힌다.
- 제작 패턴: P06, P07, P18 — 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B07, B08, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/46/Screenshot_HK_White_Palace_04.png/800px-Screenshot_HK_White_Palace_04.png)

### HK-WP-05 밝은 정원 옆 낙하 경계

[이미지 보기](images/hk-wp-05.png) · HK / White Palace · 위험 구간 · 석재, 식생, 금속

- 관찰: 왼쪽 긴 길이 끝나고 오른쪽으로 깊은 빈 공간이 열린다.
- 전경과 배경: 아래 검은 지형 속과 뒤의 흰 식생 군집이 분리된다.
- 조명: 흰 후경광 앞 어두운 상면을 착지 기준으로 남긴다.
- 제작 패턴: P05, P07, P18 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/47/Screenshot_HK_White_Palace_05.png/800px-Screenshot_HK_White_Palace_05.png)

### HK-WP-06 원판 사이 작은 발판

[이미지 보기](images/hk-wp-06.png) · HK / White Palace · 장치 공간 · 금속, 석재, 유리

- 관찰: 여러 원형 형체 사이에 짧은 발판들이 놓인다.
- 전경과 배경: 크고 흐린 뒤 원판과 선명한 앞 원판을 구분한다.
- 조명: 백색 윤곽과 어두운 안전면이 번갈아 보인다.
- 제작 패턴: P05, P06, P07 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역 · 자산 명세 B06, B07, B08, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_HK_White_Palace_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d5/Screenshot_HK_White_Palace_06.png/800px-Screenshot_HK_White_Palace_06.png)

### SS-MG-01 무성한 바닥과 둥근 잔해

[이미지 보기](images/ss-mg-01.png) · SS / Moss Grotto · 랜드마크 · 이끼, 석재, 금속

- 관찰: 초록 이끼 바닥 위 큰 둥근 잔해가 낮게 놓인다.
- 전경과 배경: 앞 검은 큰 잎과 뒤 흐린 이끼 언덕이 나뉜다.
- 조명: 위에서 내려오는 황록빛이 바닥과 잔해의 일부만 비춘다.
- 제작 패턴: P02, P03, P12, P16 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B03, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a2/Screenshot_SS_Moss_Grotto_01.png/800px-Screenshot_SS_Moss_Grotto_01.png)

### SS-MG-02 이끼 언덕과 열린 중앙

[이미지 보기](images/ss-mg-02.png) · SS / Moss Grotto · 수평 통로 · 이끼, 석재, 잎

- 관찰: 낮은 지면의 작은 이끼 벌레 둘 뒤로 큰 둥근 언덕이 겹친다.
- 전경과 배경: 양옆의 큰 검은 잎과 뒤의 부드러운 초록 덩어리가 크기로 나뉜다.
- 조명: 넓은 황록색 빛이 중앙 위쪽 여백에 모인다.
- 제작 패턴: P02, P03, P12, P15, P17 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 적 실루엣과 공격 방향 / 비대칭 공간의 무게 배분
- 적용 후보: 이끼 통로 · 자산 명세 B02, B03, B14, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5c/Screenshot_SS_Moss_Grotto_02.png/800px-Screenshot_SS_Moss_Grotto_02.png)

### SS-MG-03 큰 이끼 천장과 단층 발판

[이미지 보기](images/ss-mg-03.png) · SS / Moss Grotto · 복층 공간 · 이끼, 석재, 잎

- 관찰: 왼쪽 낮은 길과 오른쪽 짧은 발판 사이 공간이 열린다.
- 전경과 배경: 큰 검은 천장 끝과 멀리 겹친 초록 덩어리가 분리된다.
- 조명: 원경의 약한 초록빛으로 발판 외곽을 읽힌다.
- 제작 패턴: P01, P05, P12 — 검은 지형 속과 읽히는 테두리 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 하강 통로 · 자산 명세 B01, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/84/Screenshot_SS_Moss_Grotto_03.png/800px-Screenshot_SS_Moss_Grotto_03.png)

### SS-MG-04 큰 잎 아래 넓은 바닥

[이미지 보기](images/ss-mg-04.png) · SS / Moss Grotto · 열린 방 · 석재, 잎, 뿌리

- 관찰: 평평한 바닥 위 중앙을 비우고 큰 잎을 상부에 모은다.
- 전경과 배경: 앞 하단 검은 풀과 중앙 큰 잎, 뒤 흐린 숲이 겹친다.
- 조명: 넓고 약한 수직 빛이 중앙 바닥으로 내려온다.
- 제작 패턴: P02, P04, P11 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 전투방의 넓은 판독 공간
- 적용 후보: 전투방, 보스방 · 자산 명세 B02, B04, B05, B13
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9b/Screenshot_SS_Moss_Grotto_04.png/800px-Screenshot_SS_Moss_Grotto_04.png)

### SS-MG-05 작은 반원 포켓

[이미지 보기](images/ss-mg-05.png) · SS / Moss Grotto · 휴식 포켓 · 이끼, 석재, 뿌리

- 관찰: 낮은 중앙 구조를 둥근 천장과 양옆 식생이 감싼다.
- 전경과 배경: 검은 외곽 안에서만 작은 보행면이 드러난다.
- 조명: 뒤의 희미한 초록빛과 작은 광점이 포켓을 읽힌다.
- 제작 패턴: P01, P04, P10 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B01, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8d/Screenshot_SS_Moss_Grotto_05.png/800px-Screenshot_SS_Moss_Grotto_05.png)

### SS-MG-06 가시 절벽 옆 높은 문

[이미지 보기](images/ss-mg-06.png) · SS / Moss Grotto · 지역 경계 · 석재, 금속, 가시

- 관찰: 높은 오른쪽 문과 왼쪽 작은 발판 사이에 가시 구덩이가 있다.
- 전경과 배경: 검은 상부 코어 아래 오른쪽 구조의 선이 선명하다.
- 조명: 낮은 푸른빛이 발판과 문 외곽을 남긴다.
- 제작 패턴: P05, P07, P09 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B06, B09, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Moss_Grotto_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e8/Screenshot_SS_Moss_Grotto_06.png/800px-Screenshot_SS_Moss_Grotto_06.png)

### SS-BB-02 이끼에 묻힌 작은 집

[이미지 보기](images/ss-bb-02.png) · SS / Bone Bottom · 랜드마크 · 이끼, 석재, 금속

- 관찰: 둥근 집이 큰 이끼 언덕 아래에 묻힌 듯 놓인다.
- 전경과 배경: 앞쪽 가는 풀과 뒤쪽 큰 둥근 지붕의 크기가 다르다.
- 조명: 작은 포자와 약한 초록 주변광을 사용한다.
- 제작 패턴: P03, P12, P16 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bone_Bottom_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c1/Screenshot_SS_Bone_Bottom_02.png/800px-Screenshot_SS_Bone_Bottom_02.png)

### SS-BB-03 매달린 종과 낮은 대기 공간

[이미지 보기](images/ss-bb-03.png) · SS / Bone Bottom · 열린 방 · 금속, 석재, 뼈

- 관찰: 양옆 발판 사이 낮은 중앙 공간 위로 종이 매달린다.
- 전경과 배경: 앞쪽 바닥은 어둡고 뒤의 둥근 껍질 군집은 흐리다.
- 조명: 좁은 사선 빛과 작은 따뜻한 광점이 겹친다.
- 제작 패턴: P03, P04, P06 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 장치 경로와 작동부의 명료함
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B04, B05, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bone_Bottom_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/54/Screenshot_SS_Bone_Bottom_03.png/800px-Screenshot_SS_Bone_Bottom_03.png)

### SS-BB-05 천막 사이 작은 인물

[이미지 보기](images/ss-bb-05.png) · SS / Bone Bottom · 휴식 포켓 · 천, 석재, 이끼

- 관찰: 낮은 길의 양옆 천막 사이에 밝은 작은 대상이 있다.
- 전경과 배경: 큰 전경 천막이 작은 인물을 감싸는 크기 차가 있다.
- 조명: 인물 옆 작은 따뜻한 후광이 기능점을 표시한다.
- 제작 패턴: P04, P10, P15 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 적 실루엣과 공격 방향
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bone_Bottom_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/59/Screenshot_SS_Bone_Bottom_05.png/800px-Screenshot_SS_Bone_Bottom_05.png)

### SS-DD-01 덩굴이 감싼 원형 장치

[이미지 보기](images/ss-dd-01.png) · SS / Deep Docks · 목표 노출 · 석재, 금속, 덩굴

- 관찰: 용암색 여백 위의 작은 발판에 수직 구조가 놓인다.
- 전경과 배경: 앞의 검은 바닥과 중경 원형 구조, 뒤 주황빛이 분리된다.
- 조명: 장치 중앙의 약한 청록빛과 아래 열기의 색이 다르다.
- 제작 패턴: P04, P06, P09, P14 — 목표에 모이는 빛 / 장치 경로와 작동부의 명료함 / 지역 문턱과 문양 입구 / 기능색과 장식색의 분리
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B07, B08, B11, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/06/Screenshot_SS_Deep_Docks_01.png/800px-Screenshot_SS_Deep_Docks_01.png)

### SS-DD-02 불빛 위 긴 다리

[이미지 보기](images/ss-dd-02.png) · SS / Deep Docks · 장치 공간 · 금속, 석재, 용암

- 관찰: 긴 다리 아래 여러 지지 구조가 반복되고 뒤에 큰 원형 기계가 보인다.
- 전경과 배경: 앞의 어두운 보행면과 뒤의 거대 흐린 기계가 분리된다.
- 조명: 수평의 강한 주황빛과 작은 불티가 깊이를 만든다.
- 제작 패턴: P03, P06, P07 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역 · 자산 명세 B03, B07, B08, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/64/Screenshot_SS_Deep_Docks_02.png/800px-Screenshot_SS_Deep_Docks_02.png)

### SS-DD-03 뜨거운 벽 옆 단단한 문

[이미지 보기](images/ss-dd-03.png) · SS / Deep Docks · 지역 경계 · 금속, 석재, 용암

- 관찰: 낮은 바닥 왼쪽 구조와 오른쪽 밝은 벽면이 비대칭으로 놓인다.
- 전경과 배경: 왼쪽 큰 검은 덩어리와 오른쪽 밝은 균열면이 대비된다.
- 조명: 주황 균열과 작은 적색 중심광이 다른 범위를 갖는다.
- 제작 패턴: P04, P09, P17 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B03, B04, B05, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f5/Screenshot_SS_Deep_Docks_03.png/800px-Screenshot_SS_Deep_Docks_03.png)

### SS-DD-04 뜨거운 바닥 위 높은 턱

[이미지 보기](images/ss-dd-04.png) · SS / Deep Docks · 위험 구간 · 금속, 석재, 용암

- 관찰: 아래 용암색 면과 오른쪽 높은 발판 사이에 큰 틈이 있다.
- 전경과 배경: 가까운 검은 발판과 뒤의 희미한 큰 원형 면이 겹친다.
- 조명: 하단의 넓은 열기빛 위로 작은 불티가 떠 있다.
- 제작 패턴: P05, P07, P13 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 대기광과 입자의 깊이
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f4/Screenshot_SS_Deep_Docks_04.png/800px-Screenshot_SS_Deep_Docks_04.png)

### SS-DD-05 사슬에 매달린 여러 화로

[이미지 보기](images/ss-dd-05.png) · SS / Deep Docks · 장치 외형 · 금속, 사슬, 용암

- 관찰: 높이가 다른 사슬 화로들이 밝은 용암면 위에 매달려 있다.
- 전경과 배경: 선명한 앞 사슬·화로와 뒤 흐린 사슬의 대비가 다르다.
- 조명: 넓은 주황빛과 어두운 화로 몸체, 붉은 내용물의 범위가 다르다.
- 제작 패턴: P03, P06, P07, P12 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태 / 재질의 군집과 빈 구간
- 적용 후보: 고대 장치 구역 · 자산 명세 B03, B07, B08, B09, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5a/Screenshot_SS_Deep_Docks_05.png/800px-Screenshot_SS_Deep_Docks_05.png)

### SS-DD-06 어두운 아치 안 중앙 의자

[이미지 보기](images/ss-dd-06.png) · SS / Deep Docks · 휴식 포켓 · 석재, 금속

- 관찰: 높은 아치 아래 작은 기능점과 넓은 바닥 여백이 있다.
- 전경과 배경: 큰 검은 외곽과 중앙 낮은 구조, 뒤 흐린 실내가 분리된다.
- 조명: 중앙 뒤쪽 약한 빛과 양옆 작은 수직빛이 겹친다.
- 제작 패턴: P03, P04, P10 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B03, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Deep_Docks_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5e/Screenshot_SS_Deep_Docks_06.png/800px-Screenshot_SS_Deep_Docks_06.png)

### SS-FF-01 큰 종 아래 열린 바닥

[이미지 보기](images/ss-ff-01.png) · SS / Far Fields · 열린 방 · 금속, 석재, 이끼

- 관찰: 양옆 짧은 발판과 위의 종 사이 중앙을 비워 둔다.
- 전경과 배경: 검은 가장자리와 뒤의 부드러운 녹색 대기층이 나뉜다.
- 조명: 한쪽 위의 사선 광막과 작은 불티가 보인다.
- 제작 패턴: P04, P06, P11 — 목표에 모이는 빛 / 장치 경로와 작동부의 명료함 / 전투방의 넓은 판독 공간
- 적용 후보: 전투방, 보스방 · 자산 명세 B04, B05, B07, B08, B13
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b7/Screenshot_SS_Far_Fields_01.png/800px-Screenshot_SS_Far_Fields_01.png)

### SS-FF-02 불타는 지면 옆 둥근 문

[이미지 보기](images/ss-ff-02.png) · SS / Far Fields · 지역 경계 · 석재, 금속, 용암

- 관찰: 수평 위험면 위의 벽에 둥근 구조가 묻혀 있다.
- 전경과 배경: 앞의 검은 줄기와 뒤 붉은 균열벽이 대비된다.
- 조명: 주황 세로빛과 수평 발광면이 함께 보인다.
- 제작 패턴: P07, P09, P17 — 안전면과 위험면의 다른 형태 / 지역 문턱과 문양 입구 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B03, B09, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/95/Screenshot_SS_Far_Fields_02.png/800px-Screenshot_SS_Far_Fields_02.png)

### SS-FF-03 넓은 열기와 작은 안전면

[이미지 보기](images/ss-ff-03.png) · SS / Far Fields · 위험 구간 · 석재, 용암

- 관찰: 밝은 수평 위험면 옆으로 작은 어두운 지면이 남는다.
- 전경과 배경: 상부와 하단의 검은 실루엣 사이 주황 공간이 열린다.
- 조명: 강한 열기빛과 밝은 불티를 위험 재질의 신호로 쓴다.
- 제작 패턴: P02, P07, P18 — 근접 전경과 중앙 시야 여백 / 안전면과 위험면의 다른 형태 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B02, B09, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8d/Screenshot_SS_Far_Fields_03.png/800px-Screenshot_SS_Far_Fields_03.png)

### SS-FF-04 큰 천막 둘레의 가로길

[이미지 보기](images/ss-ff-04.png) · SS / Far Fields · 랜드마크 · 천, 금속, 목재

- 관찰: 거대한 붉은 천막에 낮은 가로 발판들이 붙는다.
- 전경과 배경: 뒤의 큰 천막 면과 앞의 작은 발판이 크기로 구분된다.
- 조명: 주황 주변광과 천막의 작은 밝은 틈이 겹친다.
- 제작 패턴: P03, P12, P16 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fe/Screenshot_SS_Far_Fields_04.png/800px-Screenshot_SS_Far_Fields_04.png)

### SS-FF-05 따뜻한 천막 실내

[이미지 보기](images/ss-ff-05.png) · SS / Far Fields · 휴식 포켓 · 천, 석재, 유기체

- 관찰: 둥근 창들 아래 낮은 바닥과 작은 인물이 있다.
- 전경과 배경: 검은 실내 가장자리가 작은 밝은 활동 공간을 감싼다.
- 조명: 따뜻한 타원 창빛이 실내 물체 윤곽을 드러낸다.
- 제작 패턴: P04, P10, P15 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 적 실루엣과 공격 방향
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/05/Screenshot_SS_Far_Fields_05.png/800px-Screenshot_SS_Far_Fields_05.png)

### SS-FF-06 바위집의 따뜻한 문

[이미지 보기](images/ss-ff-06.png) · SS / Far Fields · 랜드마크 · 석재, 금속, 잎

- 관찰: 낮은 계단이 큰 둥근 집 입구로 이어진다.
- 전경과 배경: 앞 작은 잎과 중간 집, 뒤 어두운 식생을 분리한다.
- 조명: 집 전체보다 문과 둥근 창만 밝다.
- 제작 패턴: P04, P09, P16 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Far_Fields_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1a/Screenshot_SS_Far_Fields_06.png/800px-Screenshot_SS_Far_Fields_06.png)

### SS-HM-01 어두운 천장 아래 빛나는 고치

[이미지 보기](images/ss-hm-01.png) · SS / Hunter's March · 목표 노출 · 석재, 잎, 실

- 관찰: 낮은 길 중앙에 작고 밝은 둥근 물체가 놓인다.
- 전경과 배경: 검은 큰 천장과 뒤 녹색 여백이 작은 목표를 둘러싼다.
- 조명: 약한 사선빛과 고치의 따뜻한 중심광이 겹친다.
- 제작 패턴: P01, P04, P08 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B01, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/41/Screenshot_SS_Hunter%27s_March_01.png/800px-Screenshot_SS_Hunter%27s_March_01.png)

### SS-HM-02 매달린 작은 빛과 바닥 잔해

[이미지 보기](images/ss-hm-02.png) · SS / Hunter's March · 수평 통로 · 석재, 실, 식생

- 관찰: 낮은 길 위 여러 작은 광원이 서로 다른 높이에 매달린다.
- 전경과 배경: 앞의 낮은 검은 실루엣과 뒤의 어두운 녹색 면이 나뉜다.
- 조명: 작은 따뜻한 광점을 높이와 간격으로 분산한다.
- 제작 패턴: P04, P12, P13 — 목표에 모이는 빛 / 재질의 군집과 빈 구간 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B04, B05, B14, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/bb/Screenshot_SS_Hunter%27s_March_02.png/800px-Screenshot_SS_Hunter%27s_March_02.png)

### SS-HM-03 새장과 높은 광점 무리

[이미지 보기](images/ss-hm-03.png) · SS / Hunter's March · 랜드마크 · 금속, 실, 석재

- 관찰: 중앙 큰 새장 위로 여러 작은 빛이 세로로 모인다.
- 전경과 배경: 하단 새장 실루엣은 선명하고 위쪽 불빛은 부드럽다.
- 조명: 빛의 군집을 한쪽 수직 축에 모은다.
- 제작 패턴: P03, P04, P16 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/4e/Screenshot_SS_Hunter%27s_March_03.png/800px-Screenshot_SS_Hunter%27s_March_03.png)

### SS-HM-04 비어 있는 작은 벤치방

[이미지 보기](images/ss-hm-04.png) · SS / Hunter's March · 휴식 포켓 · 석재, 실, 잎

- 관찰: 아래 작은 벤치와 한쪽 빈 공간을 낮은 천장이 감싼다.
- 전경과 배경: 가까운 검은 줄기와 뒤의 약한 녹색 면이 겹친다.
- 조명: 넓은 약한 사선빛이 벤치 주변 여백을 만든다.
- 제작 패턴: P02, P10, P17 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓 / 비대칭 공간의 무게 배분
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B03, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/da/Screenshot_SS_Hunter%27s_March_04.png/800px-Screenshot_SS_Hunter%27s_March_04.png)

### SS-HM-05 가시 천장 아래 걸린 돌판

[이미지 보기](images/ss-hm-05.png) · SS / Hunter's March · 위험 구간 · 석재, 실, 가시

- 관찰: 날카로운 상부 구조 아래 매달린 넓은 돌판이 보인다.
- 전경과 배경: 앞의 검은 새장과 중간 돌판, 뒤 흐린 틈이 나뉜다.
- 조명: 위쪽 좁은 빛으로 돌판 상면만 남긴다.
- 제작 패턴: P05, P06, P07 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B07, B08, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/ea/Screenshot_SS_Hunter%27s_March_05.png/800px-Screenshot_SS_Hunter%27s_March_05.png)

### SS-HM-06 낮은 발판 위 작은 벌레

[이미지 보기](images/ss-hm-06.png) · SS / Hunter's March · 전투 공간 · 석재, 잎, 유기체

- 관찰: 작은 적이 낮은 왼쪽 발판 위에 있고 오른쪽은 비어 있다.
- 전경과 배경: 적의 밝은 얼굴과 뒤의 어두운 녹색 식생이 분리된다.
- 조명: 작은 얼굴의 명암을 주변 광점보다 강하게 둔다.
- 제작 패턴: P11, P15, P17 — 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향 / 비대칭 공간의 무게 배분
- 적용 후보: 전투방, 보스방 · 자산 명세 B02, B03, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Hunter%27s_March_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c5/Screenshot_SS_Hunter%27s_March_06.png/800px-Screenshot_SS_Hunter%27s_March_06.png)

### SS-SH-01 깊은 숲의 원형 문

[이미지 보기](images/ss-sh-01.png) · SS / Shellwood · 지역 경계 · 석재, 뿌리, 이끼

- 관찰: 낮은 큰 발판 중앙에 세로 문양 구조가 있다.
- 전경과 배경: 앞 검은 코어와 중간 문, 뒤의 큰 숲줄기가 겹친다.
- 조명: 위쪽 청록빛과 작은 포자가 문 주위 빈 공간을 드러낸다.
- 제작 패턴: P03, P09, P16 — 중경과 원경의 다른 대비 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/83/Screenshot_SS_Shellwood_01.png/800px-Screenshot_SS_Shellwood_01.png)

### SS-SH-02 높은 아치 아래 작은 휴식점

[이미지 보기](images/ss-sh-02.png) · SS / Shellwood · 휴식 포켓 · 석재, 금속, 뿌리

- 관찰: 큰 문양 판 아래 중앙 기능점만 낮게 놓인다.
- 전경과 배경: 검은 양옆 프레임과 중앙 실내의 대비가 다르다.
- 조명: 양옆 작은 빛보다 중앙 뒤의 약한 광막이 넓다.
- 제작 패턴: P03, P04, P10 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B03, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c7/Screenshot_SS_Shellwood_02.png/800px-Screenshot_SS_Shellwood_02.png)

### SS-SH-03 버섯처럼 생긴 높은 쉼터

[이미지 보기](images/ss-sh-03.png) · SS / Shellwood · 복층 공간 · 석재, 뿌리, 이끼

- 관찰: 왼쪽 높은 지붕 구조와 오른쪽 짧은 턱 사이에 낮은 공간이 있다.
- 전경과 배경: 앞 상부 종과 뒤 둥근 식생 군집이 다른 크기로 겹친다.
- 조명: 넓고 약한 사선빛이 중앙의 비어 있는 공기를 보여 준다.
- 제작 패턴: P03, P05, P06 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B06, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/70/Screenshot_SS_Shellwood_03.png/800px-Screenshot_SS_Shellwood_03.png)

### SS-SH-04 어두운 천장 아래 밝은 출구

[이미지 보기](images/ss-sh-04.png) · SS / Shellwood · 지역 경계 · 석재, 뿌리

- 관찰: 왼쪽 밝은 틈과 오른쪽 높은 지면이 낮은 통로를 만든다.
- 전경과 배경: 큰 검은 코어가 위를 가리고 먼 출구의 빛만 남는다.
- 조명: 밝은 출구와 낮은 청록 주변광이 대비된다.
- 제작 패턴: P01, P04, P09 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B01, B04, B05, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b7/Screenshot_SS_Shellwood_04.png/800px-Screenshot_SS_Shellwood_04.png)

### SS-SH-05 낮은 물가와 큰 잎 천장

[이미지 보기](images/ss-sh-05.png) · SS / Shellwood · 수평 통로 · 물, 이끼, 잎

- 관찰: 양옆 지면 사이 낮은 물면이 있고 큰 잎이 위를 감싼다.
- 전경과 배경: 앞 검은 풀과 중간 수면, 뒤 숲기둥을 구분한다.
- 조명: 넓은 녹색빛을 배경에 두고 상면은 어둡게 남긴다.
- 제작 패턴: P02, P03, P12 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B02, B03, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/41/Screenshot_SS_Shellwood_05.png/800px-Screenshot_SS_Shellwood_05.png)

### SS-SH-06 거대한 나무와 사선 빛

[이미지 보기](images/ss-sh-06.png) · SS / Shellwood · 랜드마크 · 뿌리, 석재, 잎

- 관찰: 왼쪽 큰 나무에서 중앙 빈 공간으로 빛이 내려온다.
- 전경과 배경: 앞 검은 줄기와 뒤 큰 나무 사이 공기층이 보인다.
- 조명: 부드러운 사선 빛 안에 작은 밝은 입자가 모인다.
- 제작 패턴: P02, P04, P13, P16 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 대기광과 입자의 깊이 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 이끼 통로 · 자산 명세 B02, B04, B05, B15, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Shellwood_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/df/Screenshot_SS_Shellwood_06.png/800px-Screenshot_SS_Shellwood_06.png)

### SS-GM-01 밝은 인물과 복층 발판

[이미지 보기](images/ss-gm-01.png) · SS / Greymoor · 복층 공간 · 석재, 금속, 목재

- 관찰: 작은 밝은 인물 위로 매달린 발판과 오른쪽 높은 턱이 보인다.
- 전경과 배경: 상부 검은 천장과 뒤 따뜻한 실내 면이 나뉜다.
- 조명: 인물 뒤 국소 주황빛과 작은 등불이 서로 다른 높이에 있다.
- 제작 패턴: P04, P05, P15 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 적 실루엣과 공격 방향
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B04, B05, B06, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a8/Screenshot_SS_Greymoor_01.png/800px-Screenshot_SS_Greymoor_01.png)

### SS-GM-02 촛불 기둥과 짧은 발판

[이미지 보기](images/ss-gm-02.png) · SS / Greymoor · 수직 이동 · 석재, 밀랍

- 관찰: 높은 세 무리의 촛불 사이 작은 발판이 놓인다.
- 전경과 배경: 앞의 어두운 발판과 뒤의 흐린 촛불 군집이 분리된다.
- 조명: 여러 따뜻한 빛을 묶어 큰 밝기 덩어리로 읽힌다.
- 제작 패턴: P03, P04, P05 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B04, B05, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/60/Screenshot_SS_Greymoor_02.png/800px-Screenshot_SS_Greymoor_02.png)

### SS-GM-03 넓은 바닥과 먼 천막

[이미지 보기](images/ss-gm-03.png) · SS / Greymoor · 수평 통로 · 천, 석재, 식생

- 관찰: 넓게 열린 길 뒤 멀리 큰 천막과 둥근 물체가 보인다.
- 전경과 배경: 앞의 어두운 바닥과 뒤 거의 흐려진 큰 형태를 구분한다.
- 조명: 낮은 청록 대기광으로 먼 공간의 대비를 낮춘다.
- 제작 패턴: P03, P11, P13 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B03, B13, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/11/Screenshot_SS_Greymoor_03.png/800px-Screenshot_SS_Greymoor_03.png)

### SS-GM-04 문양 판 아래 휴식점

[이미지 보기](images/ss-gm-04.png) · SS / Greymoor · 휴식 포켓 · 석재, 금속, 뿌리

- 관찰: 높은 실내의 중앙 의자 주변을 넓게 비운다.
- 전경과 배경: 검은 외곽과 중앙 낮은 구조, 뒤 아치가 겹친다.
- 조명: 중앙 뒤쪽 약한 빛이 기능점을 읽힌다.
- 제작 패턴: P03, P04, P10 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B03, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e5/Screenshot_SS_Greymoor_04.png/800px-Screenshot_SS_Greymoor_04.png)

### SS-GM-05 바람개비 뒤의 낮은 다리

[이미지 보기](images/ss-gm-05.png) · SS / Greymoor · 수평 통로 · 금속, 목재, 석재

- 관찰: 낮은 난간 뒤 거대한 원형 구조와 가는 줄이 있다.
- 전경과 배경: 앞 작은 난간과 뒤 거대 흐린 구조가 크기로 나뉜다.
- 조명: 한쪽 작은 등불과 약한 수직 광막을 분리한다.
- 제작 패턴: P03, P06, P16 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로 · 자산 명세 B03, B07, B08, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b1/Screenshot_SS_Greymoor_05.png/800px-Screenshot_SS_Greymoor_05.png)

### SS-GM-06 좁은 샛길의 따뜻한 공간

[이미지 보기](images/ss-gm-06.png) · SS / Greymoor · 보상 포켓 · 석재, 금속

- 관찰: 검은 지형 사이 작은 인물과 밝은 벽 부분만 드러난다.
- 전경과 배경: 큰 검은 코어가 좁은 활동 공간을 둘러싼다.
- 조명: 작고 따뜻한 벽빛으로 샛길의 목적을 표시한다.
- 제작 패턴: P01, P04, P08 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B01, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Greymoor_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/63/Screenshot_SS_Greymoor_06.png/800px-Screenshot_SS_Greymoor_06.png)

### SS-BH-01 종과 풍선이 있는 거리

[이미지 보기](images/ss-bh-01.png) · SS / Bellhart · 랜드마크 · 금속, 석재, 천

- 관찰: 평평한 거리 위 높은 종 구조와 여러 공중 형체가 모인다.
- 전경과 배경: 앞의 작은 인물과 중간 종, 뒤 높은 건물이 크기로 나뉜다.
- 조명: 작은 따뜻한 등불들을 길의 높이에 분산한다.
- 제작 패턴: P03, P12, P16 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/49/Screenshot_SS_Bellhart_01.png/800px-Screenshot_SS_Bellhart_01.png)

### SS-BH-02 큰 종 옆 평평한 쉼터

[이미지 보기](images/ss-bh-02.png) · SS / Bellhart · 휴식 포켓 · 금속, 석재

- 관찰: 중앙 기능점 옆으로 작은 인물들이 놓이고 상부는 비어 있다.
- 전경과 배경: 뒤 거대 종 구조와 앞 낮은 물체의 크기 차가 뚜렷하다.
- 조명: 작은 등불로 기능점을 표시하고 전체는 낮은 채도로 둔다.
- 제작 패턴: P04, P10, P16 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/cd/Screenshot_SS_Bellhart_02.png/800px-Screenshot_SS_Bellhart_02.png)

### SS-BH-03 종 아래 둥근 빈 공간

[이미지 보기](images/ss-bh-03.png) · SS / Bellhart · 열린 방 · 금속, 석재, 뼈

- 관찰: 양옆 발판 사이 낮은 중앙 공간과 위의 종이 연결된다.
- 전경과 배경: 앞의 어두운 껍질 바닥과 뒤의 부드러운 공기가 나뉜다.
- 조명: 넓은 사선빛과 작은 따뜻한 광점이 깊이를 만든다.
- 제작 패턴: P03, P04, P06 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 장치 경로와 작동부의 명료함
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B04, B05, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/91/Screenshot_SS_Bellhart_03.png/800px-Screenshot_SS_Bellhart_03.png)

### SS-BH-04 중앙 인물로 모이는 방사 효과

[이미지 보기](images/ss-bh-04.png) · SS / Bellhart · 시네마틱 효과 · 빛 효과

- 관찰: 주변이 방사형으로 흐려지고 밝은 인물이 중앙에 남는다.
- 전경과 배경: 선명한 중앙 형체와 흐린 주변의 차이가 크다.
- 조명: 따뜻한 중심광과 바깥 암전이 강한 집중을 만든다.
- 제작 패턴: P04, P15, P20 — 목표에 모이는 빛 / 적 실루엣과 공격 방향 / 시야 제한과 집중 연출
- 적용 후보: 유물 획득 연출, 보스 등장 연출 · 자산 명세 B04, B05, B16, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9e/Screenshot_SS_Bellhart_04.png/800px-Screenshot_SS_Bellhart_04.png)

### SS-BH-05 쓰러진 종이 있는 거리

[이미지 보기](images/ss-bh-05.png) · SS / Bellhart · 상태 변형 · 금속, 석재

- 관찰: 비슷한 거리 구도에서 큰 종이 기울어져 상태 차이가 보인다.
- 전경과 배경: 큰 장식이 바뀌어도 앞의 낮은 보행선은 남는다.
- 조명: 작은 등불의 높이는 유지하고 전체 밝기는 낮춘다.
- 제작 패턴: P16, P19 — 방마다 하나의 큰 기억점 / 공간 골격을 유지한 상태 변화
- 적용 후보: 고대 장치 구역, 보스 처치 후 · 자산 명세 B17, B19
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e9/Screenshot_SS_Bellhart_05.png/800px-Screenshot_SS_Bellhart_05.png)

### SS-BH-06 어두운 작은 방의 입구

[이미지 보기](images/ss-bh-06.png) · SS / Bellhart · 보상 포켓 · 석재, 금속

- 관찰: 검은 지형 속 좁은 방에 작은 문과 인물이 보인다.
- 전경과 배경: 주변 검은 코어 안쪽 테두리만 푸르게 드러난다.
- 조명: 약한 청록빛과 작은 밝은 얼굴이 위치를 표시한다.
- 제작 패턴: P01, P08, P15 — 검은 지형 속과 읽히는 테두리 / 보상의 선노출과 우회 경로 / 적 실루엣과 공격 방향
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B01, B10, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bellhart_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9b/Screenshot_SS_Bellhart_06.png/800px-Screenshot_SS_Bellhart_06.png)

### SS-BW-01 진흙색 안개의 긴 길

[이미지 보기](images/ss-bw-01.png) · SS / Bilewater · 수평 통로 · 진흙, 껍질, 석재

- 관찰: 낮은 길 위에 작은 받침 구조가 있고 뒤로 큰 껍질들이 보인다.
- 전경과 배경: 앞 검은 기둥과 뒤 둥근 흐린 덩어리가 나뉜다.
- 조명: 황록색 안개와 어두운 재질로 눅눅한 공간을 만든다.
- 제작 패턴: P03, P12, P13 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B03, B14, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/60/Screenshot_SS_Bilewater_01.png/800px-Screenshot_SS_Bilewater_01.png)

### SS-BW-02 유기체가 늘어진 쉼터

[이미지 보기](images/ss-bw-02.png) · SS / Bilewater · 휴식 포켓 · 뿌리, 껍질, 잎

- 관찰: 중앙 작은 기능점 위로 큰 덩굴·껍질 덩어리가 내려온다.
- 전경과 배경: 앞 검은 잎과 뒤의 얇은 구조를 분리한다.
- 조명: 중앙의 낮은 황록빛만 남기고 둘레를 어둡게 둔다.
- 제작 패턴: P02, P10, P12 — 근접 전경과 중앙 시야 여백 / 작고 명료한 휴식 포켓 / 재질의 군집과 빈 구간
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B12, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/22/Screenshot_SS_Bilewater_02.png/800px-Screenshot_SS_Bilewater_02.png)

### SS-BW-03 늘어진 벽 사이 가는 다리

[이미지 보기](images/ss-bw-03.png) · SS / Bilewater · 위험 구간 · 껍질, 석재, 목재

- 관찰: 양옆 두꺼운 지형 사이 중앙 다리가 얇게 이어진다.
- 전경과 배경: 검은 가장자리와 중간 다리, 뒤 녹색 안개가 겹친다.
- 조명: 윗부분 작은 빛과 아래 넓은 흐림으로 다리 외곽을 드러낸다.
- 제작 패턴: P05, P07, P13 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 대기광과 입자의 깊이
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8a/Screenshot_SS_Bilewater_03.png/800px-Screenshot_SS_Bilewater_03.png)

### SS-BW-04 큰 매달린 형체와 아래 국소빛

[이미지 보기](images/ss-bw-04.png) · SS / Bilewater · 목표 노출 · 껍질, 뿌리, 석재

- 관찰: 넓은 검은 외곽 안 작은 아래 지점에 밝기가 모인다.
- 전경과 배경: 앞의 굵은 교차 줄기와 뒤 흐린 벽 사이 목표가 보인다.
- 조명: 아래의 흰 녹색 빛과 위의 어두운 큰 형체가 대비된다.
- 제작 패턴: P02, P04, P08 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d9/Screenshot_SS_Bilewater_04.png/800px-Screenshot_SS_Bilewater_04.png)

### SS-BW-05 같은 동굴 구도의 변형

[이미지 보기](images/ss-bw-05.png) · SS / Bilewater · 상태 변형 · 껍질, 뿌리, 석재

- 관찰: SS-BW-04와 거의 같은 공간 구도이며 세부 형체 상태가 다르다.
- 전경과 배경: 교차하는 앞 줄기와 뒤 안개 구조를 비교할 수 있다.
- 조명: 중앙 아래의 국소빛과 주변 어둠의 관계가 유지된다.
- 제작 패턴: P04, P19 — 목표에 모이는 빛 / 공간 골격을 유지한 상태 변화
- 적용 후보: 고대 장치 구역, 보스 처치 후 · 자산 명세 B04, B05, B19
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a6/Screenshot_SS_Bilewater_05.png/800px-Screenshot_SS_Bilewater_05.png)

### SS-BW-06 낮은 껍질 더미와 뿌리 천장

[이미지 보기](images/ss-bw-06.png) · SS / Bilewater · 수평 통로 · 껍질, 뿌리, 진흙

- 관찰: 바닥의 둥근 껍질 더미 위에 뿌리 덩어리가 매달린다.
- 전경과 배경: 하단 검은 잎과 중간 더미, 뒤 녹색 흐림이 나뉜다.
- 조명: 낮은 황록 대기광이 바닥의 외곽만 드러낸다.
- 제작 패턴: P01, P02, P12 — 검은 지형 속과 읽히는 테두리 / 근접 전경과 중앙 시야 여백 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B01, B02, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Bilewater_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c7/Screenshot_SS_Bilewater_06.png/800px-Screenshot_SS_Bilewater_06.png)

### SS-SR-01 긴 창살 같은 교차 구조

[이미지 보기](images/ss-sr-01.png) · SS / Sinner's Road · 수평 통로 · 목재, 가시, 석재

- 관찰: 평평한 길 위 양옆 긴 뾰족한 구조가 안으로 향한다.
- 전경과 배경: 왼쪽 큰 검은 전경과 뒤 긴 창살을 구분한다.
- 조명: 낮은 녹색빛으로 날카로운 외곽을 남긴다.
- 제작 패턴: P02, P07, P12 — 근접 전경과 중앙 시야 여백 / 안전면과 위험면의 다른 형태 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B02, B09, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/78/Screenshot_SS_Sinner%27s_Road_01.png/800px-Screenshot_SS_Sinner%27s_Road_01.png)

### SS-SR-02 가시 천장 아래 낮은 길

[이미지 보기](images/ss-sr-02.png) · SS / Sinner's Road · 위험 구간 · 금속, 가시, 석재

- 관찰: 왼쪽 높은 가시 띠 아래로 평평한 길이 이어진다.
- 전경과 배경: 앞 어두운 바닥과 뒤의 흐린 원형 구조가 나뉜다.
- 조명: 가시 끝의 밝기를 낮은 채도 배경에서 읽힌다.
- 제작 패턴: P05, P07 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fa/Screenshot_SS_Sinner%27s_Road_02.png/800px-Screenshot_SS_Sinner%27s_Road_02.png)

### SS-SR-03 따뜻한 금속 문과 작은 인물

[이미지 보기](images/ss-sr-03.png) · SS / Sinner's Road · 지역 경계 · 금속, 석재

- 관찰: 큰 둥근 문과 작은 인물이 낮은 바닥에 나란히 놓인다.
- 전경과 배경: 앞 작은 인물과 중간 문, 뒤 큰 어두운 고리가 겹친다.
- 조명: 약한 주황빛이 문양 외곽과 얼굴을 드러낸다.
- 제작 패턴: P04, P09, P15 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 적 실루엣과 공격 방향
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B11, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/33/Screenshot_SS_Sinner%27s_Road_03.png/800px-Screenshot_SS_Sinner%27s_Road_03.png)

### SS-SR-04 지형으로 감싼 작은 밝은 틈

[이미지 보기](images/ss-sr-04.png) · SS / Sinner's Road · 보상 포켓 · 석재, 껍질, 뿌리

- 관찰: 두꺼운 천장 아래 작은 열린 방이 끝의 빛으로 이어진다.
- 전경과 배경: 앞 교차 줄기와 뒤 밝은 작은 틈이 대비된다.
- 조명: 끝부분의 따뜻한 빛이 좁은 방의 방향을 만든다.
- 제작 패턴: P01, P04, P08 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B01, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/4/44/Screenshot_SS_Sinner%27s_Road_04.png/800px-Screenshot_SS_Sinner%27s_Road_04.png)

### SS-SR-05 작은 굴 안 둥근 적 무리

[이미지 보기](images/ss-sr-05.png) · SS / Sinner's Road · 전투 공간 · 석재, 유기체

- 관찰: 좁은 수평 굴 끝에 작은 둥근 적 둘이 모인다.
- 전경과 배경: 검은 큰 코어와 작은 밝은 몸체의 크기가 대비된다.
- 조명: 한쪽 작은 등불과 적의 흰 몸체를 구분한다.
- 제작 패턴: P01, P15, P20 — 검은 지형 속과 읽히는 테두리 / 적 실루엣과 공격 방향 / 시야 제한과 집중 연출
- 적용 후보: 전투방, 보스방 · 자산 명세 B01, B16, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/82/Screenshot_SS_Sinner%27s_Road_05.png/800px-Screenshot_SS_Sinner%27s_Road_05.png)

### SS-SR-06 끝빛이 남은 동굴 변형

[이미지 보기](images/ss-sr-06.png) · SS / Sinner's Road · 상태 변형 · 석재, 껍질, 뿌리

- 관찰: SS-SR-04와 비슷한 구도에서 안쪽 작은 물체 상태가 달라 보인다.
- 전경과 배경: 큰 앞줄기와 뒤의 좁은 틈은 같은 공간 골격을 이룬다.
- 조명: 안쪽의 작은 주황빛을 상태 비교의 기준으로 남긴다.
- 제작 패턴: P08, P19 — 보상의 선노출과 우회 경로 / 공간 골격을 유지한 상태 변화
- 적용 후보: 고대 장치 구역, 보스 처치 후 · 자산 명세 B10, B19
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sinner%27s_Road_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a3/Screenshot_SS_Sinner%27s_Road_06.png/800px-Screenshot_SS_Sinner%27s_Road_06.png)

### SS-MF-01 눈빛 동굴의 작은 주황 광원

[이미지 보기](images/ss-mf-01.png) · SS / Mount Fay · 수평 통로 · 얼음, 석재, 금속

- 관찰: 차가운 평평한 바닥 위 인물과 작은 매달린 광원이 있다.
- 전경과 배경: 위 검은 천장 끝과 뒤 푸른 대기층이 분리된다.
- 조명: 차가운 공간 속 작은 주황빛이 기능점을 강조한다.
- 제작 패턴: P04, P12, P14, P17 — 목표에 모이는 빛 / 재질의 군집과 빈 구간 / 기능색과 장식색의 분리 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B04, B05, B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e5/Screenshot_SS_Mount_Fay_01.png/800px-Screenshot_SS_Mount_Fay_01.png)

### SS-MF-02 큰 등 아래 중앙 구조

[이미지 보기](images/ss-mf-02.png) · SS / Mount Fay · 랜드마크 · 금속, 석재, 얼음

- 관찰: 높은 천장등과 아래 작은 구조가 세로 축을 만든다.
- 전경과 배경: 앞 검은 기둥과 뒤 흐린 얼음벽이 겹친다.
- 조명: 위의 흰 빛과 중앙의 작은 촛불 무리가 다른 크기로 보인다.
- 제작 패턴: P03, P04, P16 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/67/Screenshot_SS_Mount_Fay_02.png/800px-Screenshot_SS_Mount_Fay_02.png)

### SS-MF-03 큰 금속 문양 아래 휴식점

[이미지 보기](images/ss-mf-03.png) · SS / Mount Fay · 휴식 포켓 · 금속, 석재

- 관찰: 수직으로 큰 금속 장식 아래 작은 의자형 구조가 있다.
- 전경과 배경: 큰 검은 외곽과 뒤의 낮은 주황 면이 나뉜다.
- 조명: 국소 따뜻한 빛을 중앙 세로 영역에 제한한다.
- 제작 패턴: P04, P10, P16 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/7a/Screenshot_SS_Mount_Fay_03.png/800px-Screenshot_SS_Mount_Fay_03.png)

### SS-MF-04 차가운 길 옆 따뜻한 벤치

[이미지 보기](images/ss-mf-04.png) · SS / Mount Fay · 휴식 포켓 · 얼음, 석재, 금속

- 관찰: 눈 쌓인 바닥 옆 벤치와 작은 매달린 불빛이 보인다.
- 전경과 배경: 왼쪽 검은 천장과 오른쪽 밝은 냉색 공간이 비대칭이다.
- 조명: 따뜻한 작은 등불과 차가운 넓은 바깥빛이 대비된다.
- 제작 패턴: P04, P10, P17 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 비대칭 공간의 무게 배분
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B03, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/dd/Screenshot_SS_Mount_Fay_04.png/800px-Screenshot_SS_Mount_Fay_04.png)

### SS-MF-05 눈 덩어리와 먼 바위기둥

[이미지 보기](images/ss-mf-05.png) · SS / Mount Fay · 수평 통로 · 얼음, 석재, 잎

- 관찰: 낮은 눈 덩어리 사이 길과 멀리 솟은 기둥들이 보인다.
- 전경과 배경: 앞의 검은 가는 식물과 뒤 흐린 큰 기둥이 나뉜다.
- 조명: 밝은 회청색 대기광이 먼 윤곽을 흐리게 만든다.
- 제작 패턴: P03, P12, P18 — 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간 / 밝은 지역에서의 대비 반전
- 적용 후보: 이끼 통로, 중앙 통로 · 자산 명세 B03, B14, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1f/Screenshot_SS_Mount_Fay_05.png/800px-Screenshot_SS_Mount_Fay_05.png)

### SS-MF-06 차가운 실내의 고립된 벤치

[이미지 보기](images/ss-mf-06.png) · SS / Mount Fay · 휴식 포켓 · 석재, 금속, 얼음

- 관찰: 큰 원형 공간 안 벤치를 작게 배치하고 주변을 비운다.
- 전경과 배경: 앞 검은 하단 가림과 뒤의 큰 푸른 형체가 겹친다.
- 조명: 천장등에서 아래로 떨어지는 좁은 흰 빛이 벤치를 향한다.
- 제작 패턴: P02, P04, P10 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Mount_Fay_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c9/Screenshot_SS_Mount_Fay_06.png/800px-Screenshot_SS_Mount_Fay_06.png)

### SS-SK-01 높은 석조 기둥과 붉은 군집

[이미지 보기](images/ss-sk-01.png) · SS / Sands of Karak · 복층 공간 · 석재, 잎, 금속

- 관찰: 여러 층의 석조 구조 사이에 작은 붉은 덩어리가 있다.
- 전경과 배경: 오른쪽 큰 검은 기둥과 뒤의 흐린 벽면이 나뉜다.
- 조명: 약한 청록 주변광 속 붉은 작은 부분을 구별한다.
- 제작 패턴: P03, P05, P12 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e7/Screenshot_SS_Sands_of_Karak_01.png/800px-Screenshot_SS_Sands_of_Karak_01.png)

### SS-SK-02 붉은 가시 옆 작은 턱

[이미지 보기](images/ss-sk-02.png) · SS / Sands of Karak · 위험 구간 · 가시, 석재, 잎

- 관찰: 낮은 안전면과 오른쪽 붉은 가시 띠 사이 폭이 좁다.
- 전경과 배경: 상부 검은 코어와 뒤의 낮은 보랏빛 여백을 구분한다.
- 조명: 따뜻한 가시 끝과 작은 황색 광원이 서로 다른 신호다.
- 제작 패턴: P05, P07, P08 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 보상의 선노출과 우회 경로
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/27/Screenshot_SS_Sands_of_Karak_02.png/800px-Screenshot_SS_Sands_of_Karak_02.png)

### SS-SK-03 굵은 문기둥 옆 작은 적

[이미지 보기](images/ss-sk-03.png) · SS / Sands of Karak · 전투 공간 · 석재, 껍질, 금속

- 관찰: 평평한 길 끝의 굵은 기둥 옆에 작은 적이 놓인다.
- 전경과 배경: 큰 문기둥과 작은 밝은 적을 크기 차로 분리한다.
- 조명: 밝은 뒤 공간 앞에서 적의 외곽을 남긴다.
- 제작 패턴: P09, P15, P18 — 지역 문턱과 문양 입구 / 적 실루엣과 공격 방향 / 밝은 지역에서의 대비 반전
- 적용 후보: 전투방, 보스방 · 자산 명세 B11, B16, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/34/Screenshot_SS_Sands_of_Karak_03.png/800px-Screenshot_SS_Sands_of_Karak_03.png)

### SS-SK-04 붉은 식생이 감싼 빈 방

[이미지 보기](images/ss-sk-04.png) · SS / Sands of Karak · 열린 방 · 잎, 석재

- 관찰: 평평한 바닥 둘레로 붉은 식생이 붙고 가운데는 비어 있다.
- 전경과 배경: 앞 검은 풀과 중간 붉은 테두리, 뒤 푸른 공간이 나뉜다.
- 조명: 부드러운 푸른 중앙광과 따뜻한 가장자리 재질을 대비한다.
- 제작 패턴: P02, P11, P17 — 근접 전경과 중앙 시야 여백 / 전투방의 넓은 판독 공간 / 비대칭 공간의 무게 배분
- 적용 후보: 전투방, 보스방 · 자산 명세 B02, B03, B13
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/54/Screenshot_SS_Sands_of_Karak_04.png/800px-Screenshot_SS_Sands_of_Karak_04.png)

### SS-SK-05 분홍 군집이 빛나는 작은 틈

[이미지 보기](images/ss-sk-05.png) · SS / Sands of Karak · 목표 노출 · 유기체, 석재

- 관찰: 좁은 포켓의 한쪽 벽을 큰 밝은 군집이 채운다.
- 전경과 배경: 검은 외곽과 중간 발광 덩어리, 뒤의 작은 틈이 구분된다.
- 조명: 강한 분홍 중심과 보라색 번짐을 국소적으로 사용한다.
- 제작 패턴: P04, P08, P18 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 밝은 지역에서의 대비 반전
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B10, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/75/Screenshot_SS_Sands_of_Karak_05.png/800px-Screenshot_SS_Sands_of_Karak_05.png)

### SS-SK-06 큰 검은 가림 뒤 분홍빛

[이미지 보기](images/ss-sk-06.png) · SS / Sands of Karak · 지역 경계 · 유기체, 석재, 잎

- 관찰: 앞의 큰 검은 덩어리가 뒤의 분홍빛 공간을 부분적으로 가린다.
- 전경과 배경: 앞 실루엣과 뒤 밝은 식생 군집의 겹침이 뚜렷하다.
- 조명: 차가운 길과 분홍 광원이 만나는 경계를 만든다.
- 제작 패턴: P02, P09, P13 — 근접 전경과 중앙 시야 여백 / 지역 문턱과 문양 입구 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B02, B11, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Sands_of_Karak_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e7/Screenshot_SS_Sands_of_Karak_06.png/800px-Screenshot_SS_Sands_of_Karak_06.png)

### SS-WW-01 갈색 동굴의 사선 틈빛

[이미지 보기](images/ss-ww-01.png) · SS / Wormways · 수평 통로 · 석재, 뿌리, 껍질

- 관찰: 낮은 길 뒤 큰 둥근 관 형체가 휘어진 천장을 따른다.
- 전경과 배경: 앞 검은 줄기와 뒤 흐린 갈색 큰 면이 나뉜다.
- 조명: 한쪽 위에서 좁은 따뜻한 빛이 내려온다.
- 제작 패턴: P02, P04, P12 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B02, B04, B05, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c4/Screenshot_SS_Wormways_01.png/800px-Screenshot_SS_Wormways_01.png)

### SS-WW-02 작은 조형물과 둘레 뿌리

[이미지 보기](images/ss-ww-02.png) · SS / Wormways · 목표 노출 · 석재, 뿌리

- 관찰: 낮은 중앙 조형물과 양옆 어두운 뿌리가 작은 빈 공간을 만든다.
- 전경과 배경: 앞 검은 줄기 사이로 중앙 물체와 뒤 큰 면이 보인다.
- 조명: 약한 따뜻한 광막을 중앙에 제한한다.
- 제작 패턴: P02, P04, P16 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/05/Screenshot_SS_Wormways_02.png/800px-Screenshot_SS_Wormways_02.png)

### SS-WW-03 이끼 벽 옆 세로 발판

[이미지 보기](images/ss-ww-03.png) · SS / Wormways · 수직 이동 · 이끼, 석재, 잎

- 관찰: 아래 낮은 길 위로 짧은 발판들이 떠 있다.
- 전경과 배경: 오른쪽 큰 검은 잎과 뒤 낮은 대비의 이끼벽이 나뉜다.
- 조명: 작은 포자와 약한 녹색빛이 세로 공기를 드러낸다.
- 제작 패턴: P02, P05, P12 — 근접 전경과 중앙 시야 여백 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B02, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3b/Screenshot_SS_Wormways_03.png/800px-Screenshot_SS_Wormways_03.png)

### SS-WW-04 푸른 작은 방의 인물과 벤치

[이미지 보기](images/ss-ww-04.png) · SS / Wormways · 휴식 포켓 · 금속, 석재, 유리

- 관찰: 낮은 벤치 옆 밝은 인물이 있고 뒤에 수직 용기가 보인다.
- 전경과 배경: 앞 기둥과 인물, 뒤 흐린 용기들이 층을 만든다.
- 조명: 차가운 청색 주변광과 작은 흰 등불을 구분한다.
- 제작 패턴: P03, P10, P15 — 중경과 원경의 다른 대비 / 작고 명료한 휴식 포켓 / 적 실루엣과 공격 방향
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B03, B12, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/2e/Screenshot_SS_Wormways_04.png/800px-Screenshot_SS_Wormways_04.png)

### SS-WW-05 푸른 생명빛이 모인 중앙

[이미지 보기](images/ss-ww-05.png) · SS / Wormways · 목표 노출 · 석재, 유기체

- 관찰: 낮은 중앙 덩어리 주변에 밝은 작은 형체들이 모인다.
- 전경과 배경: 앞 하단 검은 가림과 뒤 부드러운 청색 면이 겹친다.
- 조명: 작은 푸른 발광체의 군집이 목표를 만든다.
- 제작 패턴: P04, P08, P13 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 대기광과 입자의 깊이
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B10, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9f/Screenshot_SS_Wormways_05.png/800px-Screenshot_SS_Wormways_05.png)

### SS-WW-06 어두운 벤치 옆 작은 나비빛

[이미지 보기](images/ss-ww-06.png) · SS / Wormways · 휴식 포켓 · 석재, 식생

- 관찰: 낮은 의자형 구조 옆 작은 발광체가 남는다.
- 전경과 배경: 앞 검은 기둥과 뒤의 매우 어두운 큰 구조가 나뉜다.
- 조명: 큰 전체광 없이 작은 청색빛으로 기능점을 표시한다.
- 제작 패턴: P04, P10 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Wormways_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/57/Screenshot_SS_Wormways_06.png/800px-Screenshot_SS_Wormways_06.png)

### SS-UW-01 천장 광원 아래 두 조형물

[이미지 보기](images/ss-uw-01.png) · SS / Underworks · 열린 방 · 석재, 금속

- 관찰: 넓은 바닥 위 양옆 작은 조형물과 중앙 여백이 있다.
- 전경과 배경: 앞 뼈무더기와 뒤 큰 벽면, 위 검은 천장이 나뉜다.
- 조명: 천장의 둥근 빛에서 아래로 좁은 광막이 내려온다.
- 제작 패턴: P04, P11, P17 — 목표에 모이는 빛 / 전투방의 넓은 판독 공간 / 비대칭 공간의 무게 배분
- 적용 후보: 유물 획득 지점, 문양의 성소 · 자산 명세 B02, B03, B04, B05, B13
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/e/e3/Screenshot_SS_Underworks_01.png/800px-Screenshot_SS_Underworks_01.png)

### SS-UW-02 중앙 조형물이 바뀐 방

[이미지 보기](images/ss-uw-02.png) · SS / Underworks · 상태 변형 · 석재, 금속

- 관찰: SS-UW-01과 같은 계열 구도에서 바닥의 작은 대상들이 달라진다.
- 전경과 배경: 천장과 뒤 벽의 큰 구조는 유지되어 상태 비교가 쉽다.
- 조명: 중앙의 수직빛을 상태 변화 전후의 공통 기준으로 쓴다.
- 제작 패턴: P04, P19 — 목표에 모이는 빛 / 공간 골격을 유지한 상태 변화
- 적용 후보: 고대 장치 구역, 보스 처치 후 · 자산 명세 B04, B05, B19
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/85/Screenshot_SS_Underworks_02.png/800px-Screenshot_SS_Underworks_02.png)

### SS-UW-03 낮은 길 뒤 둥근 금속문

[이미지 보기](images/ss-uw-03.png) · SS / Underworks · 지역 경계 · 석재, 금속

- 관찰: 긴 바닥 뒤 원형 출입 구조와 작은 표식이 보인다.
- 전경과 배경: 앞 검은 기둥과 뒤 원형 구조의 크기가 다르다.
- 조명: 위쪽 작은 주황 등불과 뒤의 청록 어둠이 대비된다.
- 제작 패턴: P04, P09, P16 — 목표에 모이는 빛 / 지역 문턱과 문양 입구 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B04, B05, B11, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6c/Screenshot_SS_Underworks_03.png/800px-Screenshot_SS_Underworks_03.png)

### SS-UW-04 나무판과 잔해의 어두운 길

[이미지 보기](images/ss-uw-04.png) · SS / Underworks · 수평 통로 · 목재, 석재, 금속

- 관찰: 낮은 길에 판자와 잔해가 기울어져 놓인다.
- 전경과 배경: 앞 검은 식생과 중간 판자, 뒤 흐린 구조가 겹친다.
- 조명: 작은 위쪽 등불만 남겨 바닥의 상면을 읽힌다.
- 제작 패턴: P01, P03, P12 — 검은 지형 속과 읽히는 테두리 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B01, B03, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6c/Screenshot_SS_Underworks_04.png/800px-Screenshot_SS_Underworks_04.png)

### SS-UW-05 기울어진 프레임과 낮은 물가

[이미지 보기](images/ss-uw-05.png) · SS / Underworks · 수평 통로 · 석재, 금속, 물

- 관찰: 작은 벤치형 대상 옆 열린 지면을 큰 기울어진 선이 감싼다.
- 전경과 배경: 앞의 검은 프레임과 뒤의 약한 청록 공간이 나뉜다.
- 조명: 한쪽 위 작은 빛과 넓은 사선 산란광을 분리한다.
- 제작 패턴: P02, P04, P17 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B04, B05
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/6c/Screenshot_SS_Underworks_05.png/800px-Screenshot_SS_Underworks_05.png)

### SS-UW-06 양옆 발판 사이 아래 위험

[이미지 보기](images/ss-uw-06.png) · SS / Underworks · 위험 구간 · 석재, 금속, 가시

- 관찰: 왼쪽 넓은 길과 오른쪽 짧은 턱 아래에 날카로운 잔해가 있다.
- 전경과 배경: 상부 검은 코어가 중앙의 깊은 틈을 강조한다.
- 조명: 좁은 위쪽 빛으로 위·아래 경계를 드러낸다.
- 제작 패턴: P05, P07 — 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B06, B09
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Underworks_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/10/Screenshot_SS_Underworks_06.png/800px-Screenshot_SS_Underworks_06.png)

### SS-CC-01 높은 빈 공간의 종

[이미지 보기](images/ss-cc-01.png) · SS / Choral Chambers · 열린 방 · 금속, 석재, 껍질

- 관찰: 양옆 짧은 발판 사이 큰 빈 공간 위로 종과 구체가 매달린다.
- 전경과 배경: 앞 지면과 뒤 수직으로 큰 흐린 구조가 구분된다.
- 조명: 좁고 긴 따뜻한 광막으로 세로 규모를 만든다.
- 제작 패턴: P03, P05, P06 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B06, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/c/c8/Screenshot_SS_Choral_Chambers_01.png/800px-Screenshot_SS_Choral_Chambers_01.png)

### SS-CC-02 밝은 뒤 울타리와 작은 의자

[이미지 보기](images/ss-cc-02.png) · SS / Choral Chambers · 휴식 포켓 · 석재, 금속

- 관찰: 평평한 길의 작은 의자 주변을 넓게 비운다.
- 전경과 배경: 앞 검은 인물 실루엣과 뒤 큰 창살이 크기로 나뉜다.
- 조명: 부드러운 밝은 뒤 면 앞에 기능점은 어두운 윤곽으로 남는다.
- 제작 패턴: P03, P10, P18 — 중경과 원경의 다른 대비 / 작고 명료한 휴식 포켓 / 밝은 지역에서의 대비 반전
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B03, B12, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/aa/Screenshot_SS_Choral_Chambers_02.png/800px-Screenshot_SS_Choral_Chambers_02.png)

### SS-CC-03 희미한 제단과 높은 문양

[이미지 보기](images/ss-cc-03.png) · SS / Choral Chambers · 목표 노출 · 석재, 금속

- 관찰: 중앙 낮은 제단 위로 높은 문양 선이 모인다.
- 전경과 배경: 상부 검은 천장과 뒤 낮은 청록 면 사이 목표가 놓인다.
- 조명: 작은 따뜻한 위쪽 빛이 중앙 수직 축을 만든다.
- 제작 패턴: P04, P08, P16 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B04, B05, B10, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/29/Screenshot_SS_Choral_Chambers_03.png/800px-Screenshot_SS_Choral_Chambers_03.png)

### SS-CC-04 관 같은 천장 아래 층진 발판

[이미지 보기](images/ss-cc-04.png) · SS / Choral Chambers · 수직 이동 · 석재, 금속

- 관찰: 오른쪽 두 높이의 발판과 왼쪽 낮은 길이 이어진다.
- 전경과 배경: 가까운 검은 줄기와 뒤의 흐린 세로 기둥을 구별한다.
- 조명: 높은 창에서 들어오는 약한 빛이 발판 외곽을 드러낸다.
- 제작 패턴: P03, P05, P12 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B03, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8a/Screenshot_SS_Choral_Chambers_04.png/800px-Screenshot_SS_Choral_Chambers_04.png)

### SS-CC-05 따뜻한 배경의 중앙 의자

[이미지 보기](images/ss-cc-05.png) · SS / Choral Chambers · 휴식 포켓 · 석재, 금속

- 관찰: 큰 문양 판 아래 작은 기능점과 평평한 바닥이 있다.
- 전경과 배경: 양옆 검은 구조와 중앙 뒤의 밝은 면이 대비된다.
- 조명: 작은 촛불과 넓은 주황빛 면을 함께 사용한다.
- 제작 패턴: P04, P10, P16 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/d/d6/Screenshot_SS_Choral_Chambers_05.png/800px-Screenshot_SS_Choral_Chambers_05.png)

### SS-CC-06 천장등 아래 두 검은 기둥

[이미지 보기](images/ss-cc-06.png) · SS / Choral Chambers · 수평 통로 · 석재, 금속, 천

- 관찰: 앞의 두 짧은 검은 기둥 사이에 낮은 작은 물체가 있다.
- 전경과 배경: 앞 기둥과 중간 대상, 뒤 아치의 선명도가 다르다.
- 조명: 위쪽 쌍등불과 한쪽 사선 광막이 겹친다.
- 제작 패턴: P02, P04, P17 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 비대칭 공간의 무게 배분
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B04, B05
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Choral_Chambers_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8b/Screenshot_SS_Choral_Chambers_06.png/800px-Screenshot_SS_Choral_Chambers_06.png)

### SS-WV-01 세로 벽과 천의 깊은 공간

[이미지 보기](images/ss-wv-01.png) · SS / Whispering Vaults · 수평 통로 · 천, 석재, 금속

- 관찰: 평평한 바닥 뒤로 긴 천과 높은 벽면이 이어진다.
- 전경과 배경: 앞 검은 줄기와 뒤의 흐린 세로 면이 층을 만든다.
- 조명: 좁은 수직 대기광이 뒤 공간만 드러낸다.
- 제작 패턴: P02, P03, P13 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/0/02/Screenshot_SS_Whispering_Vaults_01.png/800px-Screenshot_SS_Whispering_Vaults_01.png)

### SS-WV-02 뜨거운 색 장식과 낮은 방

[이미지 보기](images/ss-wv-02.png) · SS / Whispering Vaults · 목표 노출 · 석재, 금속, 천

- 관찰: 작은 바닥 대상 위 한쪽 따뜻한 장식이 걸려 있다.
- 전경과 배경: 앞 검은 물체와 뒤의 낮은 청록 면이 구별된다.
- 조명: 한쪽 작은 주황빛과 넓은 어두운 공간이 대비된다.
- 제작 패턴: P04, P08, P17 — 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 비대칭 공간의 무게 배분
- 적용 후보: 유물 획득 지점, 보상 포켓 · 자산 명세 B02, B03, B04, B05, B10
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8d/Screenshot_SS_Whispering_Vaults_02.png/800px-Screenshot_SS_Whispering_Vaults_02.png)

### SS-WV-03 매달린 등 아래 작은 의자

[이미지 보기](images/ss-wv-03.png) · SS / Whispering Vaults · 휴식 포켓 · 석재, 금속

- 관찰: 중앙 의자 위 하나의 등불과 큰 천장 여백이 있다.
- 전경과 배경: 검은 외곽과 뒤 따뜻한 작은 면이 포켓을 만든다.
- 조명: 중심이 밝고 외곽으로 약해지는 주황 국소빛이다.
- 제작 패턴: P04, P10 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3d/Screenshot_SS_Whispering_Vaults_03.png/800px-Screenshot_SS_Whispering_Vaults_03.png)

### SS-WV-04 여러 천장 틈의 세로 광막

[이미지 보기](images/ss-wv-04.png) · SS / Whispering Vaults · 복층 공간 · 석재, 금속

- 관찰: 높은 공간의 위쪽에 큰 광원 틈들이 나란히 놓인다.
- 전경과 배경: 상부 검은 실루엣과 뒤의 흐린 긴 벽이 나뉜다.
- 조명: 여러 수직 광막을 떨어뜨려 층과 간격을 보여준다.
- 제작 패턴: P03, P04, P05 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B04, B05, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5b/Screenshot_SS_Whispering_Vaults_04.png/800px-Screenshot_SS_Whispering_Vaults_04.png)

### SS-WV-05 중앙 문양과 여러 작은 등

[이미지 보기](images/ss-wv-05.png) · SS / Whispering Vaults · 랜드마크 · 석재, 금속

- 관찰: 중앙 장치형 문양 주위에 작은 등불들이 대칭으로 놓인다.
- 전경과 배경: 어두운 전경과 중간 문양, 뒤 세로벽이 겹친다.
- 조명: 작은 주황 광원 군집과 중앙 위의 넓은 빛을 구별한다.
- 제작 패턴: P04, P06, P16 — 목표에 모이는 빛 / 장치 경로와 작동부의 명료함 / 방마다 하나의 큰 기억점
- 적용 후보: 문양의 성소 · 자산 명세 B04, B05, B07, B08, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a8/Screenshot_SS_Whispering_Vaults_05.png/800px-Screenshot_SS_Whispering_Vaults_05.png)

### SS-WV-06 비대칭 틈 아래 작은 벤치

[이미지 보기](images/ss-wv-06.png) · SS / Whispering Vaults · 휴식 포켓 · 석재, 금속

- 관찰: 오른쪽으로 열린 좁은 포켓에 벤치가 있고 위로 등이 매달린다.
- 전경과 배경: 왼쪽 큰 검은 코어와 오른쪽 작은 기능점이 대비된다.
- 조명: 따뜻한 국소 등불로 좁은 공간의 중심을 표시한다.
- 제작 패턴: P01, P04, P10 — 검은 지형 속과 읽히는 테두리 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B01, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whispering_Vaults_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/87/Screenshot_SS_Whispering_Vaults_06.png/800px-Screenshot_SS_Whispering_Vaults_06.png)

### SS-WH-01 거대한 가시 고리와 작은 빛

[이미지 보기](images/ss-wh-01.png) · SS / Whiteward · 위험 구간 · 가시, 석재, 금속

- 관찰: 큰 원형 가시 구조 옆 낮은 길에 작은 발광체가 모인다.
- 전경과 배경: 앞의 굵은 가시 고리와 뒤 흐린 청록 면이 분리된다.
- 조명: 작은 분홍빛은 큰 어두운 위험 실루엣과 대비된다.
- 제작 패턴: P07, P15, P16 — 안전면과 위험면의 다른 형태 / 적 실루엣과 공격 방향 / 방마다 하나의 큰 기억점
- 적용 후보: 고대 장치 구역, 보스 접근 구간 · 자산 명세 B09, B16, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whiteward_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/71/Screenshot_SS_Whiteward_01.png/800px-Screenshot_SS_Whiteward_01.png)

### SS-WH-02 둥근 잔해가 쌓인 낮은 길

[이미지 보기](images/ss-wh-02.png) · SS / Whiteward · 수평 통로 · 껍질, 석재

- 관찰: 화면 아래 둥근 껍질 더미와 낮은 보행선이 이어진다.
- 전경과 배경: 위 검은 코어와 아래 잔해, 뒤 녹색 공기가 나뉜다.
- 조명: 전체는 어둡게 유지하고 잔해 외곽만 약하게 드러낸다.
- 제작 패턴: P01, P12, P20 — 검은 지형 속과 읽히는 테두리 / 재질의 군집과 빈 구간 / 시야 제한과 집중 연출
- 적용 후보: 중앙 통로 · 자산 명세 B01, B14, B20
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whiteward_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/55/Screenshot_SS_Whiteward_02.png/800px-Screenshot_SS_Whiteward_02.png)

### SS-WH-03 천장빛 아래 작은 몸체

[이미지 보기](images/ss-wh-03.png) · SS / Whiteward · 전투 공간 · 석재, 유기체

- 관찰: 낮은 길 위 길쭉한 작은 형체가 놓이고 위가 밝다.
- 전경과 배경: 앞 검은 큰 기둥과 밝은 작은 몸체가 크기로 분리된다.
- 조명: 좁은 흰 천장빛 안에서 몸체의 밝은 면이 읽힌다.
- 제작 패턴: P04, P11, P15 — 목표에 모이는 빛 / 전투방의 넓은 판독 공간 / 적 실루엣과 공격 방향
- 적용 후보: 전투방, 보스방 · 자산 명세 B04, B05, B13, B16
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whiteward_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a1/Screenshot_SS_Whiteward_03.png/800px-Screenshot_SS_Whiteward_03.png)

### SS-WH-04 밝은 틈과 여러 겹의 구조

[이미지 보기](images/ss-wh-04.png) · SS / Whiteward · 복층 공간 · 석재, 금속, 껍질

- 관찰: 상부 밝은 원형 틈 아래 여러 층의 장식 구조가 있다.
- 전경과 배경: 앞의 검은 세로 구조와 뒤의 큰 둥근 면이 겹친다.
- 조명: 상부 흰 빛이 아래로 갈수록 약해진다.
- 제작 패턴: P03, P04, P05 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B03, B04, B05, B06
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whiteward_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/a/a7/Screenshot_SS_Whiteward_04.png/800px-Screenshot_SS_Whiteward_04.png)

### SS-WH-06 기울어진 큰 물체의 작은 방

[이미지 보기](images/ss-wh-06.png) · SS / Whiteward · 보상 포켓 · 석재, 금속

- 관찰: 오른쪽 큰 기울어진 구조와 왼쪽 작은 인물이 좁은 방에 있다.
- 전경과 배경: 큰 검은 코어 안 작은 활동 공간만 드러난다.
- 조명: 뒤의 약한 청록빛이 큰 물체의 외곽을 남긴다.
- 제작 패턴: P01, P08, P16 — 검은 지형 속과 읽히는 테두리 / 보상의 선노출과 우회 경로 / 방마다 하나의 큰 기억점
- 적용 후보: 보상 포켓, 유물 획득 지점 · 자산 명세 B01, B10, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Whiteward_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/81/Screenshot_SS_Whiteward_06.png/800px-Screenshot_SS_Whiteward_06.png)

### SS-HH-01 큰 원형 장식과 밝은 수면

[이미지 보기](images/ss-hh-01.png) · SS / High Halls · 랜드마크 · 금속, 석재, 물

- 관찰: 매달린 거대 원형 구조 아래 수평 물면이 펼쳐진다.
- 전경과 배경: 앞 큰 장식과 뒤 흐린 기둥의 대비가 다르다.
- 조명: 넓은 따뜻한 배경광과 수면 반사 같은 밝은 띠가 겹친다.
- 제작 패턴: P03, P04, P16 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5a/Screenshot_SS_High_Halls_01.png/800px-Screenshot_SS_High_Halls_01.png)

### SS-HH-02 둥근 누각과 중앙 광원

[이미지 보기](images/ss-hh-02.png) · SS / High Halls · 랜드마크 · 석재, 금속

- 관찰: 높은 누각 아래 작은 가운데 구조와 수직 기둥들이 있다.
- 전경과 배경: 앞 프레임과 뒤 흐린 도시 구조가 여러 깊이로 나뉜다.
- 조명: 누각 중앙의 작은 빛을 넓은 회색 대기광과 구분한다.
- 제작 패턴: P03, P04, P16 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B04, B05, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fe/Screenshot_SS_High_Halls_02.png/800px-Screenshot_SS_High_Halls_02.png)

### SS-HH-03 작은 벤치와 쌍등불

[이미지 보기](images/ss-hh-03.png) · SS / High Halls · 휴식 포켓 · 석재, 금속

- 관찰: 큰 검은 지형 사이 낮은 벤치가 있고 두 등이 위에 놓인다.
- 전경과 배경: 앞 검은 하단 가림과 뒤 청록 벽이 포켓을 만든다.
- 조명: 두 작은 따뜻한 등불의 간격이 기능점을 감싼다.
- 제작 패턴: P02, P04, P10 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/1/1d/Screenshot_SS_High_Halls_03.png/800px-Screenshot_SS_High_Halls_03.png)

### SS-HH-04 커튼 뒤 부드러운 형체

[이미지 보기](images/ss-hh-04.png) · SS / High Halls · 수평 통로 · 천, 석재, 금속

- 관찰: 긴 검은 천이 위에서 내려와 뒤의 큰 형체를 부분적으로 가린다.
- 전경과 배경: 가까운 천은 검고 뒤 구조는 낮은 대비로 흐리다.
- 조명: 낮은 청록 주변광으로 커튼 사이 틈만 드러낸다.
- 제작 패턴: P02, P03, P12 — 근접 전경과 중앙 시야 여백 / 중경과 원경의 다른 대비 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B02, B03, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f3/Screenshot_SS_High_Halls_04.png/800px-Screenshot_SS_High_Halls_04.png)

### SS-HH-05 긴 실이 비스듬히 지난 세로 틈

[이미지 보기](images/ss-hh-05.png) · SS / High Halls · 수직 이동 · 실, 석재

- 관찰: 좁은 발판 옆에 매우 긴 사선 실 무리가 지난다.
- 전경과 배경: 앞의 가는 선과 뒤 밝은 긴 틈이 크기로 대비된다.
- 조명: 위쪽 빛이 실의 일부를 따뜻하게 강조한다.
- 제작 패턴: P05, P06, P13 — 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 대기광과 입자의 깊이
- 적용 후보: 중앙 통로, 하강 통로 · 자산 명세 B06, B07, B08, B15
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/69/Screenshot_SS_High_Halls_05.png/800px-Screenshot_SS_High_Halls_05.png)

### SS-HH-06 위 장식빛 아래 작은 중앙 발판

[이미지 보기](images/ss-hh-06.png) · SS / High Halls · 열린 방 · 석재, 금속

- 관찰: 넓은 바닥과 중앙 짧은 발판 위로 큰 뒤 장식이 보인다.
- 전경과 배경: 앞의 작은 발판과 뒤의 큰 흐린 원형 무늬가 나뉜다.
- 조명: 위의 따뜻한 장식빛과 어두운 앞 공간이 대비된다.
- 제작 패턴: P03, P11, P16 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 방마다 하나의 큰 기억점
- 적용 후보: 전투방, 보스방 · 자산 명세 B03, B13, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_High_Halls_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/3e/Screenshot_SS_High_Halls_06.png/800px-Screenshot_SS_High_Halls_06.png)

### SS-CK-01 대칭 장치와 높은 빛

[이미지 보기](images/ss-ck-01.png) · SS / Cogwork Core · 장치 공간 · 금속, 석재

- 관찰: 양옆 큰 장치가 중앙의 낮은 길을 감싼다.
- 전경과 배경: 앞 선명한 기둥과 뒤 흐린 원형 무늬가 층을 만든다.
- 조명: 천장 틈의 넓은 빛과 작은 밝은 점들이 세로로 모인다.
- 제작 패턴: P03, P04, P06 — 중경과 원경의 다른 대비 / 목표에 모이는 빛 / 장치 경로와 작동부의 명료함
- 적용 후보: 고대 장치 구역 · 자산 명세 B03, B04, B05, B07, B08
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/3/30/Screenshot_SS_Cogwork_Core_01.png/800px-Screenshot_SS_Cogwork_Core_01.png)

### SS-CK-02 중앙에 놓인 큰 철망

[이미지 보기](images/ss-ck-02.png) · SS / Cogwork Core · 장치 공간 · 금속, 사슬, 석재

- 관찰: 큰 새장형 구조가 중앙 발판 위에 놓인다.
- 전경과 배경: 가는 철망과 뒤 큰 둥근 무늬의 선명도가 다르다.
- 조명: 중앙의 약한 청록빛으로 구조의 외곽을 읽힌다.
- 제작 패턴: P06, P12, P16 — 장치 경로와 작동부의 명료함 / 재질의 군집과 빈 구간 / 방마다 하나의 큰 기억점
- 적용 후보: 고대 장치 구역 · 자산 명세 B07, B08, B14, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f1/Screenshot_SS_Cogwork_Core_02.png/800px-Screenshot_SS_Cogwork_Core_02.png)

### SS-CK-03 어두운 방의 큰 잔해

[이미지 보기](images/ss-ck-03.png) · SS / Cogwork Core · 랜드마크 · 금속, 석재

- 관찰: 중앙 큰 잔해를 낮은 바닥과 양옆 기둥이 감싼다.
- 전경과 배경: 전경 기둥과 뒤 잔해 더미가 크기 차를 만든다.
- 조명: 강한 광원 없이 낮은 청록빛으로 윤곽만 남긴다.
- 제작 패턴: P03, P11, P16 — 중경과 원경의 다른 대비 / 전투방의 넓은 판독 공간 / 방마다 하나의 큰 기억점
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B13, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/f6/Screenshot_SS_Cogwork_Core_03.png/800px-Screenshot_SS_Cogwork_Core_03.png)

### SS-CK-04 등불 아래 작은 쉼터

[이미지 보기](images/ss-ck-04.png) · SS / Cogwork Core · 휴식 포켓 · 금속, 석재

- 관찰: 오른쪽 높은 지면 위 작은 벤치와 위의 등불이 놓인다.
- 전경과 배경: 오른쪽 기둥과 뒤 큰 기계 무늬가 겹친다.
- 조명: 작은 흰 등불이 쉬는 지점을 분명하게 표시한다.
- 제작 패턴: P04, P10, P16 — 목표에 모이는 빛 / 작고 명료한 휴식 포켓 / 방마다 하나의 큰 기억점
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B04, B05, B12, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/6/65/Screenshot_SS_Cogwork_Core_04.png/800px-Screenshot_SS_Cogwork_Core_04.png)

### SS-CK-05 톱니 둘레의 넓은 전투면

[이미지 보기](images/ss-ck-05.png) · SS / Cogwork Core · 장치 공간 · 금속, 석재

- 관찰: 긴 평평한 바닥과 위의 큰 톱니 구조가 열린 가운데를 감싼다.
- 전경과 배경: 앞의 가는 기둥과 뒤의 부드러운 기계 면이 분리된다.
- 조명: 좁은 사선빛으로 가운데를 강조하고 둘레는 어둡게 둔다.
- 제작 패턴: P04, P06, P11 — 목표에 모이는 빛 / 장치 경로와 작동부의 명료함 / 전투방의 넓은 판독 공간
- 적용 후보: 고대 장치 구역 · 자산 명세 B04, B05, B07, B08, B13
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/5/5b/Screenshot_SS_Cogwork_Core_05.png/800px-Screenshot_SS_Cogwork_Core_05.png)

### SS-CK-06 거대 기어 앞 작은 발판

[이미지 보기](images/ss-ck-06.png) · SS / Cogwork Core · 수직 이동 · 금속, 석재

- 관찰: 오른쪽 짧은 발판 뒤에 화면보다 큰 기어가 놓인다.
- 전경과 배경: 실제 앞 난간은 선명하고 뒤 기어는 흐리고 거대하다.
- 조명: 밝은 뒤 면 앞에 어두운 발판의 윤곽을 남긴다.
- 제작 패턴: P03, P05, P06, P18 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 장치 경로와 작동부의 명료함 / 밝은 지역에서의 대비 반전
- 적용 후보: 고대 장치 구역, 중앙 통로 · 자산 명세 B03, B06, B07, B08, B18
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Cogwork_Core_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/9/9d/Screenshot_SS_Cogwork_Core_06.png/800px-Screenshot_SS_Cogwork_Core_06.png)

### SS-ME-01 이끼 양옆 벽과 중앙 문

[이미지 보기](images/ss-me-01.png) · SS / Memorium · 복층 공간 · 이끼, 석재, 금속

- 관찰: 양옆 높은 이끼벽 사이 중앙 낮은 문과 작은 발판들이 있다.
- 전경과 배경: 검은 지형 속과 선명한 이끼 테두리, 뒤 숲이 분리된다.
- 조명: 중앙 위의 약한 빛과 왼쪽 붉은 가시가 다른 역할을 한다.
- 제작 패턴: P01, P05, P07, P09 — 검은 지형 속과 읽히는 테두리 / 다음 착지면이 보이는 수직 이동 / 안전면과 위험면의 다른 형태 / 지역 문턱과 문양 입구
- 적용 후보: 문양의 성소, 중앙 통로 · 자산 명세 B01, B06, B09, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_01.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/b7/Screenshot_SS_Memorium_01.png/800px-Screenshot_SS_Memorium_01.png)

### SS-ME-02 큰 천장등 아래 작은 벤치

[이미지 보기](images/ss-me-02.png) · SS / Memorium · 휴식 포켓 · 석재, 금속, 잎

- 관찰: 낮은 바닥 위 벤치를 작게 두고 큰 등이 위를 차지한다.
- 전경과 배경: 앞 큰 검은 줄기와 뒤 밝은 공간이 층을 만든다.
- 조명: 한 개의 넓은 천장빛이 벤치로 내려온다.
- 제작 패턴: P02, P04, P10 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 작고 명료한 휴식 포켓
- 적용 후보: 전투 후 휴식 지점, 보상 포켓 · 자산 명세 B02, B04, B05, B12
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_02.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/b/be/Screenshot_SS_Memorium_02.png/800px-Screenshot_SS_Memorium_02.png)

### SS-ME-03 짧은 길 끝의 수직 경계

[이미지 보기](images/ss-me-03.png) · SS / Memorium · 지역 경계 · 석재, 금속, 잎

- 관찰: 왼쪽 낮은 길 끝에서 오른쪽 큰 밝은 틈이 열린다.
- 전경과 배경: 왼쪽의 검은 덩어리와 뒤의 큰 밝은 세로 면이 대비된다.
- 조명: 한쪽의 따뜻한 대기광이 출구 방향을 만든다.
- 제작 패턴: P03, P05, P09 — 중경과 원경의 다른 대비 / 다음 착지면이 보이는 수직 이동 / 지역 문턱과 문양 입구
- 적용 후보: 중앙 통로, 문양의 성소 · 자산 명세 B03, B06, B11
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_03.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/7/7e/Screenshot_SS_Memorium_03.png/800px-Screenshot_SS_Memorium_03.png)

### SS-ME-04 기둥과 뿌리가 감싼 밝은 대상

[이미지 보기](images/ss-me-04.png) · SS / Memorium · 목표 노출 · 석재, 금속, 이끼

- 관찰: 중앙 높은 대상 아래 녹색 바닥이 작은 안전 공간을 만든다.
- 전경과 배경: 앞 검은 기둥 사이로 중앙 대상과 뒤 뿌리가 겹친다.
- 조명: 대상 위쪽 따뜻한 빛과 아래 초록 반사색이 나뉜다.
- 제작 패턴: P02, P04, P08, P16 — 근접 전경과 중앙 시야 여백 / 목표에 모이는 빛 / 보상의 선노출과 우회 경로 / 방마다 하나의 큰 기억점
- 적용 후보: 유물 획득 지점, 문양의 성소 · 자산 명세 B02, B04, B05, B10, B17
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_04.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/f/fd/Screenshot_SS_Memorium_04.png/800px-Screenshot_SS_Memorium_04.png)

### SS-ME-05 매달린 관과 가로 통로

[이미지 보기](images/ss-me-05.png) · SS / Memorium · 수평 통로 · 금속, 석재, 실

- 관찰: 여러 수직 관형 물체가 낮은 길 위 다른 높이에 놓인다.
- 전경과 배경: 앞 검은 기둥과 중간 매달린 물체, 뒤 낮은 대기층이 겹친다.
- 조명: 작고 약한 따뜻한 빛을 간격을 두고 반복한다.
- 제작 패턴: P03, P06, P12 — 중경과 원경의 다른 대비 / 장치 경로와 작동부의 명료함 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로 · 자산 명세 B03, B07, B08, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_05.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/2/22/Screenshot_SS_Memorium_05.png/800px-Screenshot_SS_Memorium_05.png)

### SS-ME-06 두 층 사이 작은 분홍 등

[이미지 보기](images/ss-me-06.png) · SS / Memorium · 복층 공간 · 석재, 금속, 뿌리

- 관찰: 위의 긴 보행면과 아래 열린 공간 사이로 줄기가 내려온다.
- 전경과 배경: 위의 선명한 발판과 아래 뒤 구조가 다른 깊이다.
- 조명: 작은 분홍빛이 넓은 청록 어둠 속 중심이 된다.
- 제작 패턴: P04, P05, P12 — 목표에 모이는 빛 / 다음 착지면이 보이는 수직 이동 / 재질의 군집과 빈 구간
- 적용 후보: 중앙 통로, 고대 장치 구역 · 자산 명세 B04, B05, B06, B14
- [출처 페이지](https://hollowknight.wiki/w/File:Screenshot_SS_Memorium_06.png) · [제공 이미지](https://cdn.wikimg.net/en/hkwiki/images/thumb/8/8e/Screenshot_SS_Memorium_06.png/800px-Screenshot_SS_Memorium_06.png)

