# 돌벽과 기존 문틀 정렬

- 사용자 요청: 올라오는 돌벽을 기존 맵 벽에 맞추거나 통로 중간으로 이동. 기존 문틀에 맞추는 안을 적용했다.
- 방 안쪽20·문틀 위4 돌출 제거. 폭112 돌벽 오른쪽 면은 COMBAT_LEFT_WALL, 상단은 COMBAT_DOOR_HEIGHT. 이미지/충돌/먼지 범위 모두 COMBAT_ENTRANCE_BARRIER를 사용한다.
- 기존 봉쇄·유물 우회 차단·먼지·화면 진동 유지. 관련 전투방22개/효과4개 검사 통과.
- 실제 SDL 정렬 화면 archive/unused-assets/2026-11-23/docs/combat-stone-wall-aligned.png와 locked/current-layout/weight GIF 갱신·검토.
