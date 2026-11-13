"""M4 官方帖评论清洗：comments_ig.csv + ig_official.csv 内嵌评论 + comments_tiktok.csv → comments_official_clean.csv（原始文件不改）
先运行 official_clean.py（要用 official_posts_clean.csv 判断帖子是否在窗口内）。
"""
import hashlib, os, re, unicodedata, warnings
import pandas as pd
from langdetect import detect, DetectorFactory
warnings.filterwarnings("ignore"); DetectorFactory.seed = 0
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = pd.read_csv(os.path.join(D, "cleaned_data", "official_posts_clean.csv"), dtype={"post_id": str})
P["key"] = P.url.str.extract(r"/(?:p|reel|video)/([^/?]+)")[0]
BRAND_ACC = {"yakunkayatoastsg", "toastboxsg", "toastboxsingapore", "oldchangkeesingapore", "arabicasg"}
BRAND = re.compile(r"ya ?kun|亚坤|亞坤", re.I)
TOURIST = re.compile(r"first time|1st time|first visit|visit(?:ing|ed)? singapore|trip to singapore|travel|tourist|holiday|vacation|must[- ]?(?:try|eat|visit|have)|bucket list|layover|itinerary|next time (?:i|we)|打卡|攻略|旅游|旅遊|旅行|第一次|必吃|游客|遊客", re.I)
LOCAL = re.compile(r"\blah\b|\bleh\b|\bsia\b|\bshiok\b|\bdabao\b|\bkosong\b|kopitiam|grew up|growing up|childhood|since young|since (?:i was )?(?:a )?kid|my (?:grand(?:pa|ma|father|mother)|ah ?ma|ah ?gong)|last time|old days|memories|小时候|小時候|从小|從小|以前", re.I)
SOYA = re.compile(r"soya|soy ?(?:milk|latte|coffee)|豆浆|豆奶|豆漿", re.I)
COMP = re.compile(r"toast ?box|old chang kee|arabica|killiney|chin mee chin|tong ah|土司工坊|老曾记|老曾記", re.I)
PRICE = re.compile(r"\$\s?\d|\bprice|pricey|expensive|cheap|afford|worth|overpriced|over priced|value for money|贵|貴|便宜|价格|價格|划算", re.I)
PROMO = re.compile(r"giveaway|contest|\bwin\b|voucher|promo|discount|\bfree\b|points|\bapp\b|redeem|1-for-1", re.I)
DATED = re.compile(r"old[- ]fashioned|outdated|boring|uncle|auntie|老一套|过时|過時|no more the old|not the same|used to be", re.I)
def anon(s): return "u_" + hashlib.sha1(("yakun5342|" + str(s)).encode()).hexdigest()[:8] if pd.notna(s) and s != "" else ""
def lang(s):
    s = re.sub(r"https?://\S+|#\S+|@\S+", " ", s)
    if sum(ch.isalpha() for ch in s) < 3: return "unknown"
    try: return detect(s)
    except Exception: return "unknown"

ig = pd.read_csv(os.path.join(D, "comments_ig.csv"), low_memory=False)
n_ig_raw, n_ig_err = len(ig), ig.error.notna().sum()
ig = ig[ig.error.isna()]
I = pd.DataFrame({"platform": "Instagram", "key": ig.postUrl.str.extract(r"/(?:p|reel)/([^/]+)")[0], "comment_id": ig.id.astype(str),
                  "published": ig.timestamp, "author": ig.ownerUsername, "text": ig.text.fillna("").astype(str),
                  "likes": ig.likesCount, "replies": ig.repliesCount})
I["source"] = "M4_comments_scraper"
# M2 官方帖抓取时 Apify 顺带返回的每帖前 15 条评论（ig_official.csv 的 latestComments/N/*）：补充竞品评论
og = pd.read_csv(os.path.join(D, "ig_official.csv"), low_memory=False)
emb = []
for n in range(15):
    pre = f"latestComments/{n}/"
    if pre + "id" not in og: break
    e = og[["shortCode", pre + "id", pre + "timestamp", pre + "ownerUsername", pre + "text", pre + "likesCount", pre + "repliesCount"]].dropna(subset=[pre + "id"])
    e.columns = ["key", "comment_id", "published", "author", "text", "likes", "replies"]
    emb.append(e)
E = pd.concat(emb, ignore_index=True)
E["comment_id"] = pd.to_numeric(E.comment_id, errors="coerce").astype("Int64").astype(str)
E["text"] = E.text.fillna("").astype(str); E["platform"] = "Instagram"; E["source"] = "M2_embedded_latestComments"
n_emb = len(E)
I["comment_id"] = pd.to_numeric(I.comment_id, errors="coerce").astype("Int64").astype(str)
I = pd.concat([I, E], ignore_index=True).drop_duplicates(["platform", "comment_id"], keep="first")   # 两个来源重复的评论只留 M4 那条
tt = pd.read_csv(os.path.join(D, "comments_tiktok.csv"), low_memory=False, dtype={"cid": str})
n_tt_raw = len(tt)
T = pd.DataFrame({"platform": "TikTok", "key": tt.videoWebUrl.str.extract(r"/video/(\d+)")[0], "comment_id": tt.cid,
                  "published": tt.createTimeISO, "author": tt.uniqueId, "text": tt.text.fillna("").astype(str),
                  "likes": tt.diggCount, "replies": tt.replyCommentTotal, "source": "M3_tiktok_comments"})
