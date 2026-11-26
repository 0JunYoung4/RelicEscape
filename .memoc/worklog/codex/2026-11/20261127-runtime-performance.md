# 입력 중복 대기와 렌더 메시 비용 개선

- 기존 pico 입력 폴링이 넣던 SDL_Delay/FPS 제목 갱신을 앱 이벤트 변환으로 대체했다. 창 제목은 초기화1회, 기존 main60fps 제한 유지. 미사용 이미지5개 로딩 제거.
- `render_mesh.py`로 float32/RGBA 정점 바이트를 직접 기록하고 고정 인덱스·원형 좌표를 제한 캐시로 재사용했다. 동적 정점은 호출별 독립 버퍼다. A·B·C 공통 메시와 전투방 광원·중경에 적용했다.
- 화면/클립 밖 빛을 생략한다. software 얇은 광원 클립의 기존 widthinvalid는 필요한 광원만 흰 텍셀로 그려 해결했다. native 출력10장은 기준 커밋dea80ae와 픽셀일치, software는 반사광 수정2장에서 채널최대2/255 차이.
- [측정 보고](../../../../docs/runtime-performance.md) · [전체 수치](../../../../docs/runtime-performance-results.json). `tools.profile_gameplay`로 동일 static/moving 장면60프레임×두backend=1200화면 오류0. Direct3D11 전투방중앙10.87→6.28ms, A5.79→2.65ms. 입력240회중앙1.9991→0.0011ms.
- 최종전체222tests/221.569초/exit0 및diff검사통과. 장시간 전체화면 체감과 기기별 성능은 미측정이다. software C는75~81ms 수준의 이미지 합성 병목이 남아 이 경로의 전반적 향상을 주장하지 않는다.
