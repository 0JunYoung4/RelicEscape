"""Save analytical regions of interest and labeled reference boards."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
SPECS={
 "SS-MG-02":[("전경 큰 잎","foreground",(.02,.65,.27,.99)),("보행 띠와 작은 적","surface",(.28,.72,.62,.91)),("흐린 뒤 이끼 언덕","background",(.15,.12,.66,.62)),("위쪽 부드러운 빛","light",(.43,.01,.61,.51))],
 "SS-SH-06":[("전경 천장 가림","foreground",(.57,.01,.99,.46)),("중간의 굵은 뿌리","midground",(.04,.38,.36,.82)),("사선 빛과 입자","light",(.34,.13,.62,.70)),("읽히는 낮은 길","surface",(.12,.81,.78,.91))],
 "SS-UW-01":[("천장 검은 실루엣","foreground",(.38,0,.57,.30)),("지면의 작은 조형물","midground",(.22,.61,.35,.84)),("먼 석조 벽","background",(.28,.19,.66,.65)),("천장 틈과 수직빛","light",(.37,.05,.58,.79))],
 "SS-DD-05":[("선명한 앞 화로와 사슬","midground",(.59,.04,.77,.75)),("흐린 뒤 화로","background",(.06,.07,.17,.66)),("위험 재질의 밝은 면","light",(.04,.84,.95,.99)),("여러 높이의 기계 외형","midground",(.19,.01,.56,.91))],
 "SS-CK-06":[("거대하고 흐린 뒤 기어","background",(.02,.01,.65,.94)),("작고 선명한 앞 난간","midground",(.65,.44,.87,.60)),("발판의 검은 내부","surface",(.69,.67,.98,.99)),("밝은 뒤 대기층","light",(.05,.09,.25,.72))],
 "SS-MF-04":[("따뜻한 작은 광원","light",(.19,.33,.28,.63)),("작은 벤치","midground",(.32,.60,.44,.73)),("차가운 바깥 재질","background",(.81,.40,.99,.86)),("어두운 천장 프레임","foreground",(.05,.01,.56,.27))],
 "HK-CT-05":[("좌우 다른 높이의 발판","surface",(.01,.26,.28,.61)),("앞쪽 긴 사슬","foreground",(.58,0,.62,.98)),("먼 큰 창과 기둥","background",(.22,.10,.56,.38)),("작은 흰 등불","light",(.05,.35,.15,.44))],
 "HK-DN-04":[("앞을 가로지르는 실","foreground",(.27,.01,.44,.97)),("큰 문과 중간 구조","midground",(.26,.05,.72,.97)),("높이가 다른 작은 발판","surface",(.11,.76,.30,.98)),("작은 문틈 빛","light",(.47,.42,.54,.61))],
 "HK-WP-06":[("선명한 작은 발판","surface",(.29,.63,.39,.75)),("밝은 원경 창","background",(.40,.64,.47,.88)),("크기가 다른 원형 신호","midground",(.69,.01,.98,.31)),("뾰족한 왼쪽 경계","surface",(0,.05,.05,.91))],
 "SS-SK-02":[("명료한 안전면","surface",(.16,.76,.51,.88)),("따뜻한 색의 가시","surface",(.53,.72,.99,.94)),("작은 노란 광원","light",(.78,.20,.84,.33)),("검은 지형 속","foreground",(.01,.01,.19,.52))],
 "SS-WV-05":[("낮은 중앙 장치 외형","midground",(.34,.66,.68,.89)),("작은 따뜻한 광원 군집","light",(.13,.24,.92,.63)),("중앙 뒤 세로벽","background",(.35,.03,.62,.66)),("하단 검은 가림","foreground",(.04,.82,.21,.99))],
 "SS-ME-01":[("검은 코어와 이끼 경계","surface",(.06,.43,.33,.82)),("높은 실제 모양의 발판","surface",(.37,.01,.60,.13)),("중앙의 낮은 문","midground",(.43,.66,.61,.95)),("먼 세로빛과 안개","light",(.42,.22,.60,.60)),("따뜻한 위험 외곽","surface",(.01,.01,.14,.39))],
}
BOARD=[("SS-MG-02","이끼 통로","큰 형태와 재질 군집"),("SS-SH-06","유물 조명","틈빛과 앞뒤 레이어"),("SS-UW-01","유물 획득 지점","중앙 집중광과 여백"),
       ("HK-CT-05","중앙 통로","다른 높이의 길과 뒤 기둥"),("SS-CK-06","고대 장치 구역","실제 경로와 거대 뒤 기계"),("SS-DD-05","장치 배경 외형","사슬 화로의 깊이와 크기"),
       ("SS-SK-02","위험 구간","안전면과 가시의 다른 외곽"),("SS-WV-05","문양의 성소","큰 문양과 작은 광원 군집"),("SS-ME-01","성소 접근로","세로 길과 중앙의 문"),
       ("SS-MF-04","휴식 포켓","따뜻한 국소빛과 차가운 외부"),("HK-DN-04","수직 랜드마크","다른 높이의 발판과 목표"),("HK-WP-06","밝은 특수 공간","반전된 명암과 작은 안전면")]


def main():
    rows=json.loads((ROOT/"analysis.json").read_text(encoding="utf-8"));lookup={r["id"]:r for r in rows}
    dest=ROOT/"analysis";dest.mkdir(exist_ok=True)
    font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",23)
    small=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",19)
    colors=["#ffd17c","#7cdbc3","#9abaff","#f4a9dc","#d1e48c"]
    annotations=[]
    for key,marks in SPECS.items():
        row=lookup[key];out=Image.new("RGB",(1520,1120),"#0b1821")
        with Image.open(ROOT/row["local_file"]) as source:
            im=source.convert("RGB").resize((1440,810));out.paste(im,(40,88))
        d=ImageDraw.Draw(out);d.text((40,24),key+"  "+row["title"],font=font,fill="white")
        regions=[]
        for n,(label,kind,bounds) in enumerate(marks):
            x1,y1,x2,y2=bounds;x1=40+x1*1440;y1=88+y1*810;x2=40+x2*1440;y2=88+y2*810
            d.rectangle((x1,y1,x2,y2),outline=colors[n],width=4)
            d.rectangle((x1,y1,x1+34,y1+35),fill=colors[n]);d.text((x1+8,y1+1),str(n+1),font=font,fill="#0b1821")
            d.text((40+n%2*740,925+n//2*43),f"{n+1}. {label}",font=font,fill=colors[n])
            regions.append(dict(label=label,kind=kind,bbox=list(bounds)))
        d.text((40,1065),"시각적 관찰 영역 · 실제 엔진 레이어/충돌 마스크 아님 · 출처는 갤러리의 같은 ID",font=small,fill="#a3bdc7")
        file=f"analysis/{key.lower()}-annotated.jpg";out.save(ROOT/file,quality=94)
        annotations.append(dict(id=key,image=row["local_file"],annotated_image=file,
            coordinate_space="normalized xyxy, origin=source top-left",interpretation="visual ROI, not segmentation or collision",regions=regions))
    (ROOT/"annotations.json").write_text(json.dumps(annotations,ensure_ascii=False,indent=2),encoding="utf-8")
    board=Image.new("RGB",(1600,1560),"#0b1821");d=ImageDraw.Draw(board)
    for n,(key,target,label) in enumerate(BOARD):
        x=(n%3)*533;y=(n//3)*390
        with Image.open(ROOT/lookup[key]["local_file"]) as source:
            im=source.convert("RGB");im.thumbnail((521,294));board.paste(im,(x+(533-im.width)//2,y+8))
        d.text((x+10,y+312),key+" · "+target,font=small,fill="#b8e4cc")
        d.text((x+10,y+346),label,font=small,fill="#e4edf0")
    board.save(dest/"project-reference-board.jpg",quality=94)
    print("Saved 12 annotated images, 49 visual ROIs, 1 project reference board")


if __name__=="__main__":main()
