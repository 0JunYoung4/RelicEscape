# 첫 맵 하단 연습길 오브젝트

범위는 **전투방 이후 하강 통로 착지 → 왼쪽 하단 연습길 → 첫 보스 B1 직전**이다. [승인 지도](../../../docs/world-map-progress-2026-11-23.png)와 [기획 6절](../../../docs/INITIAL_DESIGN.md)을 기준으로 만들었다.

기존 이끼 동굴의 어두운 청록색 돌·둥근 잎·뿌리와 첫 유물 제단의 육각 홈을 연결했다. 내장 image_gen으로 생성한 개별 투명 PNG 6종이며 원본 알파를 그대로 보존한다. 가장자리의 약한 반투명 픽셀도 유지했다. 게임 배치·충돌·적·체크포인트 동작은 아직 연결하지 않은 이미지 시안이다.

| 동선 | 오브젝트 | 용도 | 이미지 | 생성 프롬프트 |
| --- | --- | --- | --- | --- |
| 1 | 착지 지점 폐기둥 잔해 | 전투방 하강 통로의 안전 착지면 뒤쪽 | [PNG](lower-cave-landing-rubble-v1.png) | [프롬프트](lower-cave-landing-rubble-v1.prompt.txt) |
| 2 | 벽점프 연습 돌기둥 | 하단 연습길의 짧은 고저차 구간 | [PNG](lower-cave-walljump-pillar-v1.png) | [프롬프트](lower-cave-walljump-pillar-v1.prompt.txt) |
| 3 | 짧은 돌다리 발판 | 하단 연습길의 작은 단차·가시 구간 위쪽 | [PNG](lower-cave-stone-bridge-v1.png) | [프롬프트](lower-cave-stone-bridge-v1.prompt.txt) |
| 4 | 하단 연습길 가시 덩굴 | 유물 설치·복귀를 연습하는 짧은 위험 구간 | [PNG](lower-cave-thorn-bed-v1.png) | [프롬프트](lower-cave-thorn-bed-v1.prompt.txt) |
| 5 | 보스 전실 길잡이 석등 | B1 직전 안전 공간의 벽 쪽 | [PNG](lower-cave-safe-waymarker-v1.png) | [프롬프트](lower-cave-safe-waymarker-v1.prompt.txt) |
| 6 | 첫 보스 B1 입구 폐아치 | 하단 연습길 왼쪽 끝·B1 안전 공간과 보스방 경계 | [PNG](lower-cave-b1-entrance-v1.png) | [프롬프트](lower-cave-b1-entrance-v1.prompt.txt) |

착지 잔해는 안전 착지면 뒤에 두고, 연습길에서는 기둥·돌다리·가시를 짧은 단차와 유물 설치/복귀 연습에 맞춰 배치할 수 있다. 석등의 왼쪽 표시는 B1 방향을 안내하며, 입구 아치는 보스방과 전실의 시각적 경계다. 석등에 회복·저장 기능을 추가하는 뜻은 아니다. 실제 이동 거리·발판 높이·가시 판정은 플레이 구현 단계에서 정한다.

[자산 명세](manifest.json)에 이미지 크기·알파 범위·해시·참고 ID·반영 원리를 기록했다. [제작 참고 가이드](../../../docs/reference-production-guide.md)의 HK-GP18·HK-CT-05·SS-MG-02·SS-MG-03·SS-MF-04를 실제로 열어 식생 군집, 안전 착지면, 높은 기둥 실루엣과 작은 길잡이 조명을 확인했다. 원작의 외형·벤치·캐릭터는 게임 자산으로 사용하지 않는다.

B1 아치의 `-source.png`는 투명 경계 편집 전 입력 원본이다. 그 밖의 최종 PNG는 생성 결과와 같은 파일이다. 프롬프트와 생성 출처는 각각 동명 `.prompt.txt`와 [출처 목록](generation-sources.json)에 보관한다.

A파트 버튼실에는 [상승 레일 뒤 폐기둥](lower-cave-lift-support-v1.png)을 별도로 추가했다. [A파트 환경 시안](../../concepts/map1-lower-route-a-v1.md)에서 사용 위치와 원경을 함께 볼 수 있다.

