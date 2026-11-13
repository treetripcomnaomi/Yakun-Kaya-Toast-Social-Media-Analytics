"""M2 IG 官方帖 + M3 TikTok 官方视频 → official_posts_clean.csv、official_summary.csv（原始文件不改）
规则（见主文档「统一规则」）：窗口 2024-07-01 至抓取日（2026-10-25）；抓取日前 7 天内的帖子标 recent_7d（不进互动分析）；
最近 6 个月（last_6m）用于 Step 1、5 的发帖频率和互动率；IG 互动 = 点赞+评论；TikTok 互动 = 点赞+评论+分享+收藏。
"""
import os, re, warnings
warnings.filterwarnings("ignore")
import pandas as pd
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SCRAPE = pd.Timestamp("2026-10-25", tz="UTC")
START, CUT7, SIX = pd.Timestamp("2024-07-01", tz="UTC"), SCRAPE - pd.Timedelta(days=7), SCRAPE - pd.DateOffset(months=6)
BRAND = {"yakunkayatoastsg": "Ya Kun", "toastboxsg": "Toast Box", "toastboxsingapore": "Toast Box",
         "oldchangkeesingapore": "Old Chang Kee", "arabicasg": "% Arabica"}
DISCLOSE = re.compile(r"#ad\b|#sponsored|#paidpartnership|paid partnership|#collab|in collaboration with|#partner", re.I)
PROMO = re.compile(r"giveaway|contest|\bwin\b|winner|promo|% ?off|\bdeal|freebie|\bfree\b|voucher|1-for-1|1 for 1|discount|redeem|\bapp\b|rewards?", re.I)
ADIDAS, UNIQLO, FULLERTON, SG60 = (re.compile(x, re.I) for x in [r"adidas", r"uniqlo", r"fullerton", r"sg ?60"])
SOYA = re.compile(r"soya|soy ?(?:milk|latte|coffee)|豆浆|豆奶|豆漿", re.I)
num = lambda s: pd.to_numeric(s, errors="coerce")
def lang(s):
    s = re.sub(r"https?://\S+|#\S+|@\S+", " ", str(s))
    if sum(ch.isalpha() for ch in s) < 3: return "unknown"
    try: return detect(s)
    except Exception: return "unknown"
def hashtags(r, pref):
    cols = [c for c in r.index if re.fullmatch(pref + r"/\d+(/name)?", c)]
    return "; ".join(str(r[c]) for c in cols if pd.notna(r[c]))

# ---------- IG ----------
ig = pd.read_csv(os.path.join(D, "ig_official.csv"), low_memory=False)
ig["account"] = ig.inputUrl.str.extract(r"instagram\.com/([^/]+)/")[0]
co = [c for c in ig.columns if re.fullmatch(r"coauthorProducers/\d+/username", c)]
ig["coauthors"] = ig[co].apply(lambda r: "; ".join(r.dropna().astype(str)), axis=1)
likes = num(ig.likesCount)
I = pd.DataFrame({
    "platform": "Instagram", "brand": ig.account.map(BRAND), "account": ig.account, "post_id": ig.id.astype(str),
    "url": ig.url, "published": pd.to_datetime(ig.timestamp, utc=True),
    "format": ig.type.map({"Video": "reel_video", "Image": "image", "Sidecar": "carousel"}),
    "caption": ig.caption.fillna(""), "hashtags": ig.apply(lambda r: hashtags(r, "hashtags"), axis=1),
    "post_owner": ig.ownerUsername, "coauthors": ig.coauthors,
    "is_coauthor_post": (ig.ownerUsername != ig.account) | (ig.coauthors != ""),
    "likes": likes.where(likes >= 0), "likes_hidden": likes < 0, "comments": num(ig.commentsCount),
    "shares": pd.NA, "saves": pd.NA, "views": num(ig.videoPlayCount).fillna(num(ig.videoViewCount)),
    "duration_sec": num(ig.videoDuration), "followers": pd.NA,                         # 下面用 M1 平台审计补
    "platform_disclosure": ig.paidPartnership.fillna(False).astype(bool),
})
M1 = pd.read_csv(os.path.join(D, "cleaned_data", "platform_overview_clean.csv"))                   # M1 平台审计（2026-10-24 手工记录）
I["followers"] = I.brand.map(M1[M1.platform == "Instagram"].set_index("brand").followers)
I["engagement"] = I.likes.fillna(0) + I.comments.fillna(0)
I.loc[I.likes_hidden, "engagement"] = pd.NA                                          # 点赞被隐藏：不算互动

# ---------- TikTok ----------
tt = pd.concat([pd.read_csv(os.path.join(D, f), low_memory=False) for f in ["tiktok_official_yakun.csv", "tiktok_official_competitors.csv"]], ignore_index=True)
T = pd.DataFrame({
    "platform": "TikTok", "brand": tt.input.map(BRAND), "account": tt.input, "post_id": tt.id.astype(str),
    "url": tt.webVideoUrl, "published": pd.to_datetime(tt.createTimeISO, utc=True),
    "format": tt.isSlideshow.map({True: "slideshow", False: "video"}).fillna("video"),
    "caption": tt.text.fillna(""), "hashtags": tt.apply(lambda r: hashtags(r, "hashtags"), axis=1),
    "post_owner": tt["authorMeta/name"], "coauthors": "", "is_coauthor_post": False,
    "likes": num(tt.diggCount), "likes_hidden": False, "comments": num(tt.commentCount),
    "shares": num(tt.shareCount), "saves": num(tt.collectCount), "views": num(tt.playCount),
    "duration_sec": num(tt["videoMeta/duration"]), "followers": num(tt["authorMeta/fans"]),
    "platform_disclosure": tt.isAd.fillna(False).astype(bool) | tt.isSponsored.fillna(False).astype(bool),
})
T["engagement"] = T[["likes", "comments", "shares", "saves"]].fillna(0).sum(axis=1)

