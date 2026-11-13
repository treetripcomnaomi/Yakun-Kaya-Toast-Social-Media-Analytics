"""M5 TikTok UGC 清洗：tiktok_ugc_brand.csv + tiktok_ugc_topics.csv → tiktok_ugc_clean.csv（原始文件不改）
相关度：yakun_text（文案/标签提到 Ya Kun 且有食物语境）/ category（kaya、kopi、豆浆咖啡、新加坡传统早餐）/ 其余剔除。
TikTok 搜索会按字幕、画面模糊匹配，文案不提 Ya Kun 的结果几乎都是噪音（撞名、Adidas 鞋、蔡徐坤等），按 off_topic 剔除。
"""
import hashlib, os, re, warnings
import pandas as pd
warnings.filterwarnings("ignore")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRAPE = pd.Timestamp("2026-10-25", tz="UTC")
b = pd.read_csv(os.path.join(D, "tiktok_ugc_brand.csv"), low_memory=False); b["run"] = "brand"
t = pd.read_csv(os.path.join(D, "tiktok_ugc_topics.csv"), low_memory=False); t["run"] = "topics"
d = pd.concat([b, t], ignore_index=True).copy()
n_raw = len(d)
d["query"] = d.searchQuery.where(d.searchQuery.notna(), "#" + d["searchHashtag/name"].astype(str))
d["hashtags"] = d.filter(regex=r"^hashtags/\d+/name$").fillna("").astype(str).agg(lambda r: "; ".join(x for x in r if x), axis=1)
d["text"] = d.text.fillna("").astype(str)
d["all"] = d.text + " " + d.hashtags.str.replace(";", " ")
q = d.groupby("id")["query"].agg(lambda s: "; ".join(dict.fromkeys(s)))       # 一条视频被多个词搜到：合并搜索词
d = d.drop_duplicates("id").copy(); d["query"] = d.id.map(q); n_uniq = len(d)

BRAND = re.compile(r"ya ?kun|亚坤|亞坤", re.I)
NOISE = re.compile(r"yacon|yacón|faya ?kun|kun ?faya|liyakun|亚坤(西刀)?鱼丸|ယာကွန်", re.I)
FOOD = re.compile(r"kaya|toast|kopi|coffee|egg|singapor|\bsg\b|breakfast|outlet|cafe|café|\bteh\b|food|bread|roti|soya|toastwich|cookie|mooncake|吐司|咖椰|咖啡|早餐|新加坡|面包|麵包|ขนมปัง|สังขยา", re.I)
KAYA = re.compile(r"kaya|咖椰|加椰|สังขยา", re.I)
SOYAKOPI = re.compile(r"kopi ?soya|soya ?kopi|teh ?soya|soya ?teh|kopi ?c? ?soy", re.I)
TRAD = re.compile(r"kopi|kopitiam|soft[- ]?boil|half[- ]?boil|hawker|traditional breakfast|local breakfast|breakfast set|toast", re.I)
SG = re.compile(r"singapor|\bsg\b|🇸🇬|新加坡|#sgfood|#sgeats", re.I)
OFFICIAL = {"yakunkayatoastsg", "yakuncambodia", "yakunmyanmar", "yakunthailand", "yakun_indonesia", "toastboxsingapore",
            "oldchangkeesingapore", "arabicasg"}
def relevance(r):
    s = r["all"]
    if BRAND.search(re.sub(NOISE, " ", s)) and FOOD.search(s): return "yakun_text"
    if KAYA.search(s) or SOYAKOPI.search(s) or (re.search(r"soya|soy ?(?:milk|latte|coffee)|豆浆|豆奶", s, re.I) and SG.search(s)) or (TRAD.search(s) and SG.search(s)) or (SG.search(s) and re.search(r"breakfast|早餐", s, re.I)):
        return "category"
    return "off_topic"
d["relevance"] = d.apply(relevance, axis=1)
drop = d[d.relevance == "off_topic"]; d = d[d.relevance != "off_topic"].copy()

TOURIST = re.compile(r"first time|1st time|first visit|visit(?:ing|ed)? singapore|trip to singapore|in singapore for|travel|tourist|holiday|vacation|must[- ]?(?:try|eat|visit|have)|bucket list|layover|itinerary|next time (?:i|we)|days? in singapore|singapore (?:vlog|travel|guide|trip)|#sgtravel|打卡|攻略|旅游|旅遊|旅行|第一次|必吃|必試|必试|游客|遊客|自由行", re.I)
LOCAL = re.compile(r"\blah\b|\bleh\b|\bsia\b|\bshiok\b|\bdabao\b|\bkosong\b|kopitiam|grew up|growing up|childhood|since young|since (?:i was )?(?:a )?kid|my (?:grand(?:pa|ma|father|mother)|ah ?ma|ah ?gong)|every morning|old days|memories|nostalgi|as a singaporean|小时候|小時候|从小|從小|本地人|新加坡人", re.I)
SOYA = re.compile(r"soya|soy ?(?:milk|latte|coffee)|豆浆|豆奶|豆漿", re.I)
COMP = re.compile(r"toast ?box|old chang kee|arabica|killiney|chin mee chin|tong ah|heap seng leong|土司工坊|老曾记|老曾記", re.I)
PRICE = re.compile(r"\$\s?\d|\bprice|pricey|expensive|cheap|afford|worth|overpriced|value for money|贵|貴|便宜|价格|價格|划算", re.I)
PROMO = re.compile(r"giveaway|contest|\bwin\b|voucher|promo|discount|\bfree\b|\bapp\b|redeem|1-for-1|1 for 1|% ?off|\bdeal", re.I)
DATED = re.compile(r"old[- ]fashioned|outdated|boring|uncle|auntie|老一套|过时|過時|not the same|used to be", re.I)
AESTH = re.compile(r"aesthetic|instagrammable|photo ?spot|pretty|cute|vibe|#cafehopping|cafe ?hop|打卡|出片|好拍", re.I)
DISCLOSE = re.compile(r"#ad\b|#sponsored|#paidpartnership|paid partnership|#collab|in collaboration with|#partner|#gifted|\bgifted\b|invited by|#invite", re.I)
GEO = {1880251: "SG", 1643084: "ID", 1605651: "TH", 1694008: "PH", 1733045: "MY", 6252001: "US", 1831722: "KH", 2077456: "AU",
       1562822: "VN", 1861060: "JP", 1835841: "KR", 1814991: "CN", 1668284: "TW", 2635167: "GB", 1819730: "HK", 1327865: "MM",
       1269750: "IN", 6251999: "CA", 2750405: "NL", 3017382: "FR", 2921044: "DE", 3996063: "MX", 2186224: "NZ"}
