# 입구 봉쇄 바위만큼 두꺼운 덮개

- 사용자 요청: 덮개를 전투방 입구를 막는 바위 두께 정도로 확대.
- 입구 바위의 가로 두께112를 기준으로 선택했다. 덮개32→112, 고정 받침 하단96→176. COMBAT_COVER_THICKNESS를 입구 충돌 폭에서 직접 계산.
- 얇은 텍스처 확대 대신 내장 imagegen으로 묵직한 새 덮개 cover-v4와 깊은 홈 rim-v3 생성. PNG/원본/JSON/정확한 프롬프트 저장.
- 연결부 상/하단의 원본 안쪽 경계를 각각 입구248/통로180에 환산, surface_y9/step_y354에서 상단112와 아래64를 분리해 배치. 윗면과 받침·충돌을 맞추고 이전32용 rim-v2 메타데이터는96 높이 유지.
- 우측 슬라이드0.7초, 고정 턱 지지, 부분 개방 낙하, 접근 조명, 지하 착지960 유지.
- 관련28개 테스트(20.419초), 컴파일·diff 통과. archive/unused-assets/2026-11-23/docs/combat-shaft-v5-approach.gif/닫힘/부분/개방/착지 및 최신 전체 방 화면 SDL 검토.

생성 파일(내장 imagegen):

- [덮개 PNG](../../../../assets/terrain/moss-combat-floor-cover-v4.png) · [프롬프트](../../../../assets/terrain/moss-combat-floor-cover-v4.prompt.txt)
- [깊은 연결부 PNG](../../../../assets/terrain/moss-combat-shaft-rim-v3.png) · [프롬프트](../../../../assets/terrain/moss-combat-shaft-rim-v3.prompt.txt)
