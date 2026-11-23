"""Draw the B route blockout in world units."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / "docs/map1-lower-route-b-blockout-v1.png"
im = Image.new("RGB", (2200, 1000), "#f3f6fa")
draw = ImageDraw.Draw(im)
INK, MUTED, TERRAIN = "#183147", "#50667a", "#465665"
RAIL, SAFE, ENEMY, RELIC = "#395cb2", "#237553", "#a13d53", "#067c87"
SCALE, LEFT, FLOOR = .49, 70, 530


def label(x, y, value, size=26, *, color=INK, bold=False, anchor="la"):
    font = ImageFont.truetype(
        "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf", size)
    draw.text((x, y), value, font=font, fill=color, anchor=anchor)


def world(x, y):
    return round(LEFT + x * SCALE), round(FLOOR - y * SCALE)


def box(left, bottom, right, top, fill=TERRAIN):
    draw.rectangle((*world(left, top), *world(right, bottom)), fill=fill)


def tag(x, y, width, name, color):
    draw.rectangle((x, y, x + width, y + 39), fill=color)
    label(x + width / 2, y + 20, name, 22, color="white", bold=True, anchor="mm")


label(65, 25, "B파트  |  수평 레일과 방패병 회랑", 48, bold=True)
label(69, 91, "A 왼쪽 출구 → B 오른쪽 입구  ·  그림에서는 오른쪽에서 왼쪽으로 진행  ·  단위는 월드 기준", 26, color=MUTED)
draw.rectangle((70, 161, 2128, 860), fill="#e3ebf3")
for x, width, headline in ((70, 235, "04  C 연결"), (311, 726, "03  방패병 회랑"),
                           (1043, 641, "02  수평 레일"), (1690, 438, "01  A에서 진입")):
    draw.rectangle((x, 161, x + width, 217), fill="#d2deeb")
    label(x + 16, 171, headline, 29, bold=True)

# Left overhang, right bank, lower safety floor and steps use the same vertical scale.
box(0, -96, 2250, 0)
box(0, -620, 1660, -96)
box(1660, -620, 3260, -595)
box(3260, -620, 4200, 0)
for left, right, top in ((2660, 2820, -475), (2820, 2940, -355),
                         (2940, 3060, -235), (3060, 3260, -115)):
    box(left, -595, right, top)
    box(left, top - 12, right, top, "#83c9a6")
box(1660, -599, 2660, -595, "#83c9a6")
box(0, -8, 390, 0, "#83c9a6")
for left, right, top, thickness in ((1640, 1830, 110, 110), (1430, 1580, 225, 38),
                                    (1190, 1350, 315, 38), (920, 1090, 200, 38)):
    box(left, top - thickness, right, top)

# Rail and contact points, above the same-height banks.
box(2070, 94, 3430, 106, RAIL)
sx, sy = world(3430, 100)
tag(sx - 45, sy - 20, 90, "파츠", RAIL)
sx, sy = world(2070, 100)
tag(sx - 28, sy - 20, 88, "정차", RAIL)
sx, sy = world(3590, 30)
tag(sx - 8, sy - 42, 94, "회수", SAFE)
sx, sy = world(1360, 0)
tag(sx - 36, sy - 40, 76, "유물", RELIC)
sx, sy = world(1150, 0)
tag(sx - 46, sy - 55, 92, "방패병", ENEMY)
draw.rectangle((sx + 42, sy - 51, sx + 53, sy - 20), fill="#733044")
sx, sy = world(650, 0)
tag(sx - 43, sy - 40, 86, "공벌레", ENEMY)

label(94, 285, "← C파트", 28, bold=True)
label(94, 320, "짧은 안전 통로", 23, color=SAFE)
label(460, 305, "상단 발판으로 넘기", 28, bold=True)
label(474, 347, "유물로 되돌아와 등 뒤 노리기", 23, color=RELIC)
label(1045, 265, "← 파츠 이동  |  E 장착 → 왼쪽을 보고 X", 27, color=RAIL, bold=True)
label(1045, 310, "빛나는 반대편 발판에 닿으면 E로 이동", 24, color=RAIL)
label(1720, 343, "A에서 걸어 들어옴", 24, bold=True)
label(1251, 571, "틈 1,010", 30, color=INK, bold=True)
label(1251, 617, "일찍 내려오면", 25, color=SAFE, bold=True)
label(1251, 654, "오른쪽 계단으로 →", 25, color=SAFE)
label(91, 651, "방패병 오른쪽에 유물 설치", 26, color="#a7e1e4", bold=True)
label(91, 695, "발판으로 왼쪽에 넘어가 공격을 유도한 뒤 E로 복귀", 23, color="#edf4fa")
label(91, 736, "발판만 이용해 전투를 지나가는 길도 열려 있음", 23, color="#edf4fa")
label(1700, 640, "회수 손잡이 E", 26, color="#aee7c7", bold=True)
label(1700, 679, "건너편에 남은 파츠를", 22, color="#edf4fa")
label(1700, 713, "출발점으로 되돌림", 22, color="#edf4fa")

for x, name, fill in ((73, "지형", TERRAIN), (395, "레일·파츠", RAIL), (770, "안전 회수로", SAFE),
                      (1150, "몬스터", ENEMY), (1490, "유물 설치 예시", RELIC)):
    draw.rectangle((x, 902, x + 27, 929), fill=fill)
    label(x + 41, 895, name, 24)
label(74, 945, "레일에서 떨어져도 재시도 가능  ·  B는 C 진입부에서 끝남  ·  방패병 동작과 최종 간격은 구현 검증 대상", 22, color=MUTED)
im.save(OUT)
