# 첫 맵 하단 연습길 오브젝트 이미지

- 요청 범위: 첫 맵 전투방 이후 아래로 내려온 뒤 하단 연습길을 지나 왼쪽 첫 보스 B1에 도달하는 구간. 최초 넓게 해석한 맵2·최종 보스 방향은 사용자 정정으로 제외했다.
- 내장 image_gen으로 착지 지점 잔해·벽점프 돌기둥·짧은 돌다리·가시 덩굴·길잡이 석등·B1 입구 아치6종 생성. 아치 투명 경계 편집 전 입력도 보관.
- 저장: `assets/structures/map1-lower-route/`. 한국어 README·6개 정확 프롬프트·manifest·생성 출처. `docs/environment-art-direction.md` 연결.
- 기준: 기존 green-cavern-ground-pillar-v2·relic-acquisition-shrine-v1, 가시는 기존 mutant-floor-spikes-v1. HK-GP18/HK-CT-05/SS-MG-02/SS-MG-03/SS-MF-04 실제 열람 후 식생 군집·착지 경계·기둥 실루엣·국소 안전 조명을 반영.
- 검증: 최종6개 PNG 디코드·RGBA 알파 범위/투명 픽셀·파일/프롬프트 존재·생성 출력과 SHA256 동일 확인, 전부 시각 검토. 원본 알파 보존, 가장자리 약한 반투명 표현 포함.
- 게임 배치·크기·충돌·체크포인트는 미구현. 석등은 장식이며 회복/저장 기능을 확정하지 않음. 게임 소스 미변경으로 게임 테스트는 실행하지 않음.
- memoc search/grep/work 래퍼는 npx 부재로 실행 실패, 관련 에이전트 메모리만 직접 갱신.
