"""Audit provenance, local images, production links and analytical annotations."""
import csv
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote,urlsplit

from PIL import Image

ROOT=Path(__file__).resolve().parent


class Gallery(HTMLParser):
    def __init__(self):
        super().__init__();self.links=[];self.cards=0;self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="article" and attrs.get("class")=="card":self.cards+=1
        if attrs.get("id"):self.ids.append(attrs["id"])
        for key in ("href","src"):
            if attrs.get(key):self.links.append(attrs[key])


def main():
    rows=json.loads((ROOT/"analysis.json").read_text(encoding="utf-8"))
    pats=json.loads((ROOT/"patterns.json").read_text(encoding="utf-8"))
    briefs=json.loads((ROOT/"asset-briefs.json").read_text(encoding="utf-8"))
    stats=json.loads((ROOT/"statistics.json").read_text(encoding="utf-8"))
    ids={r["id"] for r in rows};pids={p["id"] for p in pats};bids={b["id"] for b in briefs}
    targets=json.loads((ROOT/"project-targets.json").read_text(encoding="utf-8"))
    target_tags={t["tag"] for t in targets["targets"]}
    assert len(target_tags)==len(targets["targets"])
    for key in ("plan","approved_map"):assert (ROOT/targets[key]).exists()
    assert len(ids)==len(rows)==stats["total"]
    assert len({r["sha256"] for r in rows})==len(rows)
    assert len({r["pixel_sha256"] for r in rows})==len(rows)
    assert stats["new"]>=100 and stats["games"]["SS"]>=100
    for r in rows:
        path=ROOT/r["local_file"];data=path.read_bytes()
        assert hashlib.sha256(data).hexdigest()==r["sha256"],r["id"]
        with Image.open(path) as im:
            assert list(im.size)==[r["width"],r["height"]]
            im=im.convert("RGB")
            pixel_hash=hashlib.sha256(im.width.to_bytes(4,"big")+im.height.to_bytes(4,"big")+im.tobytes()).hexdigest()
            assert pixel_hash==r["pixel_sha256"],r["id"]
        assert r["patterns"] and set(r["patterns"])<=pids
        assert r["asset_briefs"] and set(r["asset_briefs"])<=bids
        assert r["project_targets"] and set(r["project_targets"])<=target_tags
        assert r["observation"] and r["lighting"] and r["depth_interpretation"]
        assert r["review"]["status"]=="visual_reviewed"
        for similar in r["similar_frames"]:assert similar["id"] in ids
        assert (ROOT/r["contact_sheet"]).exists()
    for p in pats:
        assert p["reference_ids"] and set(p["reference_ids"])<=ids
        assert set(p["asset_briefs"])<=bids
    for b in briefs:assert b["reference_ids"] and set(b["reference_ids"])<=ids
    annotations=json.loads((ROOT/"annotations.json").read_text(encoding="utf-8"))
    roi_count=0
    for a in annotations:
        assert a["id"] in ids and (ROOT/a["annotated_image"]).exists()
        for region in a["regions"]:
            x1,y1,x2,y2=region["bbox"];assert 0<=x1<x2<=1 and 0<=y1<y2<=1;roi_count+=1
    gallery=Gallery();gallery.feed((ROOT/"index.html").read_text(encoding="utf-8"))
    assert gallery.cards==len(rows)
    assert len(gallery.ids)==len(set(gallery.ids))
    local_links=0
    for link in gallery.links:
        if not urlsplit(link).scheme:
            path,_,anchor=link.partition("#")
            if path:assert (ROOT/unquote(path)).exists(),link;local_links+=1
            elif anchor:assert unquote(anchor) in gallery.ids,link
    for path in (ROOT/"README.md",ROOT.parent.parent/"reference-production-guide.md"):
        for link in re.findall(r"\]\(([^)]+)\)",path.read_text(encoding="utf-8")):
            if not urlsplit(link).scheme and not link.startswith("#"):
                assert (path.parent/unquote(link.split("#")[0])).exists(),str(path)+":"+link
    with (ROOT/"catalog.csv").open(encoding="utf-8-sig",newline="") as f:assert len(list(csv.DictReader(f)))==len(rows)
    jsonl=[json.loads(s) for s in (ROOT/"analysis.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [r["id"] for r in jsonl]==[r["id"] for r in rows]
    print(json.dumps(dict(images=len(rows),new=stats["new"],games=stats["games"],regions=stats["regions"],
        unique_files=len(rows),unique_pixels=len(rows),patterns=len(pats),asset_briefs=len(briefs),
        annotated_images=len(annotations),visual_rois=roi_count,html_cards=gallery.cards,
        local_links_checked=local_links,csv_rows=len(rows),jsonl_rows=len(jsonl)),ensure_ascii=True))


if __name__=="__main__":main()
