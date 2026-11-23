"""Collect and deduplicate attributed map references; never exports game assets."""
from concurrent.futures import ThreadPoolExecutor
import argparse
import hashlib
import io
import json
from pathlib import Path
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont, ImageStat

ROOT = Path(__file__).resolve().parent
LEGACY = ROOT.parent / "hollow-knight-greenpath"
HK = [
    ("FC", "Forgotten Crossroads"), ("FW", "Fungal Wastes"),
    ("CT", "City of Tears"), ("CP", "Crystal Peak"),
    ("DN", "Deepnest"), ("QG", "Queen's Gardens"),
    ("FCY", "Fog Canyon"), ("RW", "Royal Waterways"),
    ("AB", "Ancient Basin"), ("AY", "Abyss"),
    ("KE", "Kingdom's Edge"), ("HI", "Hive"),
    ("RG", "Resting Grounds"), ("HC", "Howling Cliffs"),
    ("WP", "White Palace"),
]
SS = [
    ("MG", "Moss Grotto"), ("BB", "Bone Bottom"),
    ("MA", "Marrow"), ("DD", "Deep Docks"),
    ("FF", "Far Fields"), ("HM", "Hunter's March"),
    ("SH", "Shellwood"), ("GM", "Greymoor"),
    ("BH", "Bellhart"), ("BW", "Bilewater"),
    ("BS", "Blasted Steps"), ("SR", "Sinner's Road"),
    ("MF", "Mount Fay"), ("SK", "Sands of Karak"),
    ("WW", "Wormways"), ("UW", "Underworks"),
    ("CC", "Choral Chambers"), ("WV", "Whispering Vaults"),
    ("WH", "Whiteward"), ("HH", "High Halls"),
    ("CK", "Cogwork Core"), ("ME", "Memorium"),
]


def wiki(game, code, region, number):
    filename = f"Screenshot {game} {region} {number:02}.png".replace(" ", "_")
    digest = hashlib.md5(filename.encode()).hexdigest()
    name = urllib.parse.quote(filename)
    path = f"{digest[0]}/{digest[:2]}/{name}"
    return dict(id=f"{game}-{code}-{number:02}", game=game, region=region,
                source_title=filename.replace("_", " "),
                source_page="https://hollowknight.wiki/w/File:" + name,
                image_url=f"https://cdn.wikimg.net/en/hkwiki/images/thumb/{path}/800px-{name}",
                original_url=f"https://cdn.wikimg.net/en/hkwiki/images/{path}",
                credit="Team Cherry / Hollow Knight Wiki", accessed="2026-11-23",
                edition="위키 게임 스크린샷", study_only=True)


def signatures(data):
    with Image.open(io.BytesIO(data)) as source:
        im = source.convert("RGB")
        gray = im.convert("L").resize((9, 8))
        values = gray.tobytes()
        bits = [values[y * 9 + x] > values[y * 9 + x + 1] for y in range(8) for x in range(8)]
        dhash = sum(int(bit) << n for n, bit in enumerate(bits))
        small = im.resize((160, 90))
        rgb_bytes = small.tobytes()
        pixels = [rgb_bytes[i:i+3] for i in range(0,len(rgb_bytes),3)]
        dark = sum(max(p) < 28 for p in pixels) / len(pixels)
        bright = sum(min(p) > 200 for p in pixels) / len(pixels)
        # Dominant swatches describe the whole frame, including UI and dark terrain.
        quantized = small.quantize(colors=6)
        palette = quantized.getpalette()
        swatches = []
        for count, index in sorted(quantized.getcolors(), reverse=True):
            rgb = palette[index * 3:index * 3 + 3]
            swatches.append(dict(hex="#" + "".join(f"{c:02x}" for c in rgb), fraction=round(count / 14400, 4)))
        return dict(width=im.width, height=im.height, sha256=hashlib.sha256(data).hexdigest(),
                    pixel_sha256=hashlib.sha256(im.width.to_bytes(4,"big") + im.height.to_bytes(4,"big") + im.tobytes()).hexdigest(),
                    dhash=f"{dhash:016x}", metrics=dict(dark_pixel_fraction=round(dark,4),
                    bright_pixel_fraction=round(bright,4), mean_rgb=[round(v,1) for v in ImageStat.Stat(small).mean],
                    palette=swatches, method="RGB160x90; dark=max(RGB)<28; bright=min(RGB)>200; frame includes UI"))


def download(row):
    path = ROOT / "images" / (row["id"].lower() + ".png")
    try:
        if path.exists():
            data = path.read_bytes()
        else:
            req = urllib.request.Request(row["image_url"], headers={"User-Agent":"Mozilla/5.0", "Referer":"https://hollowknight.wiki/"})
            with urllib.request.urlopen(req, timeout=22) as response:
                data = response.read()
        info = signatures(data)
        if info["width"] < 640 or info["height"] < 300:
            raise ValueError("Image is too small for a map reference")
        path.write_bytes(data)
        return dict(row, **info, bytes=len(data), local_file=path.relative_to(ROOT).as_posix(), status="downloaded", origin="new")
    except Exception as error:
        return dict(row, status="failed", error=str(error))


