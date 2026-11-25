---
memoc: true
type: project
scope: environment-art
updated: 2026-11-25
status: active
tags:
  - memoc/wiki
  - environment-art
---
# 전투방 중경 전경과 조명

전투방 전용 원경은 오른쪽의 부서진 석조 고리와 뿌리, 왼쪽 위 틈빛과 먼 안개를 담는다. 중앙 공중은 남청색으로 비워 수정탄이 읽히게 했다. 바닥 양끝에는 호박빛 열매가 자라고, 검은 천장 뿌리가 높은 시점에서 화면을 감싼다. [제작 참고 가이드](../../../docs/reference-production-guide.md)

`combat_scenery.py`의 `CombatScenery`는 화폭 전체를 덮는 원경 PNG, 투명 식생 PNG, 천장 뿌리 PNG를 사용한다. `MossCaveArt.combat_scenery()`는 전투방에서 지연 로드한다. 원경은 카메라가 움직일 때 지형보다 느리게 이동한다. 전투방 포자는 8개이며 이끼 통로의 기본값은 32개다.

배경 명암은 낮은 입구까지 이어져 벽 안쪽 면에 수직 이음새가 생기지 않게 한다. 모든 새 효과는 지면 아래를 그리지 않는다. 근접 식생은 월드 천장에 고정하고 천장보다 위는 잘라 화면 고정·임계점 전환을 방지한다. 호출자의 클립과 블렌드를 복원한다.

전투방 중앙에 들어서면 입구 돌벽이 먼저 닫힌다. 바닥 공벌레 두 마리를 쓰러뜨리면 중앙 상단 발판에서 골렘 두 마리가 등장한다. 마지막 골렘 처치 뒤 0.5초 정적과 0.6초 틈새 청록빛을 거쳐 돌벽과 바닥 덮개가 열린다. 카메라는 이때 상단 발판과 덮개를 같이 담는다. 하강로 내부는 구멍에 접근하면 서서히 드러난다.

렌더 회귀 검사는 공유 배경 색조 복원, 원경·식생의 지면 아래 누출 방지, SDL 상태 복원, 카메라 이동 중 전경 위치 정렬을 확인한다. 실제 골렘 발사 코드로 생성한 수정탄과 덮개 틈빛을 새 원경에서 확인했다.

## Related

- [프로젝트 허브](README.md)
- [미술 방향과 자산 프롬프트](../../../docs/environment-art-direction.md)
- [전투방 단계별 조우](../../worklog/codex/2026-11/20261125-combat-room-waves.md)
- [하강로 개방 연출](../../worklog/codex/2026-11/20261125-combat-exit-light-cue.md)
- [전투방 석조 고리 원경과 식생](../../worklog/codex/2026-11/20261125-combat-relic-grotto.md)
- [녹색 거리 조사](../knowledge/greenpath-art-study.md)
- [최신 전투 시야 작업](../../worklog/codex/2026-11/20261123-combat-readability.md)
- [이전 전투방 미술 작업](../../worklog/codex/2026-11/20261123-combat-atmosphere.md)
