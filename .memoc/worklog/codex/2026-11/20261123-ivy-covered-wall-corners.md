# 벽 모서리를 덮는 덩굴

- 요청: 각진 벽 모서리를 덩굴 등으로 자연스럽게 가림.
- 기존 벽 이미지를 바꾸지 않고 내장 imagegen으로 투명 코너 덩굴1종 추가. 원본1024×1536, 크롭(57,33,880,1128), 고정점(123,87). PNG/JSON/정확한 프롬프트 저장.
- draw_corner는 고정점 기준 좌우/상하 반전과 배율로 문틀 끝, 벽-천장/바닥, 벽에 붙은 발판, 기둥 윗모서리에 적용한다. 장식은 캐릭터/몬스터 뒤에 그려 가독성 유지.
- 하강 바닥의 작은 덩굴은 기존 접근 밝기와 같이 표시. 충돌·벽3배·발판 이미지/배치·덮개 동작·시작 동굴/착지방 보존 유지.
- 관련28개(22.205초), 컴파일·diff 검사 통과. 실제 SDL 전체 방·문틀 확대·이끼 기둥 화면 검토.
- 미리보기: docs/green-corner-foliage-combat.png, green-corner-foliage-entry.png, green-corner-foliage-gallery.png.

생성 파일(내장 imagegen):

- [덩굴 PNG](../../../../assets/terrain/green-cavern-corner-ivy-v1.png)
- [정확한 프롬프트](../../../../assets/terrain/green-cavern-corner-ivy-v1.prompt.txt)
