"""M6 小红书笔记清洗：合并 9 次 Apify 搜索结果（xhs_*_general.csv / xhs_*_latest.csv），去重、判相关性、加线索列。
输出 cleaned_data/xhs_notes_clean.csv。注意：正文只有工具给的前约 60 字（text_truncated=True），没有 IP 属地；
人工补录后（full_text / ip_location 列）重跑本脚本即可合并。之后运行 add_translations.py 加英文列。
"""
import os, re, glob, hashlib, warnings, pandas as pd
warnings.filterwarnings("ignore")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "cleaned_data", "xhs_notes_clean.csv")
SCRAPE_DATE = pd.Timestamp("2026-10-29")

files = sorted(glob.glob(os.path.join(ROOT, "xhs_*_general.csv")) + glob.glob(os.path.join(ROOT, "xhs_*_latest.csv")))
cols = ["id", "keyword", "sortSource", "title", "desc", "type", "timestamp", "author/userid", "author/nickname",
        "engagement/liked_count", "engagement/collected_count", "engagement/comments_count", "engagement/shared_count", "url"]
raw = pd.concat([pd.read_csv(f, usecols=lambda c: c in cols, dtype={"id": str, "author/userid": str}) for f in files], ignore_index=True)
n_raw = len(raw)
raw["sort"] = raw.sortSource.map({"general": "综合", "time_descending": "最新"}).fillna(raw.sortSource)
raw["src"] = raw.keyword + "（" + raw["sort"] + "）"
agg = {c: "first" for c in raw.columns if c not in ("id", "src")}
agg["src"] = lambda s: "; ".join(dict.fromkeys(s))
d = raw.groupby("id", as_index=False).agg(agg)

BRAND = re.compile(r"ya ?kun|亚坤|亞坤|雅坤", re.I)
NOISE = re.compile(r"蔡徐坤|ikun|\bkun\b(?!.*亚坤)", re.I)
CAT = re.compile(r"咖椰|加椰|kaya|吐司|土司|国民早餐|國民早餐|豆浆咖啡|豆奶咖啡|早餐|早午餐|brunch|kopi", re.I)
TOURIST = re.compile(r"第一次|首次|打卡|攻略|旅游|旅遊|旅行|必吃|必试|必試|游客|遊客|自由行|落地|中转|中轉|转机|機場|机场|樟宜|day ?\d|几天|幾天|\d天\d?晚?|来新加坡|來新加坡|去新加坡|回国|回國|国内|國內|免签|行程|酒店|人民币|rmb|first time|must[- ]?try", re.I)
LOCAL = re.compile(r"本地人|新加坡人|在新加坡生活|在新加坡工作|来新加坡\d+年|來新加坡\d+年|新加坡\d+年|读研|讀研|留学|留學|每天上班|小时候|小時候|从小|從小|日常|上班|NUS|NTU", re.I)
SOYA = re.compile(r"豆浆|豆漿|豆奶|豆乳|soy|soya", re.I)
COMP = re.compile(r"土司工坊|toast ?box|老曾记|老曾記|old chang kee|arabica|喜园|killiney|基里尼|真美珍|chin mee chin|东亚|東亞|tong ah|翠华|翠華|heap seng", re.I)
PRICE = re.compile(r"\$\s?\d|新币|新幣|sgd|rmb|人民币|元|块|塊|贵|貴|便宜|价格|價格|价钱|划算|性价比|性價比|物价|平价|平價", re.I)
PROMO = re.compile(r"优惠|優惠|折扣|打折|买一送一|買一送一|抽奖|抽獎|免费|免費|券|会员|會員|新品|限定", re.I)
DATED = re.compile(r"老一套|过时|過時|老土|没变|沒變|一般般|吃了就那样|不过如此", re.I)
AESTH = re.compile(r"出片|好拍|拍照|氛围|氛圍|颜值|顏值|复古|復古|ins风|好看", re.I)
COPY = re.compile(r"复刻|復刻|自制|自製|在家做|教程|配方|豆浆粉|豆漿粉|咖椰酱|咖椰醬", re.I)
SWEET = re.compile(r"甜|齁|腻|膩", re.I)
DISCLOSE = re.compile(r"品牌合作|合作|赞助|贊助|广告|廣告|#ad\b|探店邀请|邀请", re.I)

text = (d.title.fillna("") + " " + d.desc.fillna("")).str.strip()
brand_q = d.src.str.contains("亚坤")
rel = []
for t, q in zip(text, brand_q):
    if BRAND.search(t): rel.append("yakun_text")
    elif q and CAT.search(t): rel.append("possible_yakun")      # 品牌词搜出、没写"亚坤"但讲早餐/kaya，需人工确认
    elif not q: rel.append("category")                          # 品类词（新加坡早餐、咖椰吐司）搜出的全部算品类内容，用作占比分母
    else: rel.append("irrelevant")
