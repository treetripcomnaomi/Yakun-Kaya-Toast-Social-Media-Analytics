"""M11 YouTube 清洗：youtube_videos.csv / comments_youtube.csv → *_clean.csv（原始文件不改）
用法：python3 youtube_clean.py   （需要 pandas、langdetect）
"""
import hashlib, os, re, unicodedata
from datetime import timedelta
import pandas as pd
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
v = pd.read_csv(os.path.join(D, "youtube_videos.csv"), dtype=str, encoding="utf-8-sig").fillna("")
c = pd.read_csv(os.path.join(D, "comments_youtube.csv"), dtype=str, encoding="utf-8-sig").fillna("")

BRAND = re.compile(r"ya ?kun|亚坤|亞坤", re.I)
NOISE = re.compile(r"yacon|ubi ?yak[ou]n|faya ?kun|kun ?faya|liyakun|kutilmagan|sardor|shoxruz|亚坤(西刀)?鱼丸|亞坤(西刀)?魚丸", re.I)
KAYA = re.compile(r"kaya|咖椰|加椰", re.I)
TRAD = re.compile(r"kopi|kopitiam|soft[- ]?boil|half[- ]?boil|hawker|traditional breakfast|local breakfast|heritage breakfast|breakfast set|coffee ?shop|toast|soya coffee|kopi soya", re.I)
SG = re.compile(r"singapor|\bsg\b|🇸🇬|新加坡", re.I)
HOTEL = re.compile(r"buffet|shangri|swiss[oô]tel|pan pacific|hotel|platinum", re.I)
TOURIST = re.compile(r"first time|1st time|first visit|visit(ing|ed)? singapore|trip to singapore|in singapore for|travel|tourist|holiday|vacation|must[- ]?(try|eat|visit|have)|bucket list|layover|itinerary|when (i|we) (was|were) in singapore|next time (i|we)|days? in singapore|singapore (vlog|travel|guide)|打卡|攻略|旅游|旅遊|旅行|第一次|必吃|必試|必试|游客|遊客|自由行", re.I)
LOCAL = re.compile(r"\blah\b|\bleh\b|\bsia\b|\bshiok\b|kopitiam|grew up|growing up|childhood|since young|since (i was )?(a )?kid|my (grand(pa|ma|father|mother)|ah ?ma|ah ?gong)|every morning|as a singaporean|we singaporeans|小时候|小時候|从小|從小|本地人|新加坡人", re.I)
SOYA = re.compile(r"soya|soy ?(milk|latte|coffee)|豆浆|豆奶|豆漿", re.I)
COMP = re.compile(r"toast ?box|old chang kee|arabica|killiney|chin mee chin|tong ah|heap seng leong|土司工坊|老曾记|老曾記", re.I)
PRICE = re.compile(r"\$\s?\d|\bprice|pricey|expensive|cheap|afford|worth|overpriced|value for money|贵|貴|便宜|价格|價格|划算", re.I)
def flag(rx, s): return rx.search(s) is not None
def brand(s): return flag(BRAND, s) and not flag(NOISE, s)
def anon(prefix, s): return prefix + hashlib.sha1(("yakun5342|" + s).encode()).hexdigest()[:8] if s else ""
def lang(s):
    s = re.sub(r"https?://\S+|#\S+|@\S+", " ", s)
    if sum(ch.isalpha() for ch in s) < 3: return "unknown"
    try: return detect(s)
    except Exception: return "unknown"

# ---------- 视频 ----------
v["text_all"] = v.title + " " + v.description + " " + v.tags
def relevance(r):
    t, ti = r.text_all, r.title
    if flag(NOISE, t) and not brand(re.sub(NOISE, " ", t)): return "noise"
    if brand(ti): return "yakun_title"
    if brand(t): return "yakun_mention"
    if flag(KAYA, t) or (flag(TRAD, t) and flag(SG, t)) or (flag(SG, t) and re.search(r"breakfast|早餐", t, re.I) and not flag(HOTEL, ti)):
        return "category"
    return "off_topic"
v["relevance"] = v.apply(relevance, axis=1)
n_raw = len(v); drop_v = v[v.relevance.isin(["noise", "off_topic"])]
v = v[~v.relevance.isin(["noise", "off_topic"])].copy()

def dur(s):
    m = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1))) if m else None
num = lambda s: pd.to_numeric(s, errors="coerce")
v["duration_sec"] = v.duration.apply(dur)
v["is_short"] = (v.duration_sec <= 60) | v.text_all.str.contains("#shorts", case=False)
v["views"], v["likes"], v["comments"], v["channel_subscribers"] = num(v.views), num(v.likes), num(v.comments), num(v.channel_subscribers)
v["engagement"] = v.likes.fillna(0) + v.comments.fillna(0)          # YouTube 口径：点赞 + 评论
v["eng_per_view"] = (v.engagement / v.views).where(v.views > 0).round(4)
v["creator_tier"] = pd.cut(v.channel_subscribers, [-1, 9_999, 99_999, 999_999, float("inf")],
                           labels=["nano(<10k)", "micro(10k-100k)", "mid(100k-1M)", "macro(1M+)"]).astype(str).replace("nan", "")
