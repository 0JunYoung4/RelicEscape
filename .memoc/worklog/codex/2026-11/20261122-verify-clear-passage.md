# 전투방 전멸 후 하강 통로 확인

- 사용자 요청: 몬스터를 다 잡으면 아래 통로 개방.
- 기존 게임 로직이 이미 연결돼 추가 코드 변경 없이 재검증했다.
- 중앙에서 생성·등장 완료 후 실제 베기 판정18회로 골렘2/공벌레2 HP0 확인. 마지막 처치 전 개방하지 않으며 전멸 후0.7초 개방, 중앙에서 내려가 바닥-960 안전 착지 확인.
- 관련22개 검사 통과. 실제 SDL 전멸 개방 GIF와 PNG를 archive/unused-assets/2026-11-23/docs/combat-clear-passage-opening.gif 및 combat-clear-passage-open.png로 저장.
