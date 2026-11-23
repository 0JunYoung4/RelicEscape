---
memoc: true
type: knowledge
scope: environment-art
updated: 2026-11-23
status: active
tags:
  - memoc/wiki
  - environment-art
  - visual-research
---
# 두 게임 맵 제작용 참고 데이터

기존 녹색 거리 중심45장에 신규199장을 더해244장을 분석했다. 할로우 나이트128장·실크송116장, 게임별36개 지역이다. 모든 신규 이미지는 실제 PNG이며, 기존45장은 원래 폴더의 파일을 참조한다. 고유 파일·RGB 픽셀 해시244개를 확인했다. 이미지 수는 독립된 방의 수가 아니다.

[제작 가이드](../../../docs/reference-production-guide.md)와 [검색 갤러리](../../../docs/references/hollow-knight-silksong/index.html)를 먼저 본다. 이미지마다 공간 구성·재질·전경/중경/원경·그림자·조명과 P01~P20 패턴, B01~B20 자산 명세를 연결했다. 대표12장49개 정규화 관심 영역은 실제 엔진 레이어·충돌·세그멘테이션이 아니다. 원작의 시간·시차·적 수치도 정지 화면에서 확정하지 않는다.

[구역 대응 데이터](../../../docs/references/hollow-knight-silksong/project-targets.json)는 최신 두 맵 구조를 따른다. ‘중앙 통로’는 맵2 작은 중앙 홀, ‘문양의 성소’는 맵2 최종 보스방의 문양·제단이다. 현재 전투방·유물 시안·후속 장치 구역의 구현 상태를 구별한다. 이번 조사는 게임 동작이나 맵 범위를 변경하지 않았다.

[JSON](../../../docs/references/hollow-knight-silksong/analysis.json)·[CSV](../../../docs/references/hollow-knight-silksong/catalog.csv)·query_references.py로 재사용한다. 신규 수집은 collect_references.py가 이전 배치를 보존하고, 수동 관찰 없는 항목은 build_database.py가 거부한다. 로컬 링크518·내보내기244행·CLI·JS문법·Python컴파일을 확인했다. 브라우저의 실제 클릭 검수는 로컬 접근 정책으로 미완료다.

## Related

- [지식 허브](README.md)
- [녹색 거리 조사](greenpath-art-study.md)
- [현재 미술 방향](../../../docs/environment-art-direction.md)
- [이번 작업 로그](../../worklog/codex/2026-11/20261123-hollow-knight-silksong-reference-database.md)
