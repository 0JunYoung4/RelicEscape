"""Draw a rectangle-only level design proposal; no gameplay code is changed."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'map1-lower-route-blockout-v1.png'
im = Image.new('RGB', (2400, 1550), '#f4f5f7')
d = ImageDraw.Draw(im)
FONT = 'C:/Windows/Fonts/malgun.ttf'
BOLD = 'C:/Windows/Fonts/malgunbd.ttf'
C = dict(ground='#596574', room='#e5e9ef', relic='#188b9a', bug='#ba7033', golem='#735ca4', shield='#be5264', gate='#357c55', hazard='#e1b0b6', ink='#243142')
def rect(box, fill, outline=None, width=2):
    d.rectangle(box, fill=fill, outline=outline, width=width)
def text(x, y, s, size=24, color=None, bold=False):
    d.text((x, y), s, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color or C['ink'])
def block(x, y, w, h, label, color):
    rect((x,y,x+w,y+h),color)
    f=ImageFont.truetype(BOLD,22)
    b=d.textbbox((0,0),label,font=f)
    d.text((x+(w-b[2])/2,y+(h-b[3])/2-2),label,font=f,fill='white')
def dash_h(x1,x2,y,color):
    for x in range(x1,x2,24): rect((x,y,min(x+13,x2),y+5),color)
def dash_v(x,y1,y2,color):
    for y in range(y1,y2,24): rect((x,y,x+5,min(y+13,y2)),color)

text(55,28,'전투방 아래 → 첫 보스 B1 | 사각형 레벨디자인',42,bold=True)
text(55,92,'진행: 오른쪽에서 착지 후 왼쪽으로  /  유물 필수 퍼즐 1회 + 전투 활용 1회  /  배치·장치 동작은 설계 제안',25)
zones=[(55,455,'05  첫 보스 B1'),(475,700,'04  안전 전실'),(720,1160,'03  혼합 전투'),(1180,1810,'02  유물 필수'),(1830,2345,'01  착지·기본 이동')]
for x1,x2,label in zones:
    rect((x1,154,x2,207),'#dce2e9')
    text(x1+13,164,label,26,bold=True)
    text(x1+12,218,'진행 방향: 왼쪽',21,color='#687488')

# Continuous side view. Terrain, enemies, hazards and routes are rectangles only.
rect((55,278,2345,1110),C['room'])
rect((55,278,2130,315),C['ground'])
rect((2280,278,2345,650),C['ground'])
rect((55,315,85,700),C['ground'])
rect((55,700,1175,750),C['ground'])
rect((1210,700,1440,750),C['ground'])
rect((1620,700,2345,750),C['ground'])
# Top right descent from existing encounter.
rect((2080,255,2320,290),'#dce2e9')
text(2095,258,'기존 전투방',24,bold=True)
dash_v(2205,320,605,'#8793a2')
text(2220,362,'하강',22)
text(2100,640,'안전 착지',23,bold=True)
block(1940,652,90,48,'공벌레',C['bug'])
rect((1835,570,1900,700),C['ground'])
rect((1750,640,1795,700),C['ground'])
text(1825,500,'짧은 단차',23)
text(1825,533,'벽점프 1회',22)
# Mandatory relic detour: leave anchor above, descend to switch, teleport back.
block(1645,650,78,50,'유물 A',C['relic'])
text(1640,597,'① 위에 설치',23,color=C['relic'],bold=True)
rect((1440,700,1620,716),'#95c5c9',C['relic'])
text(1445,645,'② 낙하구',23,bold=True)
rect((1180,760,1440,805),C['ground'])
rect((1180,760,1215,1045),C['ground'])
rect((1620,716,1660,1045),C['ground'])
rect((1180,1045,1660,1080),C['ground'])
block(1250,990,125,55,'스위치 S',C['gate'])
text(1250,855,'③ 아래 스위치 작동',24,bold=True)
text(1250,892,'상부 문 열림 + 낙하구 닫힘',22)
text(1250,931,'도보 출구 없음 → E로 복귀',22,color=C['relic'])
dash_v(1555,736,1000,'#7d8899')
dash_h(1390,1555,1000,'#7d8899')
dash_h(1680,1775,1020,C['relic'])
dash_v(1770,700,1020,C['relic'])
dash_h(1730,1775,700,C['relic'])
text(1680,840,'④ E',25,color=C['relic'],bold=True)
text(1680,880,'A로 복귀',23,color=C['relic'])
text(1680,918,'자동 회수',21,color=C['relic'])
block(1175,315,35,435,'문',C['gate'])
text(1090,480,'S로 개방',23,color=C['gate'],bold=True)
dash_h(1220,1415,570,C['gate'])
text(1240,528,'⑤ 닫힌 덮개 위로 왼쪽 진행',23,color=C['gate'])
# Combat: shield faces the approaching player; upper golem supports it.
block(975,650,115,50,'유물 B',C['relic'])
block(835,620,100,80,'방패병',C['shield'])
rect((925,622,940,697),'#7f3040')
text(815,558,'정면: 오른쪽',22,color=C['shield'])
rect((730,470,865,500),C['ground'])
rect((700,600,740,625),C['ground'])
block(747,410,100,60,'수정 골렘',C['golem'])
block(735,652,85,48,'공벌레',C['bug'])
text(745,345,'골렘은 위, 근접 적은 아래',22)
text(745,378,'탄환은 낮은 빈 공간으로',21)
text(770,795,'B 설치 → 방패병 넘어가기',23,color=C['relic'],bold=True)
text(770,835,'적이 왼쪽을 보면 E로 B 복귀',22)
text(770,875,'오른쪽 등 뒤에서 공격',22)
# Safe space and open arena.
rect((475,640,695,700),'#c7dfd4')
text(495,555,'적 없음',25,bold=True)
text(489,590,'보스 진입 준비',22)
text(485,795,'재도전 위치 후보',22)
rect((450,420,475,700),C['gate'])
text(313,362,'진입 경계',22)
block(170,590,155,110,'B1 골렘',C['golem'])
text(110,420,'넓고 평평한 바닥',23,bold=True)
text(110,458,'장애물·일반 적 없음',22)
block(340,650,80,50,'유물 C',C['relic'])
text(105,795,'C 설치 → 공격 유도 → 복귀',22)
text(105,835,'기존 골렘 기반 수문장 제안',21)

# Compact plain-rectangle legend and rules below the spatial diagram.
legend=[('지형',C['ground']),('유물 위치',C['relic']),('공벌레',C['bug']),('수정 골렘',C['golem']),('방패병',C['shield']),('문·스위치',C['gate'])]
for i,(label,col) in enumerate(legend):
    x=60+i*375
    rect((x,1145,x+28,1173),col)
    text(x+42,1140,label,25)
text(55,1210,'유물이 반드시 필요한 이유',30,bold=True)
text(55,1260,'S를 누르면 낙하구가 닫혀 위쪽으로 걸어 나갈 수 없다. 위에 남긴 유물 A로 복귀해야 열린 문을 통과한다.',26)
text(55,1308,'진입 조건: A 설치를 감지해야 낙하구 개방. S 작동 뒤 덮개는 다리가 되어 재낙하를 막는다. 복귀 시 유물 자동 회수.',24)
text(55,1375,'전투 배치: 공벌레 2 + 수정 골렘 1 + 방패병 1  /  B1은 별도  /  가시·레일·석궁은 이번 구간에서 제외',24)
text(55,1423,'검토 필요: 방패병의 방향 전환·등 뒤 피격, 스위치·덮개 연동, 적 사거리와 점프 높이는 구현·플레이 검증 전 제안.',23,color='#667386')
text(55,1470,'축척 없는 구조도 · 위→아래 낙하 / 오른쪽→왼쪽 진행 · 사각형과 텍스트만 사용',22,color='#667386')
im.save(OUT)
print(OUT)
