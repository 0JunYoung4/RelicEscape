# B1 보스방 천장 균열 암석 복원

- 기존 `ceiling-rock-v2/ceiling-boulder.png`를 두 안쪽 발판 사이 보스 바로 위에 배치했다. 방 지형과 같은 좌표로 그리며 천장 앞쪽 뿌리가 암석 윗부분을 가린다.
- 포효 테스트의 전체 방 PNG, 전투 카메라 PNG, 입구에서 중앙으로 이동하는 WebP를 SDL에서 다시 캡처했다. 전체 방 PNG는 `tools.preview_b1_roar_game --full-room <PNG>`로 재생성한다.
- 은신 해제용 암석은 도입 낙석과 별개다. 본편 연결과 타격·낙하 처리는 전투 구현에서 이어간다.
