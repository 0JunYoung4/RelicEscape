# 게임용 주인공 스프라이트

- 작성일: 2026-11-02
- 이미지 버전: v3
- 상태: 사용자 승인 기본 이미지와 대기·걷기·달리기·점프·숙이기·기어가기 초안 연결
- 제작: 내장 이미지 생성 도구로 SD 캐릭터 생성 후 게임용 크기로 내보내기

## 게임 제작 기준 원본

게임에서 사용할 캐릭터는 [player-sd-idle-right-source-v3.png](../assets/concepts/player-sd-idle-right-source-v3.png)를 기준으로 수정·변형하며 제작한다. 이 원본에서 이동·점프·공격 등 필요한 자세와 애니메이션을 확장한다.

`assets/sprites/player/`의 64×64 PNG는 이전에 크기를 줄여 내보낸 참고 자료다. 제작 출발점은 `assets/concepts/`의 source 이미지이며, 실제 게임용 해상도와 프레임 크기는 제작 과정에서 정한다. 64×64를 필수 규격으로 고정하지 않는다. LD 네 방향 이미지는 별도의 콘셉트 참고 자료로 유지한다.

## LD 콘셉트와 게임용 표현

[승인된 LD 네 방향 이미지](CHARACTER_TURNAROUND.md)는 캐릭터의 외형과 복장을 보여주는 콘셉트 자료로 유지한다. 게임 안에서는 같은 짧은 머리·하늘색 재킷·남색 바지·갈색 부츠·오른손 정글도를 SD 비율로 단순화한다.

SD 방향은 사용자가 제공한 산나비 참고 이미지의 작은 캐릭터 비율과 간결한 얼굴 표현을 따른다. 얼굴은 무표정이며 작은 눈만 남기고 코·입은 그리지 않는다. 유물은 주머니 안에 보관되어 휴대 중 보이지 않는다.

## v2 체형 조정

사용자는 첫 SD 버전이 너무 어린아이처럼 보인다고 판단했다. v2는 그보다 큰 체형의 무표정 시안과 SD v1의 중간을 목표로, 머리 비중을 줄이고 몸통·다리를 늘렸다. 약 3.5등신 내외의 간결한 게임용 비율을 목표로 하며, 16~19세 탐험가의 인상을 유지한다. 얼굴은 눈만 표현하고 코·입은 생략한다. 이 체형을 유지하고 코 돌출을 제거한 v3를 사용자가 게임용 기본 이미지로 확정했다.

## v3 코 돌출 제거

v2의 체형과 복장을 유지하고 옆얼굴의 코가 튀어나온 한 픽셀만 제거했다. 내장 이미지 생성 도구의 국소 수정 결과를 게임용 원본에 반영했으며, v2와 디코딩한 픽셀을 비교해 (36, 22)의 한 픽셀만 투명해지고 나머지는 동일함을 확인했다.

## 기존 64×64 내보내기 자료

[오른쪽을 보는 대기 PNG](../assets/sprites/player/idle-right.png)

![64×64 참고 내보내기](../assets/sprites/player/idle-right.png)

| 항목 | 값 |
| --- | --- |
| 파일 크기 | 64 × 64 픽셀 |
| 방향과 동작 | 오른쪽을 보는 기본 대기 자세 |
| 프레임 수 | 1 |
| 배경 | 투명 |
| 불투명 색상 수 | 14색, 투명색을 포함한 최대 16색 팔레트 |
| 알파 | 0 또는 255, 반투명 경계 없음 |
| 불투명 영역 | 왼쪽 23, 위쪽 10부터 오른쪽 39, 아래쪽 57까지 |
| 발 기준점 | 이미지 왼쪽 위 기준 (32, 58) |

좌표와 내보내기 정보는 [프레임 메타데이터](../assets/sprites/player/idle-right.json)에 기록한다. 충돌 영역은 실제 게임 구현 시 별도로 정한다.

## 확대 확인

아래 이미지는 게임용 64×64 파일을 최근접 방식으로 8배 확대한 512×512 미리보기다. 구분을 위해 배경색을 넣었으며 실제 게임용 파일은 투명 배경이다.

![8배 확대 미리보기](../assets/concepts/player-sd-idle-right-preview-v3.png)

## 생성 자료와 검증

- [SD 생성 원본](../assets/concepts/player-sd-idle-right-source-v3.png)
- [생성 프롬프트](../assets/concepts/player-sd-idle-right-v3.prompt.txt)
- 생성 원본에서 불투명 영역을 기준으로 크기를 맞추고, 최근접 축소로 64×64 프레임에 배치했다.
- 팔레트는 최대 16색, 알파는 완전 투명과 완전 불투명으로 정리했다.
- PNG를 다시 읽어 64×64 크기, 투명 배경, 반투명 픽셀 없음과 색상 수를 확인했다.
- 2026-11-05: `main.py`에서 원본 대기 이미지, 걷기 8프레임과 달리기 16프레임을 연결했다. 전체 프레임의 좌우 렌더링과 기본 이동 검사를 통과했고 실제 창 표시를 확인했다. 이후 사용자 승인 점프 초안 8프레임과 점프 물리·착지를 연결했다. 공격은 아직 구현하지 않았다.

## 이동 프로토타입

