"""合并总表 master_table.csv + Step 1/5 指标（按老师口径） step1_step5_metrics.csv"""
import pandas as pd, numpy as np, sys, os
C = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
rd = lambda f, **k: pd.read_csv(os.path.join(C, f), low_memory=False, **k)
P = rd("official_posts_clean.csv", dtype={"post_id": str})
CO = rd("comments_official_clean.csv", dtype={"comment_id": str, "post_id": str})
U = rd("tiktok_ugc_clean.csv", dtype={"video_id": str})
YV = rd("youtube_videos_clean.csv", dtype={"video_id": str})
YC = rd("comments_youtube_clean.csv", dtype={"comment_id": str, "video_id": str})
B = rd("brand24_cleaned.csv", dtype={"id": str})
X = rd("xhs_notes_clean.csv", dtype={"note_id": str}) if os.path.exists(os.path.join(C, "xhs_notes_clean.csv")) else None
rows = []
def add(df, **cols):
    d = pd.DataFrame({k: (df[v] if isinstance(v, str) and v in df else v) for k, v in cols.items()})
    rows.append(d)
add(P, dataset="M2/M3 official posts", content_type="official_post", platform="platform", brand="brand", item_id="post_id", parent_id="",
    published_date="published_date", author_type="brand", yakun_related=(P.brand == "Ya Kun"), industry=False,
    text_en="text_en", translated="translated", lang="caption_lang", likes="likes", comments="comments", shares="shares", saves="saves",
    views="views", engagement="engagement", url="url")
add(CO, dataset="M4 official-post comments", content_type="comment", platform="platform", brand="brand", item_id="comment_id", parent_id="post_id",
    published_date="published_date", author_type=np.where(CO.is_brand_account, "brand", np.where(CO.suspected_bot, "suspected_bot", "user")),
    yakun_related=(CO.brand == "Ya Kun"), industry=False, text_en="text_en", translated="translated", lang="lang", likes="likes",
    comments="replies", url="post_url")
add(U, dataset="M5 TikTok UGC", content_type="ugc_video", platform="TikTok", brand="", item_id="video_id", parent_id="", published_date="published_date",
    author_type=np.where(U.is_official_or_franchise, "brand_or_franchise", np.where(U.author_fans >= 10000, "creator", "user")),
    yakun_related=(U.relevance == "yakun_text"), industry=(U.relevance == "category"), text_en="text_en", translated="translated", lang="lang",
    likes="likes", comments="comments", shares="shares", saves="saves", views="views", engagement="engagement", url="url",
    location_country="location_country", author_fans="author_fans", tourist_cue="tourist_cue")
add(YV, dataset="M11 YouTube videos", content_type="ugc_video", platform="YouTube", brand="", item_id="video_id", parent_id="", published_date="published_date",
    author_type=np.where(YV.channel_subscribers >= 10000, "creator", "user"), yakun_related=(YV.relevance != "category"), industry=(YV.relevance == "category"),
    text_en="text_en", translated="translated", lang="lang", likes="likes", comments="comments", views="views", engagement="engagement", url="url",
    location_country="channel_country", author_fans="channel_subscribers", tourist_cue="tourist_cue")
add(YC, dataset="M11 YouTube comments", content_type="comment", platform="YouTube", brand="", item_id="comment_id", parent_id="video_id",
    published_date="published_date", author_type="user", yakun_related=(YC.video_relevance != "category") | YC.mentions_yakun,
    industry=(YC.video_relevance == "category") & ~YC.mentions_yakun, text_en="text_en", translated="translated", lang="lang",
    likes="likes", comments="replies", tourist_cue="tourist_cue")
B["text_en"] = B.text
add(B, dataset="M7 Brand24", content_type="brand24_mention", platform="platform", brand="", item_id="id", parent_id="", published_date="date",
    author_type="source_type", yakun_related=True, industry=False, text_en="text_en", translated=False, lang="lang", url="url",
    brand24_sentiment="brand24_sentiment")
if X is not None:
    fans = X.author_followers if "author_followers" in X else pd.Series(np.nan, index=X.index)
    add(X, dataset="M6 Xiaohongshu notes", content_type="ugc_note", platform="Xiaohongshu", brand="", item_id="note_id", parent_id="",
        published_date="published_date", author_type=np.where(fans >= 10000, "creator", "user"), yakun_related=X.relevance.isin(["yakun_text", "yakun_inferred"]),
        industry=X.relevance.isin(["category", "possible_yakun"]), text_en="text_en", translated="translated", lang="lang", likes="likes", comments="comments",
        shares="shares", saves="collects", engagement="engagement", url="url", location_country="ip_location", author_fans="author_followers",
        tourist_cue="tourist_cue")
