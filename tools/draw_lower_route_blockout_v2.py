"""Render the proposed lower route as three continuous side-view strips."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / 'docs/map1-lower-route-blockout-v2.png'
image = Image.new('RGB', (2320, 1610), '#f5f7fa')
draw = ImageDraw.Draw(image)
INK, MUTED, GROUND = '#183047', '#4b6073', '#4c5b6a'
RELIC, RAIL, SAFE = '#067b85', '#3759ae', '#9de0be'
BUG, SHIELD, GOLEM, GATE = '#a05c28', '#a33b53', '#684c9b', '#237455'


def label(x, y, text, size=27, color=INK, bold=False, anchor='la'):
    font = ImageFont.truetype('C:/Windows/Fonts/malgunbd.ttf' if bold else 'C:/Windows/Fonts/malgun.ttf', size)
    draw.text((x, y), text, fill=color, font=font, anchor=anchor)


def box(x, y, w, h, color):
    draw.rectangle((x, y, x + w - 1, y + h - 1), fill=color)


def tile(x, y, w, h, text, color, size=23, ink='white'):
    box(x, y, w, h, color)
    label(x + w / 2, y + h / 2, text, size, ink, True, 'mm')


def terrain(*rectangles):
    for rect in rectangles:
        box(*rect, GROUND)


def steps(*rectangles):
    for rect in rectangles:
        box(*rect, SAFE)


def strip(y, left_title, right_title, start, end):
    box(46, y, 2228, 411, '#e7edf4')
    box(46, y, 2228, 50, '#d5e0ec')
    label(98, y + 7, left_title, 30, bold=True)
    label(2220, y + 7, right_title, 30, bold=True, anchor='ra')
    tile(46, y + 69, 49, 42, end, GROUND)
    tile(2225, y + 69, 49, 42, start, GROUND)


label(46, 23, '전투방 아래에서 첫 보스 B1까지', 52, bold=True)
label(48, 97, '각 줄은 오른쪽에서 왼쪽으로 진행  ·  같은 연결 문자로 다음 줄에 이어짐  ·  축척 없는 배치 시안', 28, MUTED)

# 01–02. The green staircase comes back to the same ledge as the relic anchor.
strip(152, '02  아래로 내려가 문 열기', '01  하강 착지 · 단차', '시작', 'A')
terrain((46, 208, 2020, 20), (2210, 208, 64, 143),
        (46, 394, 1074, 25), (1440, 394, 834, 25),
        (1635, 337, 100, 57), (1772, 364, 95, 30),
        (815, 419, 105, 110), (815, 529, 655, 22), (1440, 419, 30, 132))
tile(730, 228, 43, 166, '문', GATE)
tile(943, 484, 130, 45, '스위치', GATE)
tile(1454, 344, 86, 50, '유물', RELIC)
tile(1890, 350, 100, 44, '공벌레', BUG)
steps((1200, 505, 86, 14), (1282, 471, 84, 14), (1365, 435, 75, 14))
label(2080, 232, '↓ 하강', 25, bold=True)
label(2050, 346, '안전 착지', 26, bold=True)
label(1610, 283, '단차 뛰기', 26)
label(1142, 285, '① 유물 설치', 25, RELIC, True)
label(1142, 320, '② 아래로 낙하', 25)
label(946, 434, '③ 문 개방', 24, GATE, True)
label(1488, 452, '유물 없이 떨어짐', 24, GATE, True)
label(1488, 487, '계단을 올라 원래 발판으로', 25, GATE)
label(98, 280, '← 레일 회랑으로', 27, bold=True)
label(184, 458, '④ E로 상단 복귀', 27, RELIC, True)
label(184, 495, '틈을 뛰어 넘어 열린 문 통과', 24)

# 03–04. The first rail is the compulsory crossing. The net returns to its dock.
strip(575, '04  방패병 회랑', '03  레일 1 · 넓은 틈 건너기', 'A', 'B')
terrain((46, 800, 1314, 29), (1990, 800, 284, 29), (1175, 764, 84, 16),
        (640, 735, 150, 16), (808, 777, 95, 14), (1318, 829, 42, 101),
        (1360, 930, 663, 18), (1990, 829, 33, 101))
box(1300, 729, 728, 8, RAIL)
tile(1278, 711, 70, 43, '도착', RAIL, 20)
tile(1986, 711, 83, 43, '파츠', RAIL)
tile(1079, 752, 81, 48, '유물', RELIC)
tile(916, 734, 110, 66, '방패병', SHIELD)
box(1013, 734, 13, 66, '#742738')
tile(361, 757, 100, 43, '공벌레', BUG)
steps((1360, 916, 630, 14), (1780, 888, 92, 14), (1885, 850, 105, 14))
label(150, 687, '← 다음 레일로', 26, bold=True)
label(795, 653, '발판을 밟아 방패병 뒤로', 24)
label(1450, 653, '파츠가 건너편에 도착하면 E', 27, RAIL, True)
label(1905, 762, 'E 장착 · ← + X', 24, RAIL, True)
label(355, 865, '발판을 타고 넘거나, 방향을 돌린 뒤 E로 등 뒤 공격', 24)
label(1385, 833, '벽점프 불가 벽', 21, MUTED)
label(1393, 877, '낙하 시 출발대로 →', 24, GATE, True)
label(1393, 950, '회수 손잡이로 파츠와 유물을 초기화하고 재시도', 23, GATE)

# 05–06. The rising track offers a mid-route wall jump and a safe end landing.
strip(998, '06  수정 골렘 · 안전 전실 · B1', '05  레일 2 · 중간 하차 또는 끝 착지', 'B', '끝')
terrain((46, 1285, 1315, 25), (1280, 1220, 280, 22), (1110, 1252, 135, 22),
        (630, 1204, 170, 18), (1550, 1268, 165, 20), (1495, 1220, 55, 165),
        (1550, 1372, 724, 20), (2055, 1258, 219, 26), (2242, 1284, 32, 89))
steps((1550, 1358, 692, 14), (1825, 1332, 90, 14), (1930, 1306, 94, 14), (2040, 1280, 80, 12))
box(1390, 1155, 219, 8, RAIL)
box(1601, 1155, 8, 48, RAIL)
box(1601, 1195, 220, 8, RAIL)
box(1813, 1195, 8, 24, RAIL)
box(1813, 1211, 310, 8, RAIL)
tile(2105, 1195, 78, 41, '파츠', RAIL)
tile(1350, 1137, 78, 42, '끝', RAIL)
tile(1617, 1178, 78, 40, '중간', RAIL, 21)
tile(655, 1154, 122, 50, '수정 골렘', GOLEM)
tile(156, 1197, 174, 88, 'B1', GOLEM, 30)
tile(369, 1241, 36, 44, '문', GATE, 20)
tile(422, 1243, 154, 42, '안전 전실', SAFE, 22, INK)
label(1144, 1080, '끝에서 E → 상단에 여유 있게 착지', 24, RAIL, True)
label(1645, 1099, '중간에 E → 벽 슬라이드 · 벽점프', 24, RAIL, True)
label(795, 1149, '높은 길에서 접근', 24)
label(811, 1231, '아래로 내려 합류', 24)
label(105, 1337, '평평한 보스방에서 유물로 위치 바꾸기', 23)
label(1555, 1314, '아래 회수로 →', 23, GATE, True)

for x, name, color in [(48, '지형', GROUND), (345, '유물 설치', RELIC), (690, '레일 · 파츠', RAIL),
                       (1080, '구제 발판 · 안전 지점', SAFE), (1625, '몬스터', SHIELD), (1940, '문 · 스위치', GATE)]:
    box(x, 1446, 26, 26, color)
    label(x + 40, 1439, name, 27)
label(48, 1510, '실수해도 같은 구간에서 다시 시도. 레일 1은 필수, 레일 2는 같은 목적지로 이어지는 두 가지 하차 방식.', 28, bold=True)
label(48, 1550, '설계 시안  ·  파츠 회수 손잡이, 벽점프 불가 벽, 방패병 후면 공략은 신규 동작', 24, MUTED)
image.save(OUT)