# 人工判读（Claude 按预览判断，2026-10-30）：没写"亚坤"但套餐 A $6.3 + 豆浆咖啡 + "国民早餐"，几乎肯定是 Ya Kun
OVERRIDE = {"6acdb00f000000001b0225ff": "yakun_inferred", "6ad645f00000000027014a34": "yakun_inferred",
            "6adf38d4000000001601ad72": "category",      # 机场海南宝的咖椰吐司，不是 Ya Kun
            "6ae07880000000001a0135d8": "irrelevant",   # 马来西亚华阳伴手礼
            "6ae06f29000000001902791e": "irrelevant"}   # 奶茶店招聘广告
rel = [OVERRIDE.get(i, r) for i, r in zip(d.id, rel)]
dt = pd.to_datetime(d.timestamp, unit="s")
likes, coll, com, sh = [pd.to_numeric(d[c], errors="coerce") for c in
                        ["engagement/liked_count", "engagement/collected_count", "engagement/comments_count", "engagement/shared_count"]]
out = pd.DataFrame({
    "note_id": d.id, "url": d.url, "relevance": rel, "search_terms": d.src,
    "published_date": dt.dt.strftime("%Y-%m-%d"), "recent_7d": (SCRAPE_DATE - dt).dt.days < 7,
    "author_anon": d["author/userid"].astype(str).apply(lambda s: "x_" + hashlib.sha1(("yakun5342|" + s).encode()).hexdigest()[:8]),
    "format": d.type.map({"normal": "image", "video": "video"}).fillna(d.type),
    "title": d.title, "preview": d.desc, "text": text, "text_truncated": True,
    "likes": likes, "collects": coll, "comments": com, "shares": sh,
    "engagement": likes.fillna(0) + coll.fillna(0) + com.fillna(0) + sh.fillna(0),
    "full_text": "", "ip_location": "", "author_followers": float("nan"), "brand_collab_label": "",
})
# 合并人工补录（如有）：xhs_filled_*.xlsx 里的完整正文、IP 属地、品牌合作标识
for f in glob.glob(os.path.join(ROOT, "xhs_filled_*.xlsx")):
    m = pd.read_excel(f, dtype={"note_id": str})
    m = m.rename(columns={"【补】完整正文": "full_text", "【补】IP属地": "ip_location", "【补】作者粉丝数": "author_followers", "【补】品牌合作标识（是/否）": "brand_collab_label"})
    for c in ["full_text", "ip_location", "author_followers", "brand_collab_label"]:
        if c in m:
            v = m.set_index("note_id")[c].dropna().astype(str)
            out[c] = out.note_id.map(v).fillna(out[c])
has_full = out.full_text.astype(str).str.len() > 0
out.loc[has_full, "text"] = (out.title.fillna("") + " " + out.full_text).str.strip()
out.loc[has_full, "text_truncated"] = False
out["ip_non_sg"] = out.ip_location.astype(str).str.len().gt(0) & ~out.ip_location.astype(str).str.contains("新加坡")
for name, rx in [("tourist_cue", TOURIST), ("local_cue", LOCAL), ("soya_coffee", SOYA), ("competitor", COMP), ("price_mention", PRICE),
                 ("promo_mention", PROMO), ("dated_cue", DATED), ("aesthetic_cue", AESTH), ("recreate_at_home", COPY),
                 ("too_sweet", SWEET), ("text_disclosure", DISCLOSE)]:
    out[name] = out.text.fillna("").str.contains(rx)
out["lang"] = "zh"
n_irr = int((out.relevance == "irrelevant").sum())
out = out[out.relevance != "irrelevant"]          # 无关笔记（蔡徐坤、房产、招聘等）不进清洗文件；原始 CSV 里仍保留
print(f"剔除无关 {n_irr} 篇")
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"原始 {n_raw} 行（{len(files)} 个文件）→ 去重 {len(out)} 篇")
print("相关性", out.relevance.value_counts().to_dict())
y = out[out.relevance.isin(["yakun_text", "yakun_inferred"])]
print("Ya Kun 笔记线索", {k: int(y[k].sum()) for k in ["tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "promo_mention", "dated_cue", "aesthetic_cue", "recreate_at_home", "too_sweet", "text_disclosure", "recent_7d"]})
print("已补完整正文", int(has_full.sum()), "；已补 IP", int((out.ip_location.astype(str).str.len() > 0).sum()))