# ---------- 合并、筛窗口、加标记 ----------
P = pd.concat([I, T], ignore_index=True)
n_raw = P.groupby(["platform", "brand"]).size()
raw_min = P.groupby(["platform", "brand"]).published.min()
for c in ["likes","comments","shares","saves","views","duration_sec","followers","engagement"]:
    P[c] = pd.to_numeric(P[c], errors="coerce")
P = P.drop_duplicates(["platform", "post_id"])
P = P[(P.published >= START) & (P.published <= SCRAPE + pd.Timedelta(days=1))].copy()
P["published_date"] = P.published.dt.strftime("%Y-%m-%d")
P["recent_7d"] = P.published > CUT7
P["last_6m"] = (P.published >= SIX) & ~P.recent_7d
P["use_for_engagement"] = ~P.recent_7d & P.engagement.notna()
P["eng_per_view"] = (P.engagement / P.views).where(P.views > 0).round(4)
P["eng_rate_followers"] = (P.engagement / P.followers).where(P.followers > 0).round(4)
text = P.caption + " " + P.hashtags + " " + P.coauthors
P["text_disclosure"] = text.str.contains(DISCLOSE)
P["commercial_disclosure"] = P.platform_disclosure | P.text_disclosure
P["collab_adidas"] = text.str.contains(ADIDAS)
P["collab_uniqlo"] = text.str.contains(UNIQLO)
P["collab_fullerton"] = text.str.contains(FULLERTON)
P["sg60"] = text.str.contains(SG60)
P["promo_cue"] = text.str.contains(PROMO)
P["soya_coffee"] = text.str.contains(SOYA)
P["caption_lang"] = P.caption.apply(lang)
P["caption_words"] = P.caption.str.split().str.len().fillna(0).astype(int)
cols = ["platform", "brand", "account", "post_id", "url", "published_date", "recent_7d", "last_6m", "use_for_engagement",
        "format", "duration_sec", "caption", "hashtags", "caption_lang", "caption_words", "post_owner", "coauthors", "is_coauthor_post",
        "likes", "likes_hidden", "comments", "shares", "saves", "views", "engagement", "eng_per_view", "followers", "eng_rate_followers",
        "platform_disclosure", "text_disclosure", "commercial_disclosure", "collab_adidas", "collab_uniqlo", "collab_fullerton", "sg60", "promo_cue", "soya_coffee"]
P = P.sort_values(["platform", "brand", "published_date"], ascending=[True, True, False])
P[cols].to_csv(os.path.join(D, "cleaned_data", "official_posts_clean.csv"), index=False, encoding="utf-8-sig")

# ---------- 汇总表（Step 1、5 用）----------
rows = []
for (pf, b), g in P.groupby(["platform", "brand"]):
    s6 = g[g.last_6m]; e = g[g.use_for_engagement]; e6 = s6[s6.use_for_engagement]
    rows.append({"platform": pf, "brand": b, "raw_rows": int(n_raw.get((pf, b), 0)), "posts_in_window": len(g),
                 "earliest_post_scraped": g.published_date.min(), "latest_post": g.published_date.max(),
                 "window_complete": bool(raw_min[(pf, b)] <= START + pd.Timedelta(days=31)),  # 抓取是否回溯到窗口起点
                 "posts_last_6m": len(s6), "posts_per_week_last_6m": round(len(s6) / 26, 2),
                 "median_eng_last_6m": e6.engagement.median(), "mean_eng_last_6m": round(e6.engagement.mean(), 1) if len(e6) else None,
                 "median_eng_per_view_last_6m": e6.eng_per_view.median(), "followers": g.followers.max(),
                 "median_eng_rate_followers_last_6m": e6.eng_rate_followers.median(),
                 "share_reels_or_video": round((g.format.isin(["reel_video", "video"])).mean(), 2),
                 "share_coauthor": round(g.is_coauthor_post.mean(), 2), "share_disclosed": round(g.commercial_disclosure.mean(), 2),
                 "share_promo_cue": round(g.promo_cue.mean(), 2), "n_likes_hidden": int(g.likes_hidden.sum()), "n_recent_7d": int(g.recent_7d.sum())})
S = pd.DataFrame(rows)
S.to_csv(os.path.join(D, "cleaned_data", "official_summary.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(S.drop(columns=["raw_rows"]).to_string(index=False))
print("\n合计", len(P), "条；Ya Kun 联名帖：adidas", int(P.collab_adidas[P.brand == "Ya Kun"].sum()), "/ uniqlo", int(P.collab_uniqlo[P.brand == "Ya Kun"].sum()), "/ fullerton", int(P.collab_fullerton[P.brand == "Ya Kun"].sum()), "/ sg60", int(P.sg60[P.brand == "Ya Kun"].sum()),
      "；豆浆咖啡帖", int(P.soya_coffee[P.brand == "Ya Kun"].sum()))
print("窗口外剔除：", (n_raw - P.groupby(["platform", "brand"]).size()).to_dict())