- 대기는 `assets/concepts/player-sd-idle-right-source-v3.png`의 캐릭터 영역을 직접 표시한다. 기존 64×64 내보내기를 제작 기준으로 사용하지 않는다.
- 걷기는 `walk-right-v1.png`와 동명의 JSON에 기록된 96×104 프레임 8개를 초당 10프레임으로 재생한다.
- 달리기는 기존 `run-right-v1.png`의 16개 자세를 동명의 JSON 영역으로 잘라 초당 16프레임으로 재생한다. 원본 PNG는 변경하지 않았다.
- 점프는 [jump-right-draft-v1.png](../assets/sprites/player/jump-right-draft-v1.png)에 승인한 4×2 배열 초안을 원본 그대로 보존했다. 참조 이미지의 점프 동작을 바탕으로 팔을 올리고 다리의 앞뒤 위치와 굽힘을 다르게 한 버전이다.
- 점프의 [JSON 메타데이터](../assets/sprites/player/jump-right-draft-v1.json)는 프레임별 영역·발 기준점·동작 단계를 기록한다. 프레임은 경과 시간·상승 및 하강 속도·착지 상태에 따라 선택하며 공중 반복 재생하지 않는다.
- 높은 낙하용 [착지 스프라이트](../assets/sprites/player/hard-landing-right-v1.png)는 발 접지, 왼손 짚기, 손을 떼고 일어나기, 자세 회복을 4프레임에 담았다. [JSON](../assets/sprites/player/hard-landing-right-v1.json)에 발 기준점과 총 370ms의 재생 시간을 기록했다. 왼손을 짚은 자세는 160ms 유지한다.
- 지상 가로 베기 [전방 5프레임 시안](../assets/sprites/player/attack-forward-right-v1.png)은 기존 베기 세 자세 사이에 연결 자세 두 장을 넣어 칼을 가장 멀리 뻗은 자세까지 이어진다. 검토용으로 보관하며, [JSON](../assets/sprites/player/attack-forward-right-v1.json)에 공통 발 기준점과 총 190ms의 재생 시간을 기록했다.
- 지상 X 공격은 [수평 베기 시트](../assets/sprites/player/attack-sweep-right-v2.png)의 5프레임을 190ms 동안 재생한다. [첫 준비 자세](../assets/sprites/player/attack-windup-right-v1.png)는 뒤쪽 사선에서 등과 후드를 보여준다. 몸 앞을 가로지른 오른팔이 앞으로 펴지며 허리 높이로 베고, 칼날은 옆구리 뒤로 지나가 옷에 가려진다. [JSON](../assets/sprites/player/attack-sweep-right-v2.json)에 발 기준점과 프레임별 재생 시간을 기록했다.
- 지상과 공중의 가로 베기는 같은 반달 검기와 타격 상자를 사용한다. 타격 상자는 검기의 전체 외곽을 감싸며, 검기가 시작되는 순간부터 공격이 끝날 때까지 Ctrl+H로 확인할 수 있다.
- 숙이기는 [빠른 4프레임 정의](../assets/sprites/player/crouch-right-fast-v1.json)로 0.15초 동안 재생한다. 기존 1·3·5·8번째 자세와 지면 기준점을 사용한다. 마지막 왼손 지지 자세를 유지하며, 해제 시 역방향으로 일어난다. 실제 기어가기 이동 주기를 담은 시트는 아니다.
- 기존 8프레임 [PNG](../assets/sprites/player/reference/crouch-8frame-v1/crouch-right-draft-v1.png)와 [JSON](../assets/sprites/player/reference/crouch-8frame-v1/crouch-right-draft-v1.json)은 보관 폴더로 분리했으며 바이트를 변경하지 않았다. 빠른 버전은 보관된 원본 PNG에서 선택한 4개 영역만 읽는다.
- 기어가기는 다리 교차 자세를 수정한 [crawl-right-draft-v2.png](../assets/sprites/player/crawl-right-draft-v2.png)로 교체했다. [JSON](../assets/sprites/player/crawl-right-draft-v2.json)의 8프레임과 지면 기준점으로 초당 8프레임 반복 재생한다. 표시 배율은 140/466으로 기존 화면 높이에 맞췄다. 완전히 숙여 실제로 움직일 때만 사용하고, 멈추면 숙인 대기 자세로 돌아간다. 기존 v1은 비교용으로 유지한다.
- 대기·걷기·달리기의 크기는 각각 표시 배율로 조정하고 발 기준점을 같은 바닥에 맞춘다. 걷기는 1.5배, 달리기는 0.5배이며 최종 제작 규격을 확정한 것은 아니다.
- 횡스크롤 카메라 배율 0.5를 모든 자세에 추가 적용한다. 기본 캐릭터는 화면에서 약 70픽셀 높이이며, 에셋 자체를 다시 축소해 저장하지 않는다.
- 왼쪽은 오른쪽 이미지 반전으로 임시 표시한다. 정글도 손과 복장 비대칭을 정확하게 보존하는 전용 왼쪽 이미지는 추후 제작 대상이다.

## 이전 버전 비교

- [SD v1 게임용 PNG](../assets/sprites/player/idle-right-v1.png)
- [SD v1 확대 미리보기](../assets/concepts/player-sd-idle-right-preview-v1.png)
- v1은 큰 머리와 짧은 몸통·다리의 체형 비교 자료로 보관한다.

- [코 수정 전 v2 PNG](../assets/sprites/player/idle-right-v2.png)
- [코 수정 전 v2 미리보기](../assets/concepts/player-sd-idle-right-preview-v2.png)

## 기본 이미지 확정

2026-11-02 사용자 승인으로 v3를 기본 이미지로 확정했다. 기존 내보내기 경로 idle-right.png는 64×64 v3와 바이트 단위로 동일하며, 승인 메타데이터에 버전과 SHA-256을 기록했다. 실제 캐릭터 제작의 기준 원본은 assets/concepts/player-sd-idle-right-source-v3.png다. [캐릭터 소개 이미지](../assets/concepts/character-introduction-v1.png)와 [발표 자료](<../발표&기획서/1차 발표 및 기획/README.md>)를 함께 보관한다.