M = pd.concat(rows, ignore_index=True)
M.insert(0, "uid", M.dataset.str.extract(r"^(M\d+(?:/M\d+)?)")[0].str.replace("/", "") + "_" + M.item_id.astype(str))
M.to_csv(os.path.join(OUT, "master_table.csv"), index=False, encoding="utf-8-sig")
print("master_table", M.shape); print(M.groupby(["dataset", "yakun_related"]).size().to_string())

# ---- Step 1 / Step 5 指标（老师口径）----
W0, W1 = pd.Timestamp("2026-04-25"), pd.Timestamp("2026-10-18")      # 最近 6 个月，剔除 7 天内
days = (W1 - W0).days + 1
PO = rd("platform_overview_clean.csv")
fol = PO.set_index(["brand", "platform"]).followers.to_dict()
fol.update({("Ya Kun", "TikTok"): 225, ("Toast Box", "TikTok"): 361, ("Old Chang Kee", "TikTok"): 6064, ("% Arabica", "TikTok"): 83})  # 抓取的 TikTok 粉丝
TOTAL = {("Ya Kun","Instagram"):867, ("Toast Box","Instagram"):1692, ("Old Chang Kee","Instagram"):2579, ("% Arabica","Instagram"):np.nan,
         ("Ya Kun","TikTok"):31, ("Toast Box","TikTok"):138, ("Old Chang Kee","TikTok"):193, ("% Arabica","TikTok"):85}
P["d"] = pd.to_datetime(P.published_date)
out = []
for (b, pf), g in P.groupby(["brand", "platform"]):
    w = g[(g.d >= W0) & (g.d <= W1)]
    e = w.engagement.dropna()
    f = fol.get((b, pf), np.nan)
    out.append({"brand": b, "platform": pf, "followers": f, "total_posts_all_time": TOTAL.get((b, pf)),
                "posts_in_period": len(w), "period_days": days, "avg_posts_per_day": round(len(w) / days, 3),
                "avg_posts_per_week": round(len(w) / days * 7, 2),
                "avg_engagement_per_post": round(e.mean(), 1) if len(e) else np.nan, "median_engagement_per_post": e.median() if len(e) else np.nan,
                "avg_likes_per_post": round(w.likes.mean(), 1) if len(w) else np.nan, "avg_comments_per_post": round(w.comments.mean(), 1) if len(w) else np.nan,
                "avg_shares_per_post": round(w.shares.mean(), 1) if pf == "TikTok" and len(w) else np.nan,
                "avg_saves_per_post": round(w.saves.mean(), 1) if pf == "TikTok" and len(w) else np.nan,
                "avg_views_per_post": round(w.views.mean(), 0) if len(w) else np.nan,
                "engagement_rate_per_post": round(e.mean() / f, 5) if len(e) and f else np.nan,            # 每帖平均互动 ÷ 粉丝
                "total_engagement_in_period": e.sum(), "engagement_rate_period_total": round(e.sum() / f, 4) if f else np.nan,  # Canvas 模板口径
                "posts_with_hidden_likes": int(w.likes_hidden.sum()) if "likes_hidden" in w else 0})
S = pd.DataFrame(out)
# Ya Kun TikTok 活跃期（2024-07 至 2025-03）另算一组
g = P[(P.brand == "Ya Kun") & (P.platform == "TikTok")]
a0, a1 = g.d.min(), g.d.max(); ad = (a1 - a0).days + 1; e = g.engagement.dropna()
S = pd.concat([S, pd.DataFrame([{"brand": "Ya Kun", "platform": f"TikTok (active period {a0.date()}–{a1.date()})", "followers": 225, "total_posts_all_time": 31,
     "posts_in_period": len(g), "period_days": ad, "avg_posts_per_day": round(len(g)/ad, 3), "avg_posts_per_week": round(len(g)/ad*7, 2),
     "avg_engagement_per_post": round(e.mean(), 1), "median_engagement_per_post": e.median(), "avg_likes_per_post": round(g.likes.mean(),1),
     "avg_comments_per_post": round(g.comments.mean(),1), "avg_shares_per_post": round(g.shares.mean(),1), "avg_saves_per_post": round(g.saves.mean(),1),
     "avg_views_per_post": round(g.views.mean(),0), "engagement_rate_per_post": round(e.mean()/225, 5), "total_engagement_in_period": e.sum(),
     "engagement_rate_period_total": round(e.sum()/225, 4)}])], ignore_index=True)
S.to_csv(os.path.join(OUT, "step1_step5_metrics.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(S[["brand","platform","followers","total_posts_all_time","posts_in_period","avg_posts_per_day","avg_engagement_per_post","median_engagement_per_post","engagement_rate_per_post","engagement_rate_period_total"]].to_string(index=False))
