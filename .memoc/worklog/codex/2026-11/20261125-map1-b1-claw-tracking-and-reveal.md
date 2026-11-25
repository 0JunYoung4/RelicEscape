# B1 집게 추적과 은신 약점 노출 시안

- 단일 동굴 바닥에서 집게를 올려 플레이어가 집게 아래를 통과하는 장면을 그렸다. 렌더 기준 걷는 캐릭터 높이 71px, 집게 아래 96px, 몸통 아래 31px다.
- 화면 왼쪽 집게가 제자리에서 수직으로 떠오르고 플레이어와 함께 가로로 움직인다. 몸체는 뒤에서 좌우로 걷는다. 추적을 끊은 자리에 황색 예고를 0.8초 표시한 뒤 그대로 낙하한다.
- `assets/concepts/b1-hermit-crab/`에 `claw-tracking-slam-preview-v1.gif`, `shell-depth-reveal-preview-v1.gif`, `claw-tracking-slam-keyframes-v1.png`를 저장했다. 모션과 배치 확인을 위한 시안이다.
