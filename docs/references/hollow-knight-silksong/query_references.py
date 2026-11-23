"""Query the local project reference database without a browser or network."""
import argparse
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser(description="프로젝트용 맵 이미지 자료 검색")
    parser.add_argument("--game",choices=["HK","SS"])
    parser.add_argument("--region")
    parser.add_argument("--target")
    parser.add_argument("--pattern")
    parser.add_argument("--material")
    parser.add_argument("--light")
    parser.add_argument("--scope",choices=["scene","detail","effect","state_variant","pre_release"])
    parser.add_argument("--query",default="")
    parser.add_argument("--limit",type=int,default=10)
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    root=Path(__file__).resolve().parent
    rows=json.loads((root/"analysis.json").read_text(encoding="utf-8"))
    matches=[]
    for r in rows:
        if args.game and r["game"]!=args.game:continue
        if args.region and args.region.casefold() not in r["region"].casefold():continue
        if args.scope and r["scope"]!=args.scope:continue
        if any(value and value not in r[field] for value,field in [(args.target,"project_targets"),(args.pattern,"patterns"),(args.material,"materials"),(args.light,"lighting_types")]):continue
        haystack=" ".join([r["id"],r["region"],r["title"],r["observation"],r["depth_interpretation"],r["lighting"],*r["project_targets"],*r["materials"]])
        if args.query.casefold() not in haystack.casefold():continue
        matches.append(r)
    limited=matches[:max(0,args.limit)]
    if args.json:
        print(json.dumps(dict(total=len(matches),results=limited),ensure_ascii=True,indent=2))
    else:
        print(f"{len(matches)} matches; showing {len(limited)}")
        for r in limited:
            print(r["id"]+" | "+r["region"]+" | "+r["title"])
            print("  "+r["observation"])
            print("  patterns="+",".join(r["patterns"])+"; briefs="+",".join(r["asset_briefs"]))
            print("  "+str((root/r["local_file"]).resolve()))


if __name__=="__main__":main()
