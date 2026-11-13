"""
Collect Reddit posts and comments that mention Ya Kun.
Run on your own Mac (Terminal), from this scripts folder:
    python3 reddit_collect.py
Output: ../reddit_yakun.csv   (needs only the Python standard library)
Uses Reddit's public JSON pages, with a pause between requests to stay polite.
"""
import json, time, csv, urllib.request, urllib.parse, os

SUBS = ["singapore", "askSingapore", "SingaporeEats"]
QUERIES = ['"ya kun"', "yakun"]
UA = {"User-Agent": "NUS-NMC5342-student-project/0.1 (academic research)"}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reddit_yakun.csv")

def get(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            print("  retry", attempt + 1, e); time.sleep(10)
    return None

posts = {}
for sub in SUBS:
    for q in QUERIES:
        after = None
        for page in range(5):                       # up to ~500 results per query
            params = {"q": q, "restrict_sr": 1, "sort": "new", "limit": 100, "t": "all"}
            if after: params["after"] = after
            data = get(f"https://www.reddit.com/r/{sub}/search.json?" + urllib.parse.urlencode(params))
            time.sleep(2)
            if not data: break
            for c in data["data"]["children"]:
                p = c["data"]; posts[p["id"]] = p
            after = data["data"].get("after")
            print(f"r/{sub} {q} page {page+1}: total posts so far {len(posts)}")
            if not after: break

rows = []
def walk(children, post_id):
    for c in children:
        if c.get("kind") != "t1": continue
        d = c["data"]
        rows.append({"type": "comment", "post_id": post_id, "id": d["id"], "subreddit": d.get("subreddit"),
                     "created_utc": time.strftime("%Y-%m-%d", time.gmtime(d.get("created_utc", 0))),
                     "author": d.get("author"), "score": d.get("score"), "num_comments": "",
                     "title": "", "text": d.get("body", ""), "url": "https://www.reddit.com" + d.get("permalink", "")})
        rep = d.get("replies")
        if isinstance(rep, dict): walk(rep["data"]["children"], post_id)

for i, (pid, p) in enumerate(posts.items(), 1):
    rows.append({"type": "post", "post_id": pid, "id": pid, "subreddit": p.get("subreddit"),
                 "created_utc": time.strftime("%Y-%m-%d", time.gmtime(p.get("created_utc", 0))),
                 "author": p.get("author"), "score": p.get("score"), "num_comments": p.get("num_comments"),
                 "title": p.get("title", ""), "text": p.get("selftext", ""), "url": "https://www.reddit.com" + p.get("permalink", "")})
    data = get(f"https://www.reddit.com/comments/{pid}.json?limit=500")
    time.sleep(2)
    if data and len(data) > 1: walk(data[1]["data"]["children"], pid)
    print(f"comments: post {i}/{len(posts)}, rows so far {len(rows)}")

with open(OUT, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["type"]); w.writeheader(); w.writerows(rows)
print("Saved", len(rows), "rows to", os.path.abspath(OUT))
