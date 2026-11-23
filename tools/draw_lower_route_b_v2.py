"""Draw the B-section spike crossing as a level-design diagram."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / "docs/map1-lower-route-b-blockout-v2.png"
image = Image.new("RGB", (2290, 1010), "#f4f7fb")
d = ImageDraw.Draw(image)
INK, MUTED, TERRAIN = "#173149", "#4b6176", "#435568"
RAIL, WALL, ENEMY, SAFE, SPIKE = "#3559b3", "#945611", "#9e3650", "#278060", "#a02c44"


def label(x, y, value, size=26, *, color=INK, bold=False, anchor="la"):
    path = "C:/Windows/Fonts/malgunbd.ttf" if bold else "C:/Windows/Fonts/malgun.ttf"
    d.text((x, y), value, font=ImageFont.truetype(path, size), fill=color, anchor=anchor)


def xy(x, y):
    return round(70 + x * .43), round(650 - y * .4)


def block(left, bottom, right, top, color=TERRAIN):
    d.rectangle((*xy(left, top), *xy(right, bottom)), fill=color)


def tag(x, y, value, color, width=82):
    d.rectangle((x - width / 2, y - 18, x + width / 2, y + 18), fill=color)
    label(x, y, value, 21, color="white", bold=True, anchor="mm")


def rail(left, right, height):
    block(left, height - 7, right, height + 7, RAIL)
    lx, ly = xy(left, height)
    rx, ry = xy(right, height)
    tag(lx, ly, "정차", RAIL)
    tag(rx, ry, "파츠", RAIL)
    mid = (lx + rx) / 2
    d.polygon(((mid - 15, ly), (mid + 3, ly - 13), (mid + 3, ly + 13)), fill=RAIL)


label(67, 25, "B파트 v2  |  가시 협곡과 세 개의 공중 전투 발판", 46, bold=True)
label(69, 90, "A에서 들어와 가시 위를 건너고, 벽을 타고 올라 C로  ·  콘셉트 도면", 28, color=MUTED)
d.rectangle((70, 156, 2220, 800), fill="#e6edf5")
for x, end, caption in ((70, 335, "C 연결"), (340, 690, "03  수정 골렘"),
                        (695, 962, "레일 2  ←"), (967, 1289, "02  방패병"),
                        (1294, 1514, "벽점프  ↑"), (1519, 1700, "01  공벌레"),
                        (1705, 1964, "레일 1  ←"), (1969, 2220, "A에서 진입")):
    d.rectangle((x, 156, end, 210), fill="#d2deeb")
    label(x + 12, 165, caption, 25, bold=True)

# Connecting ledges and islands.
block(0, 500, 680, 590)
block(680, 495, 1340, 590)
block(2160, 495, 2900, 590)
block(2800, 100, 2900, 495)
block(3060, 85, 3650, 180)
block(3150, 355, 3290, 1100)
block(4460, 90, 5000, 180)
for left, right, height in ((0, 380, 590), (1100, 1340, 590), (2670, 2900, 590),
                            (2160, 2350, 590), (3410, 3650, 180), (4460, 5000, 180)):
    block(left, height - 8, right, height, SAFE)

rail(1160, 2320, 690)
rail(3450, 4620, 280)
for x, y, name, width in ((885, 740, "수정 골렘", 112), (2500, 780, "방패병", 86),
                          (3250, 260, "공벌레", 86)):
    tag(*xy(x, y), name, ENEMY, width)

# Illustrate direction changes without implying platforms in the shaft.
path = [xy(3090, 180), xy(2920, 382), xy(3130, 550), xy(2830, 690)]
d.line(path, fill=WALL, width=6, joint="curve")
ex, ey = path[-1]
d.polygon(((ex, ey), (ex + 19, ey + 4), (ex + 10, ey + 18)), fill=WALL)
for i, (x, y) in enumerate(path[1:3], start=1):
    tag(x + (29 if i == 1 else -24), y - 9, str(i), WALL, 29)

label(101, 294, "← C파트", 27, bold=True)
label(102, 334, "짧은 안전 통로", 23, color=SAFE)
label(673, 297, "폭 820", 24, color=RAIL)
label(759, 296, "정차 뒤 E", 25, color=RAIL, bold=True)
label(980, 474, "착지 여유", 23, color=SAFE, bold=True)
label(981, 510, "착지 후 안쪽으로 진입", 21, color=MUTED)
label(1520, 362, "410 높이차", 25, color=WALL, bold=True)
label(1520, 401, "왼쪽 벽 → 오른쪽 벽 → 위 발판", 23, color=WALL)
label(1695, 480, "폭 810", 24, color=RAIL)
label(1817, 480, "E 장착 · 왼쪽 X", 24, color=RAIL, bold=True)
label(100, 664, "가시에 떨어지면 체력 25 감소 → 마지막 안전 발판으로 복귀", 29, color=SPIKE, bold=True)

d.rectangle((70, 751, 2220, 800), fill=SPIKE)
for x in range(70, 2220, 25):
    d.polygon(((x, 752), (x + 12, 731), (x + 25, 752)), fill=SPIKE)
label(1145, 775, "하단 전 구간 가시", 28, color="white", bold=True, anchor="mm")

for x, color, name in ((72, TERRAIN, "지형"), (362, RAIL, "레일"), (641, WALL, "벽점프"),
                       (926, SAFE, "안전 착지·출발"), (1330, ENEMY, "몬스터"), (1678, SPIKE, "가시")):
    d.rectangle((x, 847, x + 27, 873), fill=color)
    label(x + 42, 840, name, 24)
label(73, 907, "레일 1 → 공벌레 발판 → 벽점프 → 방패병 발판 → 레일 2 → 수정 골렘 발판 → C 진입", 29, bold=True)
label(74, 956, "몬스터는 착지한 뒤 가까이 접근하면 활성화  ·  방패병과 골렘은 서로 다른 발판에 배치", 23, color=MUTED)
image.save(OUT)
