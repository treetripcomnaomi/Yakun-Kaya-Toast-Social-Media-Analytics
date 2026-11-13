"""给分析产出加中文说明列（在 topics.py、master_and_metrics.py 之后运行；可重复运行）。
话题名是人根据高频词和例子取的；如果重跑主题模型、话题编号变了，要重新核对 NAMES。"""
import pandas as pd, sys, os
OUT = sys.argv[1]
# ---- Step 4 主题 ----
NAMES = {("client", 0): ("kaya toast 本身", "好不好吃、出名、best；以 TikTok 和 YouTube 视频为主"),
         ("client", 1): ("美食视频闲聊", "多是 YouTube 评论在聊博主，和 Ya Kun 关系弱，解读时可略过"),
         ("client", 2): ("半熟蛋", "蛋怎么吃、蘸面包——用户在意「吃法」"),
         ("client", 3): ("打卡标签帖", "几乎全是 TikTok，只有 #yakunkayatoast 等标签，信息量低"),
         ("client", 4): ("表白 I love Ya Kun", "最正面的一组（87%），适合转发做 UGC"),
         ("client", 5): ("饮品（kopi、teh、豆浆咖啡）", "最大话题；夸豆浆咖啡和抱怨价格都集中在这里，负面也最多"),
         ("client", 6): ("酱油加多少", "负面最高（21%），多是说别人「酱油放太多 / 拿错酱油」——吃法教学的需求"),
         ("client", 7): ("夸赞 / 想吃", "so good、make this permanent，常见于官方帖下评论"),
         ("industry", 0): ("kaya toast 泛谈", "品类本身好不好吃"),
         ("industry", 1): ("博主互动", "评论在夸博主，和品类关系弱"),
         ("industry", 2): ("传统早餐", "把 kaya toast 当作新加坡传统早餐来认识"),
         ("industry", 3): ("蛋 + 黄油 + 面包 + 咖啡的吃法", "品类讨论里最具体的一组"),
         ("industry", 4): ("新加坡人 / 本地身份", "Singaporean breakfast、auntie 等身份话题"),
         ("industry", 5): ("泛泛好吃、想去", "最大的一组，信息量低")}
t = pd.read_csv(os.path.join(OUT, "step4_topics.csv"))
t = t[[c for c in t.columns if c not in ["话题名", "正面占比", "负面占比", "说明"]]]
a = pd.read_csv(os.path.join(OUT, "step4_topic_assignments.csv"))
m = pd.read_csv(os.path.join(OUT, "master_scored.csv"), low_memory=False, usecols=["uid", "vader_label"])
s = a.merge(m, on="uid").groupby(["set", "topic"]).vader_label.value_counts(normalize=True).unstack(fill_value=0)
t["话题名"] = [NAMES.get((r.set, r.topic), ("", ""))[0] for r in t.itertuples()]
t["正面占比"] = [round(s.loc[(r.set, r.topic), "positive"], 2) for r in t.itertuples()]
t["负面占比"] = [round(s.loc[(r.set, r.topic), "negative"], 2) for r in t.itertuples()]
t["说明"] = [NAMES.get((r.set, r.topic), ("", ""))[1] for r in t.itertuples()]
front = ["set", "topic", "话题名", "share_of_docs", "正面占比", "负面占比", "说明"]
t[front + [c for c in t.columns if c not in front]].to_csv(os.path.join(OUT, "step4_topics.csv"), index=False, encoding="utf-8-sig")
# ---- Step 1/5 指标 ----
NOTE = {("Ya Kun", "Instagram"): "发帖最少之一（每天 0.28 帖），但每帖互动 188、互动率 0.94%，与 Old Chang Kee 几乎持平——问题在量不在质",
        ("Ya Kun", "TikTok"): "近 6 个月 0 帖：2025-03 起停更",
        ("Old Chang Kee", "Instagram"): "发帖最多（每天 0.88 帖）、每帖互动最高（338）；Step 1 SMART 目标的参照对象",
        ("Old Chang Kee", "TikTok"): "持续在发，但每帖互动不高（33）",
        ("Toast Box", "Instagram"): "发帖频率和 Ya Kun 相同，每帖互动只有 Ya Kun 的 41%",
        ("Toast Box", "TikTok"): "6 个月只发 7 帖；账号是否官方待核对（M1 记 2.7k 粉，抓到的只有 361）",
        ("% Arabica", "Instagram"): "发得多但单帖互动低（71），审美统一的极简风格",
        ("% Arabica", "TikTok"): "粉丝很少（83），互动率高是因为分母小，不宜直接比较"}
mt = pd.read_csv(os.path.join(OUT, "step1_step5_metrics.csv"))
mt = mt[[c for c in mt.columns if c != "说明"]]
mt["说明"] = [("Ya Kun TikTok 活跃期（2024-07 至 2025-03）的数字，用来补充停更后没有的 6 个月数据" if "active period" in str(r.platform)
              else NOTE.get((r.brand, r.platform), "")) for r in mt.itertuples()]
mt.to_csv(os.path.join(OUT, "step1_step5_metrics.csv"), index=False, encoding="utf-8-sig")
print(t[["set", "topic", "话题名", "share_of_docs", "正面占比", "负面占比"]].to_string()); print(mt[["brand", "platform", "说明"]].to_string())
