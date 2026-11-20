---
memoc: true
type: worklog
actor: codex
date: 2026-11-20
---
# 어두운 초기 동굴 맵 구현

## Summary
- `opening_cave.py`와 `run_opening_cave`로 타이틀 이후 초기 동굴을 연결했다. 배경 v2·바닥 v1·기존 타이틀 문양문을 재사용한다.
- 폭 6000, 바닥 y420, 낮은 천장, 오른쪽 끝벽과 실제 충돌. 배경/지형은 어둡게, 캐릭터와 카메라 크기는 기존 유지.
- 기존 이동·점프·공격·숙이기·R·Esc·F11·Ctrl+H를 지원한다. 추락·문양 조사·유물·히든 엔딩은 이번 범위에서 제외했다.
- `--test-room`으로 이전 시험 맵을 유지하고 기존 통합 검사 호출을 해당 모드로 명시했다. README와 프로젝트 메모리를 갱신했다.

## Verification
- unittest discover: 78개 통과.
- SDL 소프트웨어 렌더 입구·중앙·문양문 화면을 저장해 시각 확인, SDL 오류 없음.
- 사용자 작업의 발표 PPT 임시 파일 삭제는 수정하지 않았다.
- memoc 로컬 런타임과 npm 캐시가 없어 wrapper 검색은 ENOTCACHED로 실패했다. 메모리는 직접 갱신하고 상대 링크를 별도로 검사한다.