v["lang"] = v.language.str.split("-").str[0].str.lower()
v.loc[v.lang == "", "lang"] = v.loc[v.lang == "", "title"].apply(lang)
v["non_sg_channel"] = (v.channel_country != "") & (v.channel_country != "SG")
pub = pd.to_datetime(v.published_at, utc=True); cut = pd.to_datetime(v.retrieved_at.iloc[0], utc=True) - timedelta(days=7)
v["recent_7d"] = pub > cut                                           # 互动数还在涨：不进互动率分析
v["published_date"] = pub.dt.strftime("%Y-%m-%d")
for name, rx in [("tourist_cue", TOURIST), ("local_cue", LOCAL), ("soya_coffee", SOYA), ("competitor", COMP), ("price_mention", PRICE)]:
    v[name] = v.text_all.apply(lambda s: flag(rx, s))
v["channel_anon"] = v.channel_id.apply(lambda s: anon("ch_", s))
vcols = ["video_id", "url", "relevance", "search_terms", "published_date", "recent_7d", "channel_title", "channel_anon",
         "channel_country", "non_sg_channel", "channel_subscribers", "creator_tier", "title", "description", "tags", "lang",
         "duration_sec", "is_short", "views", "likes", "comments", "engagement", "eng_per_view",
         "tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "retrieved_at"]
v[vcols].sort_values(["relevance", "views"], ascending=[False, False]).to_csv(os.path.join(D, "cleaned_data", "youtube_videos_clean.csv"), index=False, encoding="utf-8-sig")

# ---------- 评论 ----------
n_c = len(c)
c = c[c.video_id.isin(v.video_id)].copy(); n_c_kept_video = len(c)
c["text"] = c.text.str.replace(r"\s+", " ", regex=True).str.strip()
has_word = c.text.apply(lambda s: any(unicodedata.category(ch)[0] in "LN" for ch in s))
spam = c.text.str.contains(r"https?://|www\.", case=False) & c.text.str.contains(r"subscri|my channel|check (?:out )?my|whatsapp|telegram|crypto|invest|earn", case=False)
n_emoji, n_spam = (~has_word).sum(), (spam & has_word).sum()
c = c[has_word & ~spam]
n_before_dup = len(c); c = c.drop_duplicates(["author", "text"]); n_dup = n_before_dup - len(c)
c["author_anon"] = c.author.apply(lambda s: anon("u_", s))
c["text"] = c.text.str.replace(r"@[\w.\-]+", "@user", regex=True)   # 去掉文中 @ 的用户名
c["lang"] = c.text.apply(lang)
c["n_words"] = c.text.apply(lambda s: len(re.findall(r"[A-Za-z']+", s)) + len(re.findall(r"[一-鿿]", s)) // 2)
c["low_content"] = c.n_words < 3
c["mentions_yakun"] = c.text.apply(brand)
for name, rx in [("tourist_cue", TOURIST), ("local_cue", LOCAL), ("soya_coffee", SOYA), ("competitor", COMP), ("price_mention", PRICE)]:
    c[name] = c.text.apply(lambda s: flag(rx, s))
c = c.merge(v[["video_id", "relevance", "channel_country", "recent_7d"]].rename(columns={
    "relevance": "video_relevance", "channel_country": "video_channel_country", "recent_7d": "video_recent_7d"}), on="video_id")
c["published_date"] = pd.to_datetime(c.published_at, utc=True).dt.strftime("%Y-%m-%d")
ccols = ["video_id", "video_relevance", "video_channel_country", "video_recent_7d", "comment_id", "published_date", "author_anon",
         "text", "lang", "n_words", "low_content", "likes", "replies", "mentions_yakun",
         "tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention", "retrieved_at"]
c[ccols].to_csv(os.path.join(D, "cleaned_data", "comments_youtube_clean.csv"), index=False, encoding="utf-8-sig")

# ---------- 汇总 ----------
print(f"视频：原始 {n_raw} → 保留 {len(v)}（剔除 noise {sum(drop_v.relevance=='noise')}、off_topic {sum(drop_v.relevance=='off_topic')}）")
print(v.relevance.value_counts().to_string())
print(f"7 天内新视频（不进互动分析）：{v.recent_7d.sum()}；Shorts：{v.is_short.sum()}；非新加坡频道：{v.non_sg_channel.sum()}；国家未填：{(v.channel_country=='').sum()}")
print("视频线索：", {k: int(v[k].sum()) for k in ["tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention"]})
print(f"评论：原始 {n_c} → 属于保留视频 {n_c_kept_video} → 去纯表情 {n_emoji}、垃圾 {n_spam}、重复 {n_dup} → 保留 {len(c)}")
print(c.video_relevance.value_counts().to_string())
print("评论线索：", {k: int(c[k].sum()) for k in ["mentions_yakun", "low_content", "tourist_cue", "local_cue", "soya_coffee", "competitor", "price_mention"]})
print("评论语言：", c.lang.value_counts().head(8).to_dict())
print("剔除的视频标题样例：")
for _, r in drop_v.head(60).iterrows(): print(" ", r.relevance, "|", r.title[:70])
