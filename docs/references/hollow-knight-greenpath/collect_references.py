"""Download attributed study references; does not create production game assets."""
import concurrent.futures
import hashlib
import html
import io
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://hollowknight.wiki/'}

def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30) as response:
        return response.read()

def wiki(name, region, key):
    filename = name.replace(' ', '_') + '.png'
    digest = hashlib.md5(filename.encode()).hexdigest()
    base = f'https://cdn.wikimg.net/en/hkwiki/images'
    path = f'{digest[0]}/{digest[:2]}/{urllib.parse.quote(filename)}'
    return dict(id=key, region=region, title=name, source_page='https://hollowknight.wiki/w/File:' + urllib.parse.quote(filename), image_url=f'{base}/thumb/{path}/800px-{urllib.parse.quote(filename)}', original_url=f'{base}/{path}', publisher='Hollow Knight Wiki', edition='출시판 스크린샷', credit='Team Cherry / Hollow Knight Wiki')

def candidates():
    rows = [wiki(f'Screenshot HK Greenpath {n:02}', '녹색 거리', f'GP{n:02}') for n in range(1,12)]
    names = ['Screenshot HK The Hunter 01', 'Screenshot HK Nailmaster Sheo 01', 'Greenpath South Area', 'Lake of Unn Shrine Interior', 'Greenpath Central Bench(2)', 'Greenpath Obble Area(2)', "Greenpath Queen's Gardens Connection"]
    rows += [wiki(name, '녹색 거리', f'GP{n:02}') for n,name in enumerate(names,12)]
    blog = 'https://www.teamcherry.com.au/blog/the-green-path-a-hollow-knight-tour'
    markup = fetch(blog).decode()
    for n,name in enumerate(['Fungus_05.jpg','Fungus_04.jpg','Fungus_03.jpg'],19):
        match = re.search(r'https://images\.squarespace-cdn\.com/[^"<>\s]*?/' + re.escape(name), markup)
        if match:
            rows.append(dict(id=f'GP{n:02}',region='녹색 거리',title=name,source_page=blog,image_url=html.unescape(match[0]),publisher='Team Cherry',edition='개발 중 공식 자료',credit='Team Cherry'))
    guide = 'https://www.monster-soluce.com/jeux/hollow-knight/guide-solution/vertchemin-guide-exploration-et-secrets-boss-personnages'
    markup = fetch(guide).decode()
    for n,asset in enumerate(range(14249,14258),22):
        match = re.search(r'(?:https://www\.monster-soluce\.com)?/uploads/scale-[^"<>\s]*?/' + str(asset) + r'[^"<>\s]*?\.jpg', markup)
        if match:
            url = urllib.parse.urljoin(guide, html.unescape(match[0])).replace('scale-small','scale-max').replace('scale-medium','scale-max')
            rows.append(dict(id=f'GP{n:02}',region='녹색 거리',title=url.rsplit('/',1)[1],source_page=guide,image_url=url,publisher='Monster Soluce',edition='출시판 플레이 스크린샷',credit='Team Cherry / Monster Soluce'))
    others=[("Screenshot HK Queen's Gardens 01",'여왕의 정원'),("Screenshot HK Queen's Gardens 02",'여왕의 정원'),('Screenshot HK Fog Canyon 01','안개 협곡'),('Screenshot HK Fungal Wastes 01','버섯 황무지'),('Screenshot HK City of Tears 01','눈물의 도시'),('Screenshot HK Crystal Peak 01','수정 봉우리')]
    rows += [wiki(name,region,f'EX{n:02}') for n,(name,region) in enumerate(others,1)]
    enemies = ['Moss Charger', 'Mosskin', 'Volatile Mosskin', 'Moss Knight', 'Gulka', 'Fool Eater', 'Obble', 'Squit', 'Duranda']
    rows += [wiki('Screenshot HK ' + name + ' 01', '녹색 거리', f'GP{n:02}') for n,name in enumerate(enemies,31)]
    rows.sort(key=lambda row:(row['id'].startswith('EX'),row['id']))
    return rows

def download(row):
    try:
        suffix = '.jpg' if '.jpg' in row['image_url'].lower() else '.png'
        dest = ROOT / 'images' / (row['id'].lower() + suffix)
        data = dest.read_bytes() if dest.exists() else fetch(row['image_url'])
        im = Image.open(io.BytesIO(data)); im.load()
        if im.width < 600 or im.height < 300:
            raise ValueError(f'insufficient resolution {im.size}')
        dest.write_bytes(data)
        row.update(local_file=dest.relative_to(ROOT).as_posix(),width=im.width,height=im.height,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),accessed='2026-11-23',status='downloaded',study_only=True)
        return row
    except Exception as error:
        return dict(row,status='failed',error=str(error))

def sheets(rows):
    font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',18)
    for page in range((len(rows)+11)//12):
        board=Image.new('RGB',(1600,1140),'#101d24'); draw=ImageDraw.Draw(board)
        for k,row in enumerate(rows[page*12:(page+1)*12]):
            x=(k%4)*400;y=(k//4)*380
            im=Image.open(ROOT/row['local_file']).convert('RGB');im.thumbnail((392,300))
            board.paste(im,(x+(400-im.width)//2,y+12))
            draw.text((x+8,y+312),row['id']+' '+row['region'],fill='#bde0c7',font=font)
            draw.text((x+8,y+340),row['title'][:37],fill='white',font=font)
        board.save(ROOT/f'contact-sheet-{page+1:02}.jpg',quality=92)

if __name__ == '__main__':
    (ROOT/'images').mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        rows=list(pool.map(download,candidates()))
    good=[row for row in rows if row['status']=='downloaded']
    (ROOT/'sources.json').write_text(json.dumps(good,ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'download-log.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    sheets(good)
    print(json.dumps({'downloaded':len(good),'greenpath':sum(r['region']=='녹색 거리' for r in good),'failures':[{k:r.get(k) for k in ('id','title','error')} for r in rows if r['status']=='failed']},ensure_ascii=False))
