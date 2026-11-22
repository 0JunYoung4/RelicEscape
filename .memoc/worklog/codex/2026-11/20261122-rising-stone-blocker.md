# 바닥에서 오르내리는 전투방 돌벽

- 요청: 철창 표현이 부자연스러워 돌벽이 올라왔다 내려가도록 변경, 막을 벽 이미지 제작.
- 기존 방/돌기둥을 참조해 내장 imagegen으로 투명 돌벽 생성. 원본·알파 경계 크롭 PNG·정확한 프롬프트·JSON을 assets/terrain/moss-combat-door-blocker-v1*로 저장.
- lower_caves.py에서 금속 도형을 돌벽 이미지로 대체. 위쪽 부분만 노출시키며 지면에서0.55초 상승/하강. 기존 충돌·유물 제한·전멸/재입장 동작 유지.
- 관련22개 테스트 통과. 실제 SDL에서 열림/봉쇄/상승·하강 화면을 렌더하고 archive/unused-assets/2026-11-23/docs/combat-stone-wall-motion.gif로 확인.
