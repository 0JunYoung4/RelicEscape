"""Render the proposed lower route as three continuous side-view strips."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / 'docs/map1-lower-route-blockout-v3.png'
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


label(46, 23, '전투방 아래에서 B1 연결 입구까지', 52, bold=True)
label(48, 97, '각 줄은 오른쪽에서 왼쪽으로 진행  ·  같은 연결 문자로 다음 줄에 이어짐  ·  축척 없는 배치 시안', 28, MUTED)

# 01–02. The lift terminates above the continuous exit floor, across the drop.
strip(152, '02  버튼실 · 레일 1 수직 상승', '01  하강 착지 · 단차', '시작', 'A')
terrain((46, 208, 2020, 20), (2230, 208, 44, 155),
        (46, 339, 808, 27), (1412, 382, 862, 27),
        (1635, 328, 100, 54), (1772, 354, 95, 28),
        (823, 366, 31, 181), (823, 526, 784, 21), (1576, 409, 31, 117))
steps((854, 520, 722, 6), (575, 333, 279, 6))
box(710, 301, 329, 8, RAIL)
box(1031, 301, 8, 194, RAIL)
box(1031, 487, 365, 8, RAIL)
tile(665, 286, 91, 38, '정차점', RAIL, 21)
tile(1353, 472, 86, 38, '파츠', RAIL, 22)
tile(1180, 482, 85, 38, '버튼', GATE, 22)
tile(1451, 481, 113, 39, '회수', GATE, 21)
tile(1890, 338, 100, 44, '공벌레', BUG)
label(2068, 234, '↓ 전투방', 24, bold=True)
label(2060, 338, '안전 착지', 24, bold=True)
label(1624, 280, '짧은 점프 연속', 24)
label(1292, 312, '① 낙하 ↓', 25, bold=True)
label(1136, 432, '② 버튼 밟아 레일 가동', 23, GATE, True)
label(1073, 378, '③ E 장착 → 왼쪽 + X', 25, RAIL, True)
label(1064, 304, '↑ 유물 파츠 상승', 23, RAIL, True)
label(459, 244, '④ 정차 후 E → 출구 발판에 착지', 26, RAIL, True)
label(115, 275, '← 바닥을 따라 계속 이동', 25)
label(105, 441, '착지점 왼쪽에 연속 바닥', 26, GATE, True)
label(105, 480, '착지 후 추가 점프 없이 A로 진행', 24)
label(859, 454, '일찍 E를 누르면', 21, GATE, True)
label(857, 488, '안전 바닥 → 회수', 20, GATE)

# 03–04. The low path returns to the horizontal rail dock.
strip(575, '04  방패병 회랑', '03  레일 2 · 넓은 틈 건너기', 'A', 'B')
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
strip(998, '06  수정 골렘 · 안전 전실 · 보스방 연결', '05  레일 3 · 중간 하차 또는 끝 착지', 'B', '끝')
terrain((175, 1285, 1186, 25), (1280, 1220, 280, 22), (1110, 1252, 135, 22),
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
for y in (1185, 1213, 1241, 1269):
    box(175, y, 7, 16, GATE)
steps((182, 1279, 385, 6))
tile(279, 1224, 172, 41, '안전 전실', SAFE, 22, INK)
label(82, 1125, '← 별도 B1 방으로', 26, GATE, True)
label(83, 1160, '여기서 통로 끝', 22, GATE)
label(1144, 1080, '끝에서 E → 상단에 여유 있게 착지', 24, RAIL, True)
label(1645, 1099, '중간에 E → 벽 슬라이드 · 벽점프', 24, RAIL, True)
label(795, 1149, '높은 길에서 접근', 24)
label(811, 1231, '아래로 내려 합류', 24)
label(172, 1337, '전실에서 쉬고 왼쪽 연결 입구로', 23)
label(1555, 1314, '아래 회수로 →', 23, GATE, True)

for x, name, color in [(48, '지형', GROUND), (345, '유물 설치', RELIC), (690, '레일 · 파츠', RAIL),
                       (1080, '구제 발판 · 안전 지점', SAFE), (1625, '몬스터', SHIELD), (1940, '문 · 스위치', GATE)]:
    box(x, 1446, 26, 26, color)
    label(x + 40, 1439, name, 27)
label(48, 1510, '수직 상승 → 수평 횡단 → 하차 타이밍 선택. 레일마다 다른 이동을 요구한다.', 28, bold=True)
label(48, 1550, '안전 바닥에서 해당 출발대로 복귀  ·  회수 손잡이로 이미 보낸 파츠 재정렬', 24, MUTED)
image.save(OUT)
