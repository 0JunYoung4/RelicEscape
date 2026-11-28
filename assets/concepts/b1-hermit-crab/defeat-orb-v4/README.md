# B1 응축된 푸른 에너지 v4

청백색 중심 주위에 푸른빛의 층이 응축되고 바깥의 옅은 빛은 투명하게 사라진다. 확인한 시안과 같은 320 × 320 원본 프레임을 LANCZOS로 축소했다. [보스방 부유 미리보기](energy-orb-hover.webp)

[투명 스프라이트 시트 PNG](energy-orb-sheet.png)는 512 × 512 RGBA다. 128 × 128 칸 16개를 4 × 4 배열로 배치했다. 왼쪽 위부터 행을 따라 읽으며 기준점은 모든 칸에서 (64, 64)다. 프레임당 75ms로 총 1.20초 동안 반복한다.

`.\.venv\Scripts\python.exe -m tools.render_b1_defeat_orb_v4`로 다시 렌더링한다.
