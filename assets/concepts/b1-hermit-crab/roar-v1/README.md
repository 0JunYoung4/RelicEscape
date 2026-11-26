# B1 포효

천장 바위가 등딱지에 떨어지고 바위 소라게가 눈을 뜬 뒤의 전투 시작 연출이다. 몸과 집게를 낮춰 힘을 모은 뒤, 기존 얼굴을 유지한 채 고개를 위로 젖히고 두 집게를 들어 벌린다. 공기 파동과 낮게 퍼지는 돌먼지·자갈은 독립 레이어다. [보스방 합성 미리보기](boss-roar-preview.gif)

| 레이어 | 투명 애니메이션 | 투명 PNG 시트 | 프레임 크기 | 바닥 기준점 |
| --- | --- | --- | --- | --- |
| 보스 | [WebP](boss-roar-animation.webp) | [PNG](boss-roar-sheet.png) | 600 × 420 | (300, 400) |
| 공기 파동 | [WebP](roar-wave-animation.webp) | [PNG](roar-wave-sheet.png) | 900 × 440 | (450, 420) |
| 먼지·자갈 | [WebP](roar-debris-animation.webp) | [PNG](roar-debris-sheet.png) | 900 × 440 | (450, 420) |

세 레이어의 바닥 기준점을 보스 중심의 같은 월드 좌표에 맞춘다. 시트는 왼쪽에서 오른쪽, 위에서 아래로 읽는 8열 6행이며, 24fps로 48프레임(2초)을 재생한다. 프레임 번호는 0부터 시작한다. 파동은 16프레임, 먼지·자갈은 17프레임에 시작하고 보스 자세는 18프레임에 포효 정점에 닿는다. 시트의 앞뒤 투명 프레임도 타이밍에 포함한다. [효과 기준점과 타이밍](roar-effects.json)

원경과 지형을 그린 뒤 공기 파동 → 보스 → 바닥 먼지 → 플레이어 → 근접 전경 순으로 그린다. 보스는 기존 `assembled-upright-v6.png`를 바탕으로 움직이며 자갈은 기존 `ceiling-rock-v2/debris-v1/`의 작은 파편을 사용한다. 합성은 바위 충돌 직후부터 재생하며 B1 본편 전투와는 아직 연결되지 않았다.

재생성은 저장소 루트에서 다음 순서로 실행한다.

```powershell
.\.venv\Scripts\python.exe -m tools.render_b1_roar_pose
.\.venv\Scripts\python.exe -m tools.render_b1_roar_effects
.\.venv\Scripts\python.exe -m tools.render_b1_roar_preview
```