num = lambda s: pd.to_numeric(s, errors="coerce")
fans = num(d["authorMeta/fans"]); pub = pd.to_datetime(d.createTimeISO, utc=True)
out = pd.DataFrame({
    "video_id": d.id.astype(str), "url": d.webVideoUrl, "relevance": d.relevance, "run": d.run, "query": d["query"],
    "published_date": pub.dt.strftime("%Y-%m-%d"), "recent_7d": pub > SCRAPE - pd.Timedelta(days=7),
    "author_anon": d["authorMeta/name"].astype(str).apply(lambda s: "u_" + hashlib.sha1(("yakun5342|" + s).encode()).hexdigest()[:8]),
    "author_public": d["authorMeta/name"].where(d["authorMeta/verified"].fillna(False).astype(bool) | (fans >= 10_000) | d["authorMeta/name"].isin(OFFICIAL), ""),
    "is_official_or_franchise": d["authorMeta/name"].isin(OFFICIAL),
    "author_fans": fans,
    "creator_tier": pd.cut(fans, [-1, 9_999, 99_999, 999_999, float("inf")], labels=["nano(<10k)", "micro(10k-100k)", "mid(100k-1M)", "macro(1M+)"]).astype(str).replace("nan", ""),
    "author_verified": d["authorMeta/verified"].fillna(False).astype(bool),
    "text": d.text.str.replace(r"@[\w.\-]+", "@user", regex=True), "hashtags": d.hashtags, "lang": d.textLanguage,
    "location_country": num(d["locationMeta/countryCode"]).map(GEO).fillna(d["locationMeta/countryCode"].astype(str).replace("nan", "")),
    "location_name": d["locationMeta/locationName"].fillna(""),
    "format": d.isSlideshow.map({True: "slideshow", False: "video"}).fillna("video"), "duration_sec": num(d["videoMeta/duration"]),
    "views": num(d.playCount), "likes": num(d.diggCount), "comments": num(d.commentCount), "shares": num(d.shareCount), "saves": num(d.collectCount),
    "subtitle_available": d["videoMeta/subtitleLinks/0/downloadLink"].notna(),
    "platform_disclosure": d.isAd.fillna(False).astype(bool) | d.isSponsored.fillna(False).astype(bool),
})
out["engagement"] = out[["likes", "comments", "shares", "saves"]].fillna(0).sum(axis=1)        # TikTok 口径
out["eng_per_view"] = (out.engagement / out.views).where(out.views > 0).round(4)
a = d["all"].values
for name, rx in [("tourist_cue", TOURIST), ("local_cue", LOCAL), ("soya_coffee", SOYA), ("competitor", COMP), ("price_mention", PRICE),
                 ("promo_mention", PROMO), ("dated_cue", DATED), ("aesthetic_cue", AESTH), ("text_disclosure", DISCLOSE)]:
    out[name] = [bool(rx.search(s)) for s in a]
out["commercial_disclosure"] = out.platform_disclosure | out.text_disclosure
out["collab_query"] = out["query"].str.contains("adidas|uniqlo|sg60")
out = out.sort_values(["relevance", "views"], ascending=[False, False])
out.to_csv(os.path.join(D, "cleaned_data", "tiktok_ugc_clean.csv"), index=False, encoding="utf-8-sig")

print(f"原始 {n_raw} → 去重 {n_uniq}（同一视频被多个词搜到 {n_raw - n_uniq}）→ 保留 {len(out)}，剔除 off_topic {len(drop)}")
print(out.relevance.value_counts().to_string())
print("其中品牌/加盟商官方账号", int(out.is_official_or_franchise.sum()), "；7 天内", int(out.recent_7d.sum()), "；有字幕链接", int(out.subtitle_available.sum()))
print("按搜索词保留率：")
qq = pd.concat([d[["id", "query"]].assign(kept=True), drop[["id", "query"]].assign(kept=False)])
qq = qq.assign(query=qq["query"].str.split("; ")).explode("query")
print(qq.groupby("query").kept.agg(["size", "sum"]).rename(columns={"size": "videos", "sum": "kept"}).to_string())
print("地点", out.location_country.replace("", "未标").value_counts().head(8).to_dict())
print("语言", out.lang.value_counts().head(8).to_dict())
print("线索", {k: int(out[k].sum()) for k in ["tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "promo_mention", "dated_cue", "aesthetic_cue", "commercial_disclosure"]})
print("创作者", out.creator_tier.value_counts().to_dict())
print("剔除样例：", drop.text.str.replace("\n", " ").str[:60].sample(12, random_state=3).tolist())
