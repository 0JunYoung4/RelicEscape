# 할로우 나이트·실크송 참고 자료의 프로젝트 데이터화

2026년11월23일. 두 게임의 여러 맵 이미지를100장 이상 누적하고 우리 프로젝트에서 사용할 데이터로 정리하라는 요청을 처리했다.

## 결과

- 기존45장+신규199장=244장. HK128·SS116, 게임별36개 지역. 신규 PNG 약72.86MiB. 완전 중복0, dHash 유사 구도 후보1개를 별도 표시.
- `docs/references/hollow-knight-silksong/`: 출처 원장·수집 로그, 수동 관찰199행, 분석 JSON/JSONL/CSV,20패턴·20자산 명세, 구역 대응·manifest·통계, 오프라인 검색/2장 비교 갤러리, 연락표21장, 대표12주석49영역과 프로젝트 참고 보드.
- `docs/reference-production-guide.md`: 실제 구역별 우선 참고·현재 구현/후보 구별·제작 순서·데이터 필드·계속 누적하는 절차. README/미술 방향 문서 연결.
- 최신 승인 두 맵 지도와 연결: 중앙 통로→맵2 작은 중앙 홀, 성소→맵2 최종 보스방. 후속 미술 제안이 구현이나 새 기능의 승인을 뜻하지 않음.
- `legacy-curation.txt`에서 기존45장의 재질·공간·주요 구역을 직접 보정했다. 비교 문장 속 ‘이끼’를 잘못 태그한 수정 봉우리 HK-EX06을 수정했고, 식생 통로의 위험 장면이 모두 장치 구역으로 추천되지 않도록 했다.
- 이번 조사에서 게임 코드·자산·PPT는 변경하지 않음. 이미 구현한 전투방 미술과 제단 조명v2 콘셉트 보존.

## 검증과 한계

244개 파일 디코드·크기·SHA256·RGB픽셀 해시 일치/고유성, JSON/JSONL/CSV244행, HTML244카드, 로컬 링크518개, 모든 패턴·명세·구역·주석 ID 참조와 ROI범위 통과. 연락표 전체와 선별 원본, 대표12개 주석을 시각 검토했다. 주석은 참고할 위치이며 엔진 레이어/충돌 정답 데이터가 아니다. SS-DD-05의 매달린 물체는 화로 외형으로 교정했고 밟을 수 있다고 주장하지 않는다.

CLI 구역+패턴+게임 검색, 조명/재질 검색을 확인. Node vm.Script로 갤러리 JS문법과 내장244레코드 JSON파싱 통과. 자료 스크립트6개 py_compile·git diff --check 통과. 실제 브라우저 필터/비교창 클릭과 브라우저 레이아웃은 로컬 접근 정책으로 미검증이며 우회하지 않았다.

memoc 로컬 런타임/npx 부재로 wrapper의 search/work/ingest/lint-wiki 실행이 불가해 최소 메모리·에이전트 작업로그를 직접 작성했다. 신규 위키에는 허브에서 인바운드와 Related를 연결하고 로컬 링크를 직접 검사했다. 세션 요약은800B 미만으로 교체한다.

## 계속 누적

수집기는 기존 sources.json/다운로드 로그를 보존하고 game/region/max-per-region 필터를 제공한다. 새 이미지를 시각 확인하고 observations-*.txt의8필드를 채운 뒤 build_database.py→build_analysis_plates.py→build_database.py와 validate_database.py를 실행한다. 관찰 없는 신규 레코드는 빌드를 실패시킨다. 예약 자동 수집은 설정하지 않았다.

## Related

- [제작 가이드](../../../../docs/reference-production-guide.md)
- [지식 기록](../../../wiki/knowledge/hollow-knight-silksong-reference-database.md)
- [이전45장 조사](20261123-greenpath-reference-study.md)
