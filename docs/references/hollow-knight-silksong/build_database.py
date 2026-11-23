"""Build the project reference database, production briefs and offline gallery."""
from collections import Counter
import csv
import html
import json
from pathlib import Path

from production_patterns import patterns, assets

ROOT=Path(__file__).resolve().parent
ALIASES={"녹색 거리":"Greenpath","여왕의 정원":"Queen's Gardens","안개 협곡":"Fog Canyon",
         "버섯 황무지":"Fungal Wastes","눈물의 도시":"City of Tears","수정 봉우리":"Crystal Peak",
         "Abyss":"The Abyss","Hive":"The Hive"}
TAG_PATTERNS={"휴식":["P10"],"조명":["P04"],"레이어":["P03"],"그림자":["P01","P02"],
              "맵":["P05"],"위험":["P07"],"유적":["P16"],"텍스처":["P12"],"전투":["P11"],
              "몬스터":["P15"],"랜드마크":["P16"],"전이":["P09"],"수직":["P05"],
              "탐색":["P08"],"상호작용":["P06"],"개발판":["P12"]}
PRIMARY_TARGETS={"수평 통로":["중앙 통로"],"복층 공간":["중앙 통로","고대 장치 구역"],
    "수직 이동":["중앙 통로","하강 통로"],"전투 공간":["전투방","보스방"],
    "열린 방":["전투방","보스방"],"휴식 포켓":["전투 후 휴식 지점","보상 포켓"],
    "보상 포켓":["보상 포켓","유물 획득 지점"],"목표 노출":["유물 획득 지점","보상 포켓"],
    "지역 경계":["중앙 통로","문양의 성소"],"장치 공간":["고대 장치 구역"],
    "장치 외형":["고대 장치 구역"],"재질 상세":["고대 장치 구역"],
    "조명 상세":["유물 획득 지점","문양의 성소"],"시네마틱 효과":["유물 획득 연출","보스 등장 연출"],
    "상태 변형":["고대 장치 구역","보스 처치 후"],"랜드마크":["중앙 통로","문양의 성소"],
    "위험 구간":["고대 장치 구역","보스 접근 구간"]}
TARGET_OVERRIDES={"SS-UW-01":["유물 획득 지점","문양의 성소"],
    "SS-SH-06":["유물 획득 지점","이끼 통로"],"SS-ME-04":["유물 획득 지점","문양의 성소"],
    "SS-MG-02":["이끼 통로"],"SS-MG-03":["이끼 통로","하강 통로"],
    "SS-WV-05":["문양의 성소"],"SS-ME-01":["문양의 성소","중앙 통로"],
    "SS-CK-06":["고대 장치 구역","중앙 통로"],"HK-CT-05":["중앙 통로","하강 통로"],
    "HK-AY-05":["문양의 성소","유물 획득 지점"]}


