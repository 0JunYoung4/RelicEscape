# B1 포효 · 무게와 타이밍 보정

[할로우 나이트의 Dung Defender 도입 영상 9:30](https://www.youtube.com/watch?v=91c-CuX6fhM&t=570s)에서 넓게 디딘 발을 고정한 채 양팔이 서로 다른 박자로 움직이는 점을 참고했다. [The Hollow Knight 전투](https://www.youtube.com/watch?v=qPL5Ex7U_DQ&t=3957s)의 시작 포효에서는 제자리에서 고개를 들어 올린 실루엣이 전투 신호가 된다. 이 두 가지 원리를 바위 소라게의 관절과 무게에 맞춰 적용했다.

소라게가 몸을 낮춰 잠깐 버틴 뒤, 고개가 먼저 들리고 무거운 집게가 따라 열린다. 포효의 가장 큰 실루엣은 한 자세로 유지한다. 돌아올 때 왼쪽 집게가 먼저 풀리고 오른쪽이 뒤따라 내려오며, 무게를 받은 몸이 한 번 낮아진 뒤 전투 자세로 돌아간다. 얼굴의 닫힌 돌판은 그대로다.

- [보스 단독 미리보기 GIF](boss-roar-preview.gif)
- [B1 보스방 게임 렌더러 캡처](boss-roar-game-preview.webp)
- [투명 WebP](boss-roar-animation.webp) · [투명 PNG 시트](boss-roar-sheet.png)
- [프레임 위치와 재생 시간](boss-roar.json) · [새 복귀 자세 원본](source-recovery-atlas.png) · [생성 프롬프트](source-recovery.prompt.txt)

2초 중 0.44–0.55초는 몸을 낮춰 버티는 구간이고, 0.72–1.13초는 포효 정점이다. 집게가 내려온 뒤 1.50–1.64초에 몸이 한 번 더 낮아진다. 보스방 시안에서 같은 카메라와 효과를 두고 v3와 비교해 이 구간을 확인했다.

기존 자세 15장과 ImageGen으로 새로 그린 복귀 자세 4장을 원본 픽셀 그대로 잘라 바닥 기준점 (275, 329)에 맞춰 옮겼다. 시트는 5열 × 4행, 각 칸은 540 × 363px이며 왼쪽 위부터 읽는다. 마지막 칸은 비어 있다. 본편 연결 전의 보스 단독 시안이다. [이전 v3](../roar-v3/README.md) · [별도 효과 자산](../roar-v1/README.md)

별도 게임 테스트 장면은 낙석 직후 플레이어가 보스와 마주한 시점부터 재생한다. 게임과 같은 pico2d 렌더러에서 v4 보스, 실제 플레이어, 공기 파동과 돌먼지를 그린다. 실행 뒤 `E` 또는 `R`로 포효를 다시 보고 `Esc`로 닫을 수 있다. C 전실에서 B1로 들어가는 본편 경로는 연결 전이다.

```powershell
.\.venv\Scripts\python.exe -m tools.preview_b1_roar_game
.\.venv\Scripts\python.exe -m tools.preview_b1_roar_game --capture assets/concepts/b1-hermit-crab/roar-v4/boss-roar-game-preview.webp
```
