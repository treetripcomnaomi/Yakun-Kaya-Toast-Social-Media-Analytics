"""M11 YouTube 用户视频 + 评论（YouTube Data API v3，免费额度）
用法：在 Mac「终端」里运行  python3 youtube_collect.py
运行后按提示粘贴自己的 API key（不会保存到文件，也不要发给别人）。
输出（上一级文件夹）：youtube_videos.csv、comments_youtube.csv、youtube_run_log.txt
额度：每个搜索词约 100 单位，每条视频评论约 1 单位；总共约 1,000 单位，远低于每天 10,000。
中途出错（如额度用完）也会先把已经抓到的数据存下来。
"""
import csv, getpass, json, os, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone

QUERIES = ["ya kun", "ya kun kaya toast", "ya kun soya coffee",
           "kaya toast singapore", "singapore breakfast", "亚坤"]
PER_QUERY = 50          # 每个搜索词取相关度最高的 50 条视频
COMMENTS_PER_VIDEO = 50 # 每条视频取 50 条评论（按相关度）
OUT = os.path.abspath(os.environ.get("YT_OUT") or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
API = os.environ.get("YT_API_BASE", "https://www.googleapis.com/youtube/v3/")
RETRIEVED = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# macOS 自带的 python.org 版本常缺证书：优先用 certifi
try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    CTX = ssl.create_default_context()

class Fatal(Exception):
    pass

units = 0
def get(endpoint, cost=1, **params):
    global units
    params["key"] = KEY
    url = API + endpoint + "?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30, context=CTX) as r:
                units += cost
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            if "commentsDisabled" in body or "videoNotFound" in body or e.code == 404:
                units += cost
                return None
            if "quotaExceeded" in body or "dailyLimitExceeded" in body:
                raise Fatal("今天的 API 额度用完了（quotaExceeded）。已抓到的数据会先保存；明天再跑或换一个 key。")
            if "keyInvalid" in body or "API key not valid" in body:
                raise Fatal("API key 无效：检查是否复制完整（通常以 AIza 开头），并确认已启用 YouTube Data API v3。")
            if "accessNotConfigured" in body or "SERVICE_DISABLED" in body or "has not been used" in body:
                raise Fatal("这个项目还没启用 YouTube Data API v3：在 Google Cloud 控制台 → 库 → 搜 YouTube Data API v3 → 启用，等 1–2 分钟再跑。")
            if attempt == 2:
                raise Fatal(f"API 出错 {e.code}：{body[:300]}")
        except urllib.error.URLError as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e):
                raise Fatal("证书错误：在终端先运行  pip3 install certifi  再重跑；"
                            "或打开 应用程序 → Python 3.x 文件夹 → 双击 Install Certificates.command。")
            if attempt == 2:
                raise Fatal(f"网络错误：{e}（检查是否联网 / VPN）")
        time.sleep(2 * (attempt + 1))

videos, comments, log = [], [], []
def save(status):
    os.makedirs(OUT, exist_ok=True)
    for name, rows in [("youtube_videos.csv", videos), ("comments_youtube.csv", comments)]:
        path = os.path.join(OUT, name)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            if rows:
                w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
        print(f"已保存 {name}：{len(rows)} 行")
    with open(os.path.join(OUT, "youtube_run_log.txt"), "w", encoding="utf-8") as f:
        f.write(f"M11 YouTube 抓取日志\n运行时间(UTC)：{RETRIEVED}\n工具：YouTube Data API v3 + scripts/youtube_collect.py\n"
                f"设置：search type=video order=relevance maxResults={PER_QUERY}；commentThreads order=relevance "
                f"maxResults={COMMENTS_PER_VIDEO}（仅顶层评论）\n搜索词：{'; '.join(QUERIES)}\n")
        f.write("\n".join(log) + "\n")
        f.write(f"视频（去重后）：{len(videos)}；评论：{len(comments)}\n估计消耗额度：约 {units} 单位\n状态：{status}\n")
    print(f"已保存 youtube_run_log.txt（估计消耗约 {units} 单位）")

KEY = os.environ.get("YT_API_KEY") or getpass.getpass("粘贴 YouTube API key（输入时不显示，粘贴后按回车）：").strip()
if not KEY:
    sys.exit("没有输入 key。")

status = "完成"
try:
    # 1. 搜索
    hits = {}
    for q in QUERIES:
        res = get("search", cost=100, part="snippet", q=q, type="video", maxResults=PER_QUERY, order="relevance")
        items = (res or {}).get("items", [])
        for rank, it in enumerate(items, 1):
            vid = it["id"].get("videoId")
            if vid:
                hits.setdefault(vid, []).append(f"{q}#{rank}")
        log.append(f"搜索 {q!r}：{len(items)} 条")
        print(log[-1])

    # 2. 视频详情（每次 50 条）
    ids = list(hits)
    for i in range(0, len(ids), 50):
        res = get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i+50]))
        for v in (res or {}).get("items", []):
            s, st = v["snippet"], v.get("statistics", {})
            videos.append({
                "video_id": v["id"], "url": f"https://www.youtube.com/watch?v={v['id']}",
                "search_terms": "; ".join(hits[v["id"]]),
                "published_at": s["publishedAt"], "channel_id": s["channelId"], "channel_title": s["channelTitle"],
                "title": s["title"], "description": s.get("description", "").replace("\r", " "),
                "tags": "; ".join(s.get("tags", [])), "duration": v.get("contentDetails", {}).get("duration", ""),
                "language": s.get("defaultAudioLanguage") or s.get("defaultLanguage", ""),
                "views": st.get("viewCount", ""), "likes": st.get("likeCount", ""), "comments": st.get("commentCount", ""),
                "retrieved_at": RETRIEVED,
            })
    print(f"视频详情：{len(videos)} 条（去重后）")

    # 3. 频道订阅数（创作者等级用）
    chs = list({v["channel_id"] for v in videos})
    subs = {}
    for i in range(0, len(chs), 50):
        res = get("channels", part="statistics,snippet", id=",".join(chs[i:i+50]))
        for c in (res or {}).get("items", []):
            subs[c["id"]] = (c.get("statistics", {}).get("subscriberCount", ""), c["snippet"].get("country", ""))
    for v in videos:
        v["channel_subscribers"], v["channel_country"] = subs.get(v["channel_id"], ("", ""))

    # 4. 评论（顶层评论，按相关度）
    for n, v in enumerate(videos, 1):
        if v["comments"] in ("", "0"):
            continue
        res = get("commentThreads", part="snippet", videoId=v["video_id"], maxResults=COMMENTS_PER_VIDEO,
                  order="relevance", textFormat="plainText")
        for t in (res or {}).get("items", []):
            c = t["snippet"]["topLevelComment"]["snippet"]
            comments.append({"video_id": v["video_id"], "comment_id": t["id"], "published_at": c["publishedAt"],
                             "author": c.get("authorDisplayName", ""), "text": c.get("textDisplay", "").replace("\r", " "),
                             "likes": c.get("likeCount", 0), "replies": t["snippet"].get("totalReplyCount", 0),
                             "retrieved_at": RETRIEVED})
        if n % 25 == 0:
            print(f"评论：已处理 {n}/{len(videos)} 条视频，共 {len(comments)} 条评论")
except Fatal as e:
    status = f"中断：{e}"
    print("\n⚠️ " + str(e))
except KeyboardInterrupt:
    status = "中断：手动停止"
finally:
    save(status)
