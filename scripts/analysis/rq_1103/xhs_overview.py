"""小红书方案 A：整体描述（不逐篇判游客导向；不用 IP 属地和身份线索列——红线）
输入：cleaned_data/xhs_notes_merged_1102.csv（295 篇，Ya Kun 相关 = yakun_text + yakun_inferred）
      xhs_补录/*.xlsx 里组员补录的完整正文（只取「完整正文」列）
输出：analysis_outputs/小红书_整体描述_1103.csv（逐篇线索）"""
import pandas as pd, glob, re, os
os.chdir(os.path.expanduser("~/mnt/文稿:YaKun_vMFD"))
m = pd.read_csv("cleaned_data/xhs_notes_merged_1102.csv")
y = m[m.relevance.isin(["yakun_text", "yakun_inferred"])].copy()
full = {}
for f in glob.glob("xhs_补录/*.xlsx"):
    d = pd.read_excel(f, sheet_name="补录")
    for _, r in d.iterrows():
        t = r.get("完整正文（复制粘贴原文）")
        if isinstance(t, str) and len(t.strip()) > 20:
            full[str(r["uid（勿改）"]).strip()] = t.strip()
def key(r):
    for k in [str(r.note_id), "M6_" + str(r.note_id)]:
        if k in full: return full[k]
    return None
y["full_text"] = y.apply(key, axis=1)   # 11/3 检查：补录表的完整正文列都还是空的
y["has_full"] = y.full_text.notna()
y["t"] = (y.title.fillna("") + " " + y.full_text.fillna(y.desc.fillna(""))).str.lower()
CUES = {
 "打卡/必吃/攻略": r"打卡|必吃|必去|必喝|国民早餐|國民早餐|攻略|旅游|旅行|游客|遊客|行程|citywalk|第一次来|来新加坡|來新加坡|樟宜|机场",
 "豆浆咖啡": r"豆浆|豆漿|soya|soy",
 "太甜/少甜": r"太甜|好甜|很甜|偏甜|有点甜|有點甜|甜腻|甜膩|齁|少甜|无糖|無糖|少糖|kosong|siew dai|siu dai",
 "在家复刻": r"复刻|復刻|在家|自制|自製|自己做|做法|教程|食谱|食譜",
 "价格": r"贵|貴|便宜|价格|價格|新币|新幣|\$|sgd|性价比|性價比|划算|涨价|漲價",
 "heritage（老字号/历史/本地情怀）": r"1944|老字号|老字號|历史|歷史|传统|傳統|情怀|情懷|古早|老牌|海南|本地人|地道|正宗",
 "半熟蛋": r"半熟蛋|溏心蛋|生熟蛋|鸡蛋|雞蛋|egg",
 "负面词": r"避雷|(?<![不没])踩雷|难吃|難吃|失望|不好吃|翻车|翻車|智商税|不值|吃不惯|吃不动|吃不動|拉垮|不是很爱|(?<!不)一般",
    "点单攻略/怎么吃": r"怎么点|怎麼點|点单|點單|攻略|不踩雷|怎么吃|怎麼吃|教你|指南",
    "中国大陆/澳门/海外门店": r"苏州|蘇州|重庆|重慶|澳门|澳門|海口|东京|東京|上海|北京|南京|成都|广州|廣州|深圳|杭州|厦门|香港|台湾|台北|日本|首尔|韩国|曼谷|雅加达|菲律宾|马尼拉",
}
for k, rx in CUES.items(): y[k] = y.t.str.contains(rx, regex=True)
y["soya_search_only"] = y.search_terms.fillna("").str.split(";").apply(lambda s: all("豆浆" in x for x in s if x.strip()))
out = y[["note_id", "url", "published_date", "type", "title", "engagement", "has_full", "search_terms", "soya_search_only"] + list(CUES)]
out.to_csv("analysis_outputs/小红书_整体描述_1103.csv", index=False, encoding="utf-8-sig")
print("Ya Kun 相关笔记", len(y), "；有完整正文", int(y.has_full.sum()))
print(pd.to_datetime(y.published_date).dt.to_period("Q").value_counts().sort_index().tail(6).to_dict())
for k in CUES:
    s = y[k]; print(f"{k}: {s.sum()} ({s.mean():.0%})  有完整正文的 {y[y.has_full][k].mean():.0%}  互动中位数 有 {y[s].engagement.median():.0f} / 无 {y[~s].engagement.median():.0f}")
ns = y[~y.soya_search_only]; print("不是只靠豆浆搜索找到的", len(ns), "其中豆浆咖啡", ns["豆浆咖啡"].sum(), f"{ns['豆浆咖啡'].mean():.0%}")
print("互动 中位数", y.engagement.median(), "均值", round(y.engagement.mean()), "视频", (y.type=='video').sum())
print(y.sort_values("engagement", ascending=False)[["published_date","type","engagement","title"]].head(12).to_string())
