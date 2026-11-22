# 골렘 바닥 등장 애니메이션

2026-11-22, Codex.

- 기존 idle-left-v1와 walk-left-v2를 참조해 내장 imagegen으로 투명4×4/16프레임 등장 시트 제작. 균열→큰 주먹 두 개로 바닥 지지→머리/어깨 끌어올림→등 수정→짧은 다리→기존 주먹 걸음 중립. 프레임당120ms, 총1.92초.
- 표시 높이140과 본체 접지 기준점을 JSON에 기록했다. 생성 원본·정확한 프롬프트 보존, 그림 편집 없이 프레임/접지/인코딩만 후처리. 확대 GIF는 실제 발판 위에서 등장→기존 이동까지 재생하며 투명 APNG도 제공한다.
- CrystalGolem에 active/emerge phase와 begin_emergence 추가. 등장 중 이동/방향 변경/검 피격/접촉 피해/수정 발사 보류. Health의 기존 emerge 제외 규칙 공유. 기존 공격 예약을 비우고, 종료 후 좌우 초기 대기 보존 및 최소0.65초 준비 시간을 둔다.
- 전투방 중앙 조우 때 골렘2마리와 공벌레2마리 모두 등장 모션을 시작한다. 방 왕복은 시간 유지, 중복 호출은 시간 리셋 금지, 죽은 적 부활 없음. 기존 갤러리 공벌레·전멸 후 개방 정책 유지.
- 신규4개:30/60/120fps 위치·발판·방향 고정/기존 순찰 복귀, 등장 중 검·접촉 피해와 종료 후 복구, 예약 공격 취소·중복 시작·죽음, 중앙 조우/아트 선택/왕복 유지/이동 연결. 관련31개·전체142개 검사 통과. py_compile·git diff --check 통과.
- assets/sprites/enemies/stone-crystal-golem-emerge-left-v1 PNG/JSON/프롬프트/GIF/APNG와 docs/golem-emergence-in-game.gif·PNG 및 contact-sheet 저장. 확대·실제 방 렌더를 검토했다.
