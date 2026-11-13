"""Reddit（M10）：组员 11/2 用 Apify 抓回 returned_1103/Reddit_apify.csv（11 帖 + 264 评论，r/singapore）。
只摘原话补充 RQ2，不并进 1,575 条样本。排除政治 / 社会新闻帖（台湾标注、缅甸抵制、扔沙子、猪肉谣言、2021 支持 Ya Kun 帖）和与 Ya Kun 无关的每日闲聊评论。
输出 analysis_outputs/Reddit_原话_1103.csv（相关帖下的全部评论，不含用户名）"""
import pandas as pd, os, re, html
os.chdir(os.path.expanduser("~/mnt/文稿:YaKun_vMFD"))
r = pd.read_csv("returned_1103/Reddit_apify.csv", low_memory=False)
posts = r[r.dataType == "post"].set_index("id").title.to_dict()
c = r[r.dataType == "comment"].copy()
KEEP = {"t3_17ohfd9": "2023 远东广场 Ya Kun 婚礼", "t3_1m21k2y": "2025 Fullerton 酒店 Ya Kun 下午茶 S$60++",
        "t3_1s5l7dy": "2026 东京 Ya Kun 套餐", "t3_hbruvn": "2020 Ya Kun 新宿开店", "t3_8u4uer": "2018 游客行程求建议",
        "t3_1uhf8sb": "2026 每日闲聊帖（只留提到 Ya Kun 的）"}
c = c[c.postId.isin(KEEP)]
c["thread"] = c.postId.map(KEEP)
c["text"] = c.body.astype(str).map(html.unescape)
mention = c.text.str.contains(r"ya ?kun|kaya|kopi|toast|teh", case=False, regex=True)
c = c[~c.postId.isin(["t3_1uhf8sb", "t3_8u4uer"]) | mention]
out = c[["thread", "createdAt", "upVotes", "text", "url"]].sort_values(["thread", "upVotes"], ascending=[True, False])
out.to_csv("analysis_outputs/Reddit_原话_1103.csv", index=False, encoding="utf-8-sig")
print(len(r), "条 →", len(out), "条相关评论"); print(out.thread.value_counts())
