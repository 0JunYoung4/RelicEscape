---
memoc: true
type: project
scope: environment-art
updated: 2026-11-23
status: active
tags:
  - memoc/wiki
  - environment-art
---
# 전투방 중경 전경과 조명

현재 전투방은 중경 폐아치의 대비를 낮추고, 수정탄이 지나가는 공중을 남청색으로 눌렀다. 오른쪽 위의 짧은 사선 빛이 공중 위에서 희미해지고, 바닥의 옅은 대기광이 공벌레 등판 뒤에 깔린다. 월드 천장에 고정된 잎과 뿌리를 짧게 만들어 플레이 공간의 가림을 줄였다. [제작 참고 가이드](../../../docs/reference-production-guide.md)

`combat_scenery.py`의 `CombatScenery`가 기존 투명 PNG 2종과 SDL 알파 메시로 그린다. `MossCaveArt.combat_scenery()`는 지연 로드하며 `lower_caves.py` 전투방에서 호출한다. 전투방 원경은 색조 120/145/178을 적용한 뒤 텍스처 색조를 복원한다. 전투방 포자는 8개이며 이끼 통로의 기본값은 32개다.

배경 명암은 낮은 입구까지 이어져 벽 안쪽 면에 수직 이음새가 생기지 않게 한다. 모든 새 효과는 지면 아래를 그리지 않는다. 근접 식생은 월드 천장에 고정하고 천장보다 위는 잘라 화면 고정·임계점 전환을 방지한다. 호출자의 클립과 블렌드를 복원한다.

발판·적4마리·충돌·카메라·덮개112·입구 봉쇄·하강 접근 조명은 그대로다. 시작 동굴·최초 착지방·이끼 통로에는 새 분위기를 적용하지 않았다.

렌더 회귀 검사는 공유 배경 색조 복원, 지면 아래 누출 방지, SDL 상태 복원, 카메라 이동 중 전경 위치 정렬을 확인한다. 최신 SDL 비교에서는 실제 골렘 발사 코드로 생성한 수정탄의 같은 비행 시점을 확인했다. [전후 비교](../../../docs/combat-readability-comparison.jpg) · [높은 발판 시점](../../../docs/combat-readability-high.png)

## Related

- [프로젝트 허브](README.md)
- [미술 방향과 자산 프롬프트](../../../docs/environment-art-direction.md)
- [녹색 거리 조사](../knowledge/greenpath-art-study.md)
- [최신 전투 시야 작업](../../worklog/codex/2026-11/20261123-combat-readability.md)
- [이전 전투방 미술 작업](../../worklog/codex/2026-11/20261123-combat-atmosphere.md)
