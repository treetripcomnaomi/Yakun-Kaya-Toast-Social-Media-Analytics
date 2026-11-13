"""11/2 小红书合并：旧的 9 次搜索（主文件夹 xhs_*_general/latest.csv）+ 组员补抓 12 次（Rednotes_keywords 文件夹）。
相关性规则沿用 xhs_clean.py；原始 CSV 不改。输出 cleaned_data/xhs_notes_merged_1102.csv。"""
import os, re, glob, pandas as pd
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
NEW = os.path.expanduser("~/mnt/Rednotes_keywords")
old = sorted(glob.glob(os.path.join(ROOT, "xhs_*_general.csv")) + glob.glob(os.path.join(ROOT, "xhs_*_latest.csv")))
new = sorted(glob.glob(os.path.join(NEW, "*.csv")))
cols = ["id","keyword","sortSource","title","desc","type","timestamp","author/userid",
        "engagement/liked_count","engagement/collected_count","engagement/comments_count","engagement/shared_count","url"]
def rd(f, batch):
    x = pd.read_csv(f, usecols=lambda c: c in cols, dtype={"id": str, "author/userid": str}); x["batch"] = batch; return x
raw = pd.concat([rd(f, "旧（10/29）") for f in old] + [rd(f, "补抓（11/1）") for f in new], ignore_index=True)
raw["sort"] = raw.sortSource.map({"general": "综合", "time_descending": "最新", "popularity_descending": "最热"}).fillna(raw.sortSource)
raw["src"] = raw.keyword + "（" + raw["sort"] + "）"
agg = {c: "first" for c in raw.columns if c not in ("id", "src", "batch")}
agg["src"] = lambda s: "; ".join(dict.fromkeys(s)); agg["batch"] = lambda s: "; ".join(dict.fromkeys(s))
d = raw.groupby("id", as_index=False).agg(agg)
BRAND = re.compile(r"ya ?kun|亚坤|亞坤|雅坤", re.I)
CAT = re.compile(r"咖椰|加椰|kaya|吐司|土司|国民早餐|國民早餐|豆浆咖啡|豆奶咖啡|早餐|早午餐|brunch|kopi", re.I)
text = (d.title.fillna("") + " " + d.desc.fillna("")).str.strip()
brand_q = d.src.str.contains("亚坤|亞坤")
rel = ["yakun_text" if BRAND.search(t) else "possible_yakun" if (q and CAT.search(t)) else "category" if not q else "irrelevant"
       for t, q in zip(text, brand_q)]
OVERRIDE = {"6acdb00f000000001b0225ff": "yakun_inferred", "6ad645f00000000027014a34": "yakun_inferred",
            "6adf38d4000000001601ad72": "category", "6ae07880000000001a0135d8": "irrelevant", "6ae06f29000000001902791e": "irrelevant"}
d["relevance"] = [OVERRIDE.get(i, r) for i, r in zip(d.id, rel)]
d["text"] = text
d["published_date"] = pd.to_datetime(d.timestamp, unit="s").dt.strftime("%Y-%m-%d")
eng = [pd.to_numeric(d[c], errors="coerce").fillna(0) for c in cols[8:12]]
d["engagement"] = sum(eng)
d.rename(columns={"id": "note_id", "src": "search_terms"}).drop(columns=["keyword","sortSource","sort"]).to_csv(
    os.path.join(ROOT, "cleaned_data", "xhs_notes_merged_1102.csv"), index=False, encoding="utf-8-sig")
print("原始行", len(raw), "（旧", sum(raw.batch.str.startswith("旧")), "补抓", sum(raw.batch.str.startswith("补")), "）去重后", len(d))
print(d.relevance.value_counts().to_dict())
y = d[d.relevance.isin(["yakun_text", "yakun_inferred"])]
print("Ya Kun 相关", len(y), "其中只在补抓里出现", sum(y.batch == "补抓（11/1）"), "；只在旧数据", sum(y.batch == "旧（10/29）"), "；两边都有", sum(y.batch.str.contains(";")))