def load_records():
    observations={}
    legacy_curation={}
    for line in (ROOT/"legacy-curation.txt").read_text(encoding="utf-8").splitlines():
        key,layout,materials,targets=line.split("|")
        if key in legacy_curation:raise ValueError("Repeated legacy curation " + key)
        legacy_curation[key]=dict(layout=layout,materials=materials.split(","),project_targets=targets.split(","))
    for path in sorted(ROOT.glob("observations-*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            key,title,layout,observation,materials,depth,light,uses=line.split("|")
            if key in observations:raise ValueError("Repeated observation " + key)
            observations[key]=dict(title=title,layout=layout,observation=observation,
                materials=materials.split(","),depth_interpretation=depth,lighting=light,patterns=uses.split(","))
    rows=json.loads((ROOT/"sources.json").read_text(encoding="utf-8"))
    pattern_map={p["id"]:p for p in patterns()}
    for index,row in enumerate(rows):
        curated_targets=None
        row["region"]=ALIASES.get(row["region"],row["region"])
        if row["origin"]=="new":
            row.update(observations.pop(row["id"]))
        else:
            tags=row["tags"]
            row["title"]=row["label"]
            row["observation"]=row["composition"]+" "+row["texture"]
            row["depth_interpretation"]=row["layers"]
            row["patterns"]=sorted({p for t in tags for p in TAG_PATTERNS.get(t,[])}) or ["P12"]
            row.update(legacy_curation.pop(row["id"]))
            curated_targets=row["project_targets"]
        if row["id"] in ("SS-MF-01","SS-DD-01","HK-GP33","HK-GP37","HK-CP-03"):
            row["patterns"]=sorted(set(row["patterns"]+["P14"]))
        row["scope"]=("pre_release" if "개발 중" in row["edition"] else
                       "effect" if row["layout"]=="시네마틱 효과" else
                       "detail" if "상세" in row["layout"] else
                       "state_variant" if row["layout"]=="상태 변형" else "scene")
        broad_targets={t for p in row["patterns"] for t in pattern_map[p]["targets"]}
        row["project_targets"]=list(PRIMARY_TARGETS[row["layout"]])
        if row["layout"]=="수평 통로" and any(m in row["materials"] for m in ("잎","이끼","덩굴")):
            row["project_targets"]=["이끼 통로","중앙 통로"]
        if row["id"] in TARGET_OVERRIDES:row["project_targets"]=TARGET_OVERRIDES[row["id"]]
        if curated_targets:
            # Preserve manual production targets rather than keyword inference.
            row["project_targets"]=curated_targets
        row["secondary_project_targets"]=sorted(broad_targets-set(row["project_targets"]))
        row["asset_briefs"]=sorted({a for p in row["patterns"] for a in pattern_map[p]["asset_briefs"]})
        row["priority"]=min(pattern_map[p]["priority"] for p in row["patterns"])
        light=row["lighting"]
        row["lighting_types"]=[name for name,keys in [("사선광",["사선"]),("천장빛",["천장","위쪽","위에서"]),
            ("국소광",["등불","국소","작은 빛","중심광"]),("대기광",["대기광","안개","주변광","산란","광막"]),
            ("후광",["후광","번짐"]),("밝은 면",["수면","백색","흰색","황금","주황빛"]),
            ("명암 반전",["밝은 원경","밝은 지역","어두운 윤곽"])] if any(k in light for k in keys)] or ["낮은 주변광"]
        row["review"]=dict(status="visual_reviewed",date="2026-11-23",method="연락표 시각 검토 및 선별 원본 확인",
                           interpretation="정지 화면의 시각적 해석. 원작 엔진 레이어·충돌·시차 속도·효과 시간은 확정하지 않음")
        row["contact_sheet"]=f"contact-sheets/sheet-{index//12+1:02}.jpg"
        row["similar_frames"]=[]
        for other in rows[:index]:
            if other["game"]==row["game"]:
                distance=(int(row["dhash"],16)^int(other["dhash"],16)).bit_count()
                if distance<=4:
                    row["similar_frames"].append(dict(id=other["id"],dhash_distance=distance))
    if observations:raise ValueError("Unused observations " + str(sorted(observations)))
    if legacy_curation:raise ValueError("Unused legacy curation " + str(sorted(legacy_curation)))
    assert len({r["sha256"] for r in rows})==len(rows)
    assert len({r["pixel_sha256"] for r in rows})==len(rows)
    return rows


def save_json(path,value):
    (ROOT/path).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding="utf-8")


def write_exports(rows):
    pats=patterns();briefs=assets()
    for p in pats:p["reference_ids"]=[r["id"] for r in rows if p["id"] in r["patterns"]]
    for b in briefs:b["reference_ids"]=[r["id"] for r in rows if b["id"] in r["asset_briefs"]]
    save_json("analysis.json",rows);save_json("patterns.json",pats);save_json("asset-briefs.json",briefs)
    with (ROOT/"analysis.jsonl").open("w",encoding="utf-8") as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    fields=["id","game","region","title","layout","scope","materials","patterns","project_targets","asset_briefs",
            "priority","observation","depth_interpretation","lighting","lighting_types","local_file","source_page","image_url",
            "width","height","sha256","pixel_sha256","dark_pixel_fraction","bright_pixel_fraction","similar_frames"]
    with (ROOT/"catalog.csv").open("w",encoding="utf-8-sig",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");writer.writeheader()
        for r in rows:
            flat=dict(r,dark_pixel_fraction=r["metrics"]["dark_pixel_fraction"],bright_pixel_fraction=r["metrics"]["bright_pixel_fraction"])
            for k,v in list(flat.items()):
                if isinstance(v,list):flat[k]="; ".join(x["id"] if isinstance(x,dict) else x for x in v)
            writer.writerow(flat)
    stats=dict(total=len(rows),new=sum(r["origin"]=="new" for r in rows),legacy=sum(r["origin"]=="legacy" for r in rows),
               games=dict(Counter(r["game"] for r in rows)),regions=len({(r["game"],r["region"]) for r in rows}),
               by_region=dict(Counter(r["game"]+" / "+r["region"] for r in rows)),scopes=dict(Counter(r["scope"] for r in rows)),
               patterns=len(pats),asset_briefs=len(briefs),similar_frame_records=sum(bool(r["similar_frames"]) for r in rows),
               bytes_new=sum(r["bytes"] for r in rows if r["origin"]=="new"))
    save_json("statistics.json",stats)
    save_json("dataset-manifest.json",dict(format_version="1.0",title="RelicEscape 맵 제작용 참고 데이터",
        snapshot_date="2026-11-23",counts=stats,
        files=dict(records="analysis.json",jsonl="analysis.jsonl",csv="catalog.csv",sources="sources.json",
                   patterns="patterns.json",asset_briefs="asset-briefs.json",annotations="annotations.json",
                   gallery="index.html",guide="../../reference-production-guide.md",project_targets="project-targets.json"),
        project_plan="본편 두 맵. 중앙 통로는 맵2 작은 중앙 홀, 문양의 성소는 맵2 최종 보스방에 통합. project-targets.json 참조",
        interpretation=dict(observation="이미지에서 읽히는 형태·재질·명암의 시각적 관찰",
                            application="프로젝트 적용 제안. 구현 여부는 패턴의 project_status와 최신 소스 확인",
                            spatial_labels="시각적 관심 영역이며 실제 엔진 레이어·충돌·세그멘테이션 아님",
                            metrics="UI 포함 전체 화면 RGB160x90의 계산값. 원작의 재질색·광량·카메라 설정 아님"),
        project_constraints=["시작 동굴과 최초 착지방 보존","승인된 벽·발판과 현재 충돌·이동감 유지",
            "천장 전경은 월드 천장에 고정","문틀 끝에 별도 덩굴을 붙이지 않음",
            "현재 전투방 적4·발판3·덮개112·개방/접근 조명 유지","유물은 청색 기능 신호를 장식과 구별",
            "연구 이미지를 게임 자산으로 직접 사용하지 않고 프로젝트 고유 자산 제작"],
        continuation="collect_references.py는 이전 배치를 보존. 신규 항목의 시각 관찰 없이는 build_database.py가 실패함"))
    return pats,briefs,stats


def write_readme(rows,pats,briefs,stats):
    parts=[f'''# 할로우 나이트와 실크송 프로젝트 참고 데이터

2026년11월23일 기준 **총{stats['total']}장**. 기존45장에 신규{stats['new']}장을 더했다. 할로우 나이트{stats['games']['HK']}장과 실크송{stats['games']['SS']}장, 게임별 지역을 구분해 총{stats['regions']}개 지역을 다룬다. 사진의 개수는 서로 다른 방의 개수가 아니다.

- [오프라인 검색 갤러리](index.html): 게임·지역·맵 용도·재질·조명·프로젝트 적용 구역으로 검색하고 두 장 비교.
- [프로젝트 제작 가이드](../../reference-production-guide.md): 지금 무엇을 만들고 어디에 쓸지 결정하는 순서.
- [분석 JSON](analysis.json) · [한 줄 한 이미지 JSONL](analysis.jsonl) · [CSV](catalog.csv) · [출처 원장](sources.json)
- [제작 패턴20개](patterns.json) · [자산 제작 명세20개](asset-briefs.json) · [통계](statistics.json)
- [최신 두 맵의 위치·구현 상태 대응](project-targets.json): 중앙 통로는 맵2 작은 중앙 홀, 문양의 성소는 맵2 최종 보스방의 문양·제단에 대응.
- [기존 녹색 거리 자료집](../hollow-knight-greenpath/README.md)

신규{stats['new']}장은 실제 PNG로 저장했고 기존45장은 원래 파일을 참조해 중복 복사를 피했다. 파일 및 디코딩된 RGB 픽셀 해시로 완전 중복을 제외했다. 비슷한 구도는 dHash 거리4 이하 후보를 따로 표시한다. 이 표시는 유사도 후보이며 같은 방·같은 원본이라고 확정하는 판정은 아니다.

개별 관찰은 시각적으로 확인한 화면 내용이고, P01~P20은 RelicEscape 적용 제안이다. 시작 동굴·최초 착지방 보존, 승인된 벽·발판, 현재 전투방 배치·충돌·카메라·덮개112·접근 조명은 유지 기준이다. 게임에 적용한 항목과 미구현 제안은 각 패턴의 현재 상태에서 구별한다.

## 데이터 활용 순서

1. 필요한 프로젝트 구역을 고른다. 예: 고대 장치 구역.
2. 용도와 제작 패턴을 고른다. 예: P06 장치 경로, P05 수직 이동.
3. 이미지의 관찰과 전경/배경·조명을 확인하고 두 장을 비교한다.
4. 연결된 B01~B20 제작 명세에서 기존 자산 재사용 여부와 충돌·시야 제약을 확인한다.
5. 프로젝트 고유 자산을 제작하고 실제 이동·전투 화면에서 검증한다.

CLI 예: `.\\.venv\\Scripts\\python.exe docs/references/hollow-knight-silksong/query_references.py --target "고대 장치 구역" --pattern P06 --limit 8`

원작 이미지와 문양은 연구용으로 보관한다. 게임에 직접 쓰는 제작 자산은 `assets/`에서 별도로 만든다. 이미지 권리는 Team Cherry 및 해당 권리자에게 있으며, Wiki의 이미지별 출처 페이지를 기록했다. 다운로드된 800px 이미지와 링크만 보관한 원본 URL을 구별한다.

## 지역별 자료

| 게임 | 지역 | 이미지 수 |
| --- | --- | ---: |
''']
    for name,count in stats["by_region"].items():
        game,region=name.split(" / ",1);parts.append(f"| {game} | {region} | {count} |\n")
    parts.append("\n## 제작 패턴\n\n| ID | 패턴 | 우선순위 | 적용 구역 |\n| --- | --- | --- | --- |\n")
    for p in pats:parts.append(f"| {p['id']} | {p['title']} | {p['priority']} | {', '.join(p['targets'])} |\n")
    parts.append("\n## 이미지별 관찰 목록\n\n")
    for r in rows:
        pmap={p["id"]:p for p in pats}
        uses=" / ".join(pmap[p]["title"] for p in r["patterns"])
        parts.append(f'''### {r['id']} {r['title']}

[이미지 보기]({r['local_file']}) · {r['game']} / {r['region']} · {r['layout']} · {', '.join(r['materials'])}

- 관찰: {r['observation']}
- 전경과 배경: {r['depth_interpretation']}
- 조명: {r['lighting']}
- 제작 패턴: {', '.join(r['patterns'])} — {uses}
- 적용 후보: {', '.join(r['project_targets'])} · 자산 명세 {', '.join(r['asset_briefs'])}
- [출처 페이지]({r['source_page']}) · [제공 이미지]({r['image_url']})

''')
    (ROOT/"README.md").write_text("".join(parts),encoding="utf-8")


def write_gallery(rows,pats,briefs,stats):
    esc=html.escape
    pmap={p["id"]:p for p in pats}
    cards=[]
    for r in rows:
        uses=" ".join(r["project_targets"])
        haystack=" ".join([r["id"],r["region"],r["title"],r["observation"],r["depth_interpretation"],r["lighting"],*r["materials"],*r["project_targets"],*r["patterns"],*r["lighting_types"],*[pmap[p]["title"] for p in r["patterns"]]])
        pattern_links="".join(f'<li><a href="#pattern-{p}">{p} {esc(pmap[p]["title"])}</a></li>' for p in r["patterns"])
        palette="".join(f'<span style="background:{p["hex"]}" title="{p["hex"]} · {p["fraction"]:.1%}"></span>' for p in r["metrics"]["palette"])
        similar="、".join(x["id"] for x in r["similar_frames"])
        scope_label={"scene":"공간 참고","detail":"재질·조명 상세","effect":"연출 효과","state_variant":"상태 비교","pre_release":"개발 중 자료"}[r["scope"]]
        cards.append(f'''<article class="card" id="{r['id']}" data-id="{r['id']}" data-game="{r['game']}" data-region="{esc(r['region'])}" data-layout="{esc(r['layout'])}" data-scope="{r['scope']}" data-materials="{esc(';'.join(r['materials']))}" data-lights="{esc(';'.join(r['lighting_types']))}" data-targets="{esc(';'.join(r['project_targets']))}" data-patterns="{';'.join(r['patterns'])}" data-search="{esc(haystack)}"><a class="picture" href="{esc(r['local_file'])}" data-large><img loading="lazy" src="{esc(r['local_file'])}" alt="{esc(r['id']+' '+r['title'])}" width="{r['width']}" height="{r['height']}"></a><div class="body"><div class="eyebrow">{r['id']} · {r['game']} / {esc(r['region'])}</div><h3>{esc(r['title'])}</h3><p class="meta">{esc(r['layout'])} · {scope_label} · {esc(', '.join(r['materials']))}</p><dl><dt>화면 관찰</dt><dd>{esc(r['observation'])}</dd><dt>전경과 배경</dt><dd>{esc(r['depth_interpretation'])}</dd><dt>조명</dt><dd>{esc(r['lighting'])}</dd><dt>프로젝트 적용 패턴</dt><dd><ul>{pattern_links}</ul></dd><dt>적용할 구역</dt><dd>{esc(', '.join(r['project_targets']))}</dd></dl><details><summary>색상 수치와 출처 정보</summary><div class="palette">{palette}</div><p class="meta">암부 {r['metrics']['dark_pixel_fraction']:.1%} · 밝은 픽셀 {r['metrics']['bright_pixel_fraction']:.1%}. UI를 포함한 화면 전체의 계산값이며 재질별 팔레트나 원작 렌더 설정이 아니다.</p><p class="meta">유사 구도 후보: {similar or '없음'} · {r['width']}×{r['height']} · 2026-11-23 확인</p><p class="meta">자산 명세: {', '.join(r['asset_briefs'])}</p></details><footer><a href="{esc(r['source_page'])}" target="_blank" rel="noopener">출처 ↗</a><a href="{esc(r['image_url'])}" target="_blank" rel="noopener">제공 이미지 ↗</a><label class="compare-label"><input type="checkbox" data-compare="{r['id']}">비교 담기</label></footer></div></article>''')
    pattern_cards=[]
    for p in pats:
        example=" ".join(f'<a href="#{rid}">{rid}</a>' for rid in p["reference_ids"][:10])
        pattern_cards.append(f'''<details class="pattern" id="pattern-{p['id']}"><summary>{p['id']} {esc(p['title'])} <small>{p['priority']}</small></summary><p>{esc(p['action'])}</p><p><b>적용 구역</b> {esc(', '.join(p['targets']))}</p><p><b>제약</b> {esc(p['constraint'])}</p><p><b>검수</b> {esc(p['acceptance'])}</p><p class="meta">{esc(p['project_status'])}</p><p class="examples">{example}</p><button data-filter-pattern="{p['id']}">이 패턴의 참고 {len(p['reference_ids'])}장 보기</button></details>''')
    def options(values):return ''.join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in sorted(values))
    selectors=[("game","게임",options({r['game'] for r in rows})),("region","지역",options({r['region'] for r in rows})),
               ("layout","공간 용도",options({r['layout'] for r in rows})),("target","프로젝트 구역",options({v for r in rows for v in r['project_targets']})),
               ("material","재질",options({v for r in rows for v in r['materials']})),("light","조명",options({v for r in rows for v in r['lighting_types']})),
               ("pattern","제작 패턴",''.join(f'<option value="{p["id"]}">{p["id"]} {esc(p["title"])}</option>' for p in pats)),
               ("scope","자료 종류",''.join(f'<option value="{v}">{k}</option>' for v,k in [("scene","공간 참고"),("detail","재질·조명 상세"),("effect","연출 효과"),("state_variant","상태 비교"),("pre_release","개발 중 자료")]))]
    controls=''.join(f'<label>{label}<select id="{key}"><option value="">전체</option>{opts}</select></label>' for key,label,opts in selectors)
    doc='''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>RelicEscape 맵 제작 참고 데이터</title><style>
:root{color-scheme:dark;--bg:#0b171e;--panel:#14262e;--line:#35505a;--txt:#e3ede9;--muted:#abc1c8;--accent:#afe6bc}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:16px/1.75 'Malgun Gothic',sans-serif}a{color:var(--accent);text-underline-offset:4px}header,main{max-width:1540px;margin:auto;padding:32px}h1{font-size:clamp(30px,4vw,50px);line-height:1.3;margin:12px 0 24px}h2{font-size:27px;margin:32px 0 20px}h3{font-size:21px;line-height:1.4;margin:8px 0}.lead{max-width:1100px;font-size:19px;color:#c8dde0}.eyebrow{font-size:13px;color:var(--accent)}.stats,.nav{display:flex;gap:14px;flex-wrap:wrap}.stats span{padding:8px 14px;border:1px solid var(--line);border-radius:24px}.nav{margin-top:24px}.note{padding:16px 20px;background:#18313a;border-left:3px solid var(--accent);max-width:1200px}.muted,.meta{font-size:13px;color:var(--muted)}.filter-box{background:#10232c;border:1px solid var(--line);padding:18px;border-radius:10px}.filters{display:flex;flex-wrap:wrap;gap:12px;align-items:end}label{display:flex;flex-direction:column;font-size:13px;color:var(--muted)}input,select,button{font:inherit;color:var(--txt);background:#1a333e;border:1px solid #4a6b76;padding:9px 12px;border-radius:6px}select{max-width:255px}#search{width:clamp(250px,40vw,560px)}button{cursor:pointer}.pagination{display:flex;gap:12px;align-items:center;justify-content:center;margin:22px 0}.pagination button:disabled{opacity:.4;cursor:default}#count{font-size:14px;color:var(--muted);margin:14px 0}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden;scroll-margin-top:24px}.card[hidden]{display:none}.picture{display:block;background:#02070b}.picture img{display:block;width:100%;height:auto;aspect-ratio:16/9;object-fit:contain}.body{padding:20px}dt{color:var(--accent);font-size:13px;font-weight:bold;margin-top:14px}dd{margin:4px 0;line-height:1.75;font-size:15px}ul{padding-left:18px;margin:4px 0}footer{display:flex;gap:15px;flex-wrap:wrap;align-items:center;font-size:13px;border-top:1px solid var(--line);padding-top:14px;margin-top:18px}.compare-label{flex-direction:row;gap:6px;align-items:center}.palette{display:flex;height:28px;margin-top:12px}.palette span{flex:1}summary{cursor:pointer}details summary{color:#c8ddd0;font-size:14px}.patterns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.pattern{background:var(--panel);padding:18px;border:1px solid var(--line);border-radius:8px;scroll-margin-top:20px}.pattern summary{font-size:17px}.pattern small{margin-left:10px;color:var(--muted)}.examples{display:flex;flex-wrap:wrap;gap:12px;font-size:13px}.plate-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.plate-grid img{width:100%;height:auto}.selection{position:sticky;bottom:12px;z-index:8;margin-top:24px;padding:14px;background:#25483ff2;border:1px solid #70b29d;border-radius:10px;display:flex;gap:16px;align-items:center;flex-wrap:wrap}.selection[hidden]{display:none}dialog{border:1px solid #557e8c;background:#08151d;color:var(--txt);padding:20px;max-width:96vw;max-height:94vh;width:1400px}dialog::backdrop{background:#000e}.dialog-close{float:right;margin-bottom:12px}.large-image{display:block;max-width:90vw;max-height:80vh;margin:auto;object-fit:contain}.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:24px;clear:both}.compare-grid img{width:100%;height:auto}.swatches{display:flex;margin:12px 0}.swatches span{height:30px;flex:1}.empty{padding:32px;color:var(--muted)}@media(max-width:1080px){.grid,.plate-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:700px){header,main{padding:20px}.grid,.patterns,.plate-grid,.compare-grid{grid-template-columns:1fr}.filters select{max-width:90vw}#search{width:100%}.selection{position:static}}
</style><header><div class="eyebrow">RELICESCAPE · 맵 제작용 참고 데이터 · 2026년 11월 23일</div><h1>할로우 나이트와 실크송<br>맵을 만드는 형태와 빛</h1><p class="lead">사진을 모으는 데서 끝내지 않고, 우리 맵에서 쓸 공간 구조·재질·전경·배경·조명을 제작 패턴과 자산 명세로 연결한다. 관찰한 화면과 프로젝트 적용 제안은 구분한다.</p><div class="stats"><span>TOTAL장</span><span>이번에 NEW장 추가</span><span>할로우 나이트 HKCOUNT장</span><span>실크송 SSCOUNT장</span><span>REGIONCOUNT개 지역</span><span>제작 패턴20개 · 자산 명세20개</span></div><nav class="nav"><a href="#catalog">이미지 검색</a><a href="#patterns">제작 패턴</a><a href="#plates">대표 영역 주석</a><a href="../../reference-production-guide.md">프로젝트 제작 가이드</a><a href="README.md">전체 목록</a><a href="analysis.json">분석 JSON</a><a href="analysis.jsonl">JSONL</a><a href="catalog.csv">CSV</a><a href="asset-briefs.json">자산 명세</a></nav><p class="note">신규 자료는 실제 PNG로 보관하고 기존45장은 원래 파일을 참조한다. 파일·RGB 픽셀 중복을 제외했으며 비슷한 구도는 별도 표시한다. 이미지 수는 서로 다른 방의 수가 아니다. 이미지 권리는 Team Cherry 및 해당 권리자에게 있고, 게임에 직접 넣는 자산은 별도로 제작한다.</p></header><main><section id="catalog"><h2>만들 구역부터 고르는 이미지 검색</h2><div class="filter-box"><div class="filters"><label>키워드<input id="search" type="search" placeholder="예: 천장빛, 가시, 폐아치, 유물, SS-DD-05"></label><button id="reset">필터 초기화</button></div><div class="filters" style="margin-top:16px">CONTROLS</div><p class="muted">P0는 시야·기능 판독 우선, P1은 공간·재질 제작, P2는 후속 변주다. 원작의 난도나 구현 완료 등급을 뜻하지 않는다.</p></div><p id="count" aria-live="polite"></p><div class="pagination"><button id="prev-top">이전</button><span id="page-top"></span><button id="next-top">다음</button></div><div class="grid">CARDS</div><p class="empty" id="empty" hidden>조건에 맞는 자료가 없습니다.</p><div class="pagination"><button id="prev">이전</button><span id="page"></span><button id="next">다음</button></div><div class="selection" id="selection" hidden><span id="selected-label"></span><button id="compare-open">두 이미지 비교</button><button id="clear-selection">비우기</button></div></section><section id="patterns"><h2>프로젝트 적용 패턴과 검수 기준</h2><div class="patterns">PATTERNS</div></section><section id="plates"><h2>대표 이미지의 전경 배경과 빛</h2><p>박스는 관찰할 영역을 가리킨다. 실제 엔진 레이어나 충돌 마스크를 추출한 결과가 아니다.</p><div class="plate-grid">PLATES</div></section><p class="note">수치 팔레트와 암부 비율은 UI를 포함한 전체 이미지에서 계산했다. 재질별 색상·실제 충돌·시차 속도·광원 합성·효과 시간·적 능력은 정지 이미지에서 확정하지 않는다. 시작 동굴·최초 착지방 보존, 현재 발판·벽·충돌·전투 규칙은 프로젝트 제작 가이드의 유지 조건을 따른다.</p></main><dialog id="viewer"><button class="dialog-close" data-close>닫기 ×</button><img id="large" class="large-image" alt=""></dialog><dialog id="compare"><button class="dialog-close" data-close>닫기 ×</button><div class="compare-grid" id="compare-content"></div></dialog><script id="records-data" type="application/json">DATAJSON</script><script>
const rows=JSON.parse(document.querySelector('#records-data').textContent),byId=new Map(rows.map(r=>[r.id,r]));const cards=[...document.querySelectorAll('.card')];const keys=['game','region','layout','target','material','light','pattern','scope'];const filters=Object.fromEntries(keys.map(k=>[k,document.getElementById(k)]));const query=document.querySelector('#search');let page=0;const pageSize=24;let matches=[];const selected=new Set();
function includes(c,field,value){return !value||c.dataset[field].split(';').includes(value)}
function apply(){let term=query.value.trim().toLocaleLowerCase();matches=cards.filter(c=>(!term||c.dataset.search.toLocaleLowerCase().includes(term))&&(!filters.game.value||c.dataset.game===filters.game.value)&&(!filters.region.value||c.dataset.region===filters.region.value)&&(!filters.layout.value||c.dataset.layout===filters.layout.value)&&(!filters.scope.value||c.dataset.scope===filters.scope.value)&&includes(c,'targets',filters.target.value)&&includes(c,'materials',filters.material.value)&&includes(c,'lights',filters.light.value)&&includes(c,'patterns',filters.pattern.value));let pages=Math.max(1,Math.ceil(matches.length/pageSize));page=Math.min(page,pages-1);cards.forEach(c=>c.hidden=true);matches.slice(page*pageSize,(page+1)*pageSize).forEach(c=>c.hidden=false);document.querySelector('#count').textContent=matches.length+' / '+cards.length+'장 · 한 페이지24장';['page','page-top'].forEach(id=>document.getElementById(id).textContent=(page+1)+' / '+pages);['prev','prev-top'].forEach(id=>document.getElementById(id).disabled=page===0);['next','next-top'].forEach(id=>document.getElementById(id).disabled=page>=pages-1);document.querySelector('#empty').hidden=matches.length>0}
function reset(){query.value='';Object.values(filters).forEach(f=>f.value='');page=0;apply()}
[query,...Object.values(filters)].forEach(el=>el.addEventListener('input',()=>{page=0;apply()}));document.querySelector('#reset').onclick=reset;['prev','prev-top','next','next-top'].forEach(id=>document.getElementById(id).onclick=()=>{page+=id.startsWith('prev')?-1:1;apply();document.querySelector('#catalog').scrollIntoView()});document.querySelectorAll('[data-filter-pattern]').forEach(b=>b.onclick=()=>{reset();filters.pattern.value=b.dataset.filterPattern;apply();document.querySelector('#catalog').scrollIntoView()});
const viewer=document.querySelector('#viewer'),large=document.querySelector('#large');document.querySelectorAll('[data-large]').forEach(a=>a.addEventListener('click',e=>{if(typeof viewer.showModal!=='function')return;e.preventDefault();large.src=a.getAttribute('href');large.alt=a.querySelector('img')?.alt||'관찰 영역';viewer.showModal()}));document.querySelectorAll('[data-close]').forEach(b=>b.onclick=()=>b.closest('dialog').close());document.querySelectorAll('dialog').forEach(d=>d.addEventListener('click',e=>{if(e.target===d)d.close()}));
function selectionUI(){document.querySelector('#selection').hidden=selected.size===0;document.querySelector('#selected-label').textContent=[...selected].join(' + ');document.querySelector('#compare-open').disabled=selected.size!==2;document.querySelectorAll('[data-compare]').forEach(c=>c.checked=selected.has(c.dataset.compare))}
document.querySelectorAll('[data-compare]').forEach(c=>c.onchange=()=>{let id=c.dataset.compare;if(c.checked){if(selected.size===2)selected.delete(selected.values().next().value);selected.add(id)}else selected.delete(id);selectionUI()});document.querySelector('#clear-selection').onclick=()=>{selected.clear();selectionUI()};document.querySelector('#compare-open').onclick=()=>{const content=document.querySelector('#compare-content');content.replaceChildren();[...selected].forEach(id=>{const r=byId.get(id),section=document.createElement('section'),h=document.createElement('h3'),im=document.createElement('img');h.textContent=id+' '+r.title;im.src=r.local_file;im.alt=r.title;section.append(h,im);for(const [label,value] of [['지역',r.region],['관찰',r.observation],['전경과 배경',r.depth_interpretation],['조명',r.lighting],['적용 구역',r.project_targets.join(', ')],['제작 패턴',r.patterns.join(', ')]]){let p=document.createElement('p');p.textContent=label+': '+value;section.append(p)}let a=document.createElement('a');a.href=r.source_page;a.textContent='출처 페이지';a.target='_blank';a.rel='noopener';section.append(a);content.append(section)});document.querySelector('#compare').showModal()};
function revealHash(){let id=decodeURIComponent(location.hash.slice(1));if(byId.has(id)){reset();let index=cards.findIndex(c=>c.dataset.id===id);page=Math.floor(index/pageSize);apply();document.getElementById(id).scrollIntoView()}else if(id.startsWith('pattern-')){let d=document.getElementById(id);if(d)d.open=true}}
window.addEventListener('hashchange',revealHash);apply();revealHash();
</script></html>'''
    plate_files=sorted((ROOT/"analysis").glob("*-annotated.jpg"))
    plates=''.join(f'<a href="analysis/{p.name}" data-large><img loading="lazy" src="analysis/{p.name}" alt="{esc(p.stem)}"></a>' for p in plate_files)
    slim=[{k:r[k] for k in ['id','title','region','local_file','source_page','observation','depth_interpretation','lighting','project_targets','patterns']} for r in rows]
    replacements={"TOTAL":str(stats['total']),"NEW":str(stats['new']),"HKCOUNT":str(stats['games']['HK']),"SSCOUNT":str(stats['games']['SS']),"REGIONCOUNT":str(stats['regions']),
                  "CONTROLS":controls,"CARDS":"".join(cards),"PATTERNS":"".join(pattern_cards),"PLATES":plates,"DATAJSON":json.dumps(slim,ensure_ascii=False).replace("</","<\\/")}
    for key,value in replacements.items():doc=doc.replace(key,value)
    (ROOT/"index.html").write_text(doc,encoding="utf-8")


def main():
    rows=load_records();pats,briefs,stats=write_exports(rows);write_readme(rows,pats,briefs,stats);write_gallery(rows,pats,briefs,stats)
    print(json.dumps({k:stats[k] for k in ('total','new','legacy','games','regions','patterns','asset_briefs')},ensure_ascii=True))


if __name__=="__main__":main()