C = pd.concat([I, T], ignore_index=True)
n_all = len(C)
C = C.merge(P[["platform", "key", "brand", "post_id", "url", "published_date", "recent_7d", "last_6m", "format", "post_owner",
               "is_coauthor_post", "collab_adidas", "collab_uniqlo", "collab_fullerton", "sg60", "promo_cue", "soya_coffee"]]
            .rename(columns={"published_date": "post_date", "recent_7d": "post_recent_7d", "last_6m": "post_last_6m", "format": "post_format",
                             "promo_cue": "post_promo_cue", "soya_coffee": "post_soya_coffee", "url": "post_url"}),
            on=["platform", "key"], how="left")
out_window = C.brand.isna(); n_out = out_window.sum(); n_out_posts = C[out_window].key.nunique()
C = C[~out_window].copy()
C["text"] = C.text.str.replace(r"\s+", " ", regex=True).str.strip()
has_word = C.text.apply(lambda s: any(unicodedata.category(ch)[0] in "LN" for ch in s))
tag_only = C.text.str.fullmatch(r"(?:@[\w.]+[\s,]*)+")
n_emoji, n_tag = (~has_word).sum(), (tag_only & has_word).sum()
C = C[has_word & ~tag_only]
n_b = len(C); C = C.drop_duplicates(["author", "text"]); n_dup = n_b - len(C)     # 同一人在多条帖子贴同一段话，只留一条
C["is_brand_account"] = C.author.isin(BRAND_ACC)
posts_per_author = C.groupby("author").key.transform("nunique")
C["suspected_bot"] = posts_per_author >= 20                                        # 在 ≥20 条帖子下评论（如模板化夸奖账号），编码时复核
C["author_anon"] = C.author.apply(anon)
C["text"] = C.text.str.replace(r"@[\w.\-]+", "@user", regex=True)
C["lang"] = C.text.apply(lang)
C["n_words"] = C.text.apply(lambda s: len(re.findall(r"[A-Za-z']+", s)) + len(re.findall(r"[一-鿿]", s)) // 2)
C["low_content"] = C.n_words < 3
C["published_date"] = pd.to_datetime(C.published, utc=True).dt.strftime("%Y-%m-%d")
for name, rx in [("mentions_yakun", BRAND), ("tourist_cue", TOURIST), ("local_cue", LOCAL), ("soya_coffee", SOYA), ("competitor", COMP),
                 ("price_mention", PRICE), ("promo_mention", PROMO), ("dated_cue", DATED)]:
    C[name] = C.text.str.contains(rx)
cols = ["platform", "brand", "post_id", "post_url", "post_date", "post_recent_7d", "post_last_6m", "post_format", "post_owner", "is_coauthor_post",
        "collab_adidas", "collab_uniqlo", "collab_fullerton", "sg60", "post_promo_cue", "post_soya_coffee",
        "comment_id", "source", "published_date", "author_anon", "is_brand_account", "suspected_bot", "text", "lang", "n_words", "low_content",
        "likes", "replies", "mentions_yakun", "tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "promo_mention", "dated_cue"]
C[cols].sort_values(["platform", "post_date"], ascending=[True, False]).to_csv(os.path.join(D, "cleaned_data", "comments_official_clean.csv"), index=False, encoding="utf-8-sig")
print(f"IG M4 原始 {n_ig_raw}（no_items {n_ig_err}）+ M2 内嵌评论 {n_emb} + TikTok 原始 {n_tt_raw} → 去掉两来源重复后共 {n_all}")
print(f"→ 窗口外/不在官方帖数据里的帖子 {n_out_posts} 条、评论 {n_out} 条剔除")
print(f"→ 纯表情 {n_emoji}、只 @ 朋友 {n_tag}、同人同文重复 {n_dup} 剔除 → 保留 {len(C)}")
print(C.groupby(["platform", "brand", "source"]).agg(comments=("comment_id", "size"), posts=("post_id", "nunique")).to_string())
print("品牌账号回复", int(C.is_brand_account.sum()), "；疑似机器人", int(C.suspected_bot.sum()), "；低内容", int(C.low_content.sum()))
print("线索：", {k: int(C[k].sum()) for k in ["mentions_yakun", "tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "promo_mention", "dated_cue"]})
print("最近6个月帖子的评论", int(C.post_last_6m.sum()), "；联名帖评论 adidas/uniqlo/fullerton/sg60",
      [int(C[k].sum()) for k in ["collab_adidas", "collab_uniqlo", "collab_fullerton", "sg60"]])
print("语言", C.lang.value_counts().head(6).to_dict())
