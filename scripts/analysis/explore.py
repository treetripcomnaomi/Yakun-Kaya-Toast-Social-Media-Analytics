import pandas as pd, numpy as np, re, warnings
from scipy.stats import kruskal, mannwhitneyu
warnings.filterwarnings("ignore")
M = pd.read_csv("out/master_scored.csv", low_memory=False)
R = M[M.h_reliable]
print("== heritage 分数（h_valence，越高越偏传统）：官方帖 × 品牌")
o = R[R.content_type == "official_post"]
print(o.groupby(["brand"]).h_valence.agg(["count", "mean", "median"]).round(4).to_string())
print("Kruskal-Wallis:", kruskal(*[g.h_valence for _, g in o.groupby("brand")]))
print("\n== 用户内容 vs 品牌（只看 Ya Kun 相关）")
y = R[R.yakun_related]
print(y.groupby("content_type").h_valence.agg(["count", "mean", "median"]).round(4).to_string())
print("\n== 稳健性：原生英文 vs 含翻译（Ya Kun 相关用户内容）")
uu = y[y.content_type != "official_post"]
print(uu.groupby("translated").h_valence.agg(["count", "mean"]).round(4).to_string())
print("\n== VADER 情感：客户（Ya Kun 相关用户内容）vs 行业（品类内容）")
uc = M[(M.content_type != "official_post") & (M.author_type != "brand")]
grp = np.where(uc.yakun_related, "client", np.where(uc.industry, "industry", "other"))
t = pd.crosstab(grp, uc.vader_label, normalize="index").round(3); t["n"] = pd.Series(grp).value_counts(); print(t.to_string())
print("\n== 过去 30 天（2026-09-25 至 10-25）自抓内容声量")
d = pd.to_datetime(M.published_date, errors="coerce")
w = M[(d >= "2026-09-25") & (d <= "2026-10-25") & (M.content_type != "official_post")]
print(pd.crosstab(w.dataset, np.where(w.yakun_related, "client", np.where(w.industry, "industry", "competitor/other"))).to_string())
print("\n== Brand24 窗口:", M[M.dataset == "M7 Brand24"].published_date.min(), "-", M[M.dataset == "M7 Brand24"].published_date.max())