def contacts(rows):
    (ROOT / "contact-sheets").mkdir(exist_ok=True)
    font=ImageFont.truetype("C:/Windows/Fonts/malgun.ttf",16)
    for page in range((len(rows)+11)//12):
        out=Image.new("RGB",(1600,990),"#0b1821");draw=ImageDraw.Draw(out)
        for n,row in enumerate(rows[page*12:(page+1)*12]):
            x=(n%4)*400;y=(n//4)*330
            with Image.open(ROOT/row["local_file"]) as source:
                im=source.convert("RGB");im.thumbnail((392,264));out.paste(im,(x+(400-im.width)//2,y+8))
            draw.text((x+8,y+274),row["id"],font=font,fill="#b8e4cc")
            draw.text((x+8,y+299),row["region"],font=font,fill="#edf3f5")
        out.save(ROOT/"contact-sheets"/f"sheet-{page+1:02}.jpg",quality=94)


def main():
    parser=argparse.ArgumentParser(description="공개 맵 이미지를 기존 자료에 누적 수집")
    parser.add_argument("--max-per-region",type=int,default=6)
    parser.add_argument("--game",choices=["HK","SS","both"],default="both")
    parser.add_argument("--region",default="")
    parser.add_argument("--accessed",default="2026-11-23")
    args=parser.parse_args()
    if not 1<=args.max_per_region<=30:parser.error("--max-per-region must be 1..30")
    (ROOT/"images").mkdir(parents=True,exist_ok=True)
    rows=[]
    for old in json.loads((LEGACY/"analysis.json").read_text(encoding="utf-8")):
        data=(LEGACY/old["local_file"]).read_bytes()
        rows.append(dict(old, id="HK-"+old["id"], game="HK", source_title=old["title"],
                         local_file="../hollow-knight-greenpath/"+old["local_file"],
                         origin="legacy", **signatures(data)))
    # Retain earlier batches even when a follow-up collects just one region.
    previous_file=ROOT/"sources.json"
    if previous_file.exists():
        for previous in json.loads(previous_file.read_text(encoding="utf-8")):
            if previous["origin"]=="new":
                if not (ROOT/previous["local_file"]).exists():
                    raise FileNotFoundError(previous["local_file"])
                rows.append(previous)
    initial_count=len(rows)
    known={row["image_url"] for row in rows}
    candidates=[wiki(game,code,region,n) for game,regions in (("HK",HK),("SS",SS))
                if args.game in (game,"both") for code,region in regions
                if args.region.casefold() in region.casefold()
                for n in range(1,args.max_per_region+1)]
    candidates=[row for row in candidates if row["image_url"] not in known]
    for row in candidates:row["accessed"]=args.accessed
    with ThreadPoolExecutor(max_workers=6) as pool:
        results=list(pool.map(download,candidates))
    log=[];seen_bytes={row["sha256"]:row["id"] for row in rows};seen_pixels={row["pixel_sha256"]:row["id"] for row in rows}
    for row in results:
        if row["status"]=="downloaded":
            duplicate=seen_bytes.get(row["sha256"]) or seen_pixels.get(row["pixel_sha256"])
            if duplicate:
                row=dict(row,status="duplicate",duplicate_of=duplicate)
            else:
                rows.append(row);seen_bytes[row["sha256"]]=row["id"];seen_pixels[row["pixel_sha256"]]=row["id"]
        log.append(row)
    for i,row in enumerate(rows):
        nearest=[]
        for previous in rows[:i]:
            if previous["game"]==row["game"] and previous["region"]==row["region"]:
                distance=(int(row["dhash"],16)^int(previous["dhash"],16)).bit_count()
                if distance<=4:nearest.append(dict(id=previous["id"],dhash_distance=distance))
        row["similar_frames"]=nearest
    (ROOT/"sources.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
    log_path=ROOT/"download-log.json"
    old_log=json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
    combined={row["id"]:row for row in old_log}
    combined.update({row["id"]:row for row in log})
    log_path.write_text(json.dumps(list(combined.values()),ensure_ascii=False,indent=2),encoding="utf-8")
    contacts(rows)
    print(json.dumps(dict(total=len(rows),added_this_run=len(rows)-initial_count,legacy=sum(r["origin"]=="legacy" for r in rows),new=sum(r["origin"]=="new" for r in rows),
        HK=sum(r["game"]=="HK" for r in rows),SS=sum(r["game"]=="SS" for r in rows),
        failed=[dict(id=r["id"],error=r.get("error")) for r in log if r["status"]=="failed"],
        duplicates=[dict(id=r["id"],duplicate_of=r["duplicate_of"]) for r in log if r["status"]=="duplicate"]),ensure_ascii=True))


if __name__=="__main__":
    main()
