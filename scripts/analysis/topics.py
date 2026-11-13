"""Step 4 主题：NMF 主题模型（TF-IDF，1–2 词组）+ 高频词组；客户（Ya Kun 相关用户内容）和行业（品类内容）各一套"""
import pandas as pd, numpy as np, re, warnings
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF
warnings.filterwarnings("ignore")
M = pd.read_csv("out/master_scored.csv", low_memory=False)
U = M[(M.content_type != "official_post") & (M.author_type != "brand") & ~(M.text_en.astype(str).str.contains(r"\(political, off-topic\)"))].copy()
U["clean"] = (U.text_en.astype(str).str.lower().str.replace(r"http\S+|@\S+|#", " ", regex=True)
              .str.replace(r"[^a-z\s']", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip())
STOP = list(__import__("sklearn.feature_extraction.text", fromlist=["ENGLISH_STOP_WORDS"]).ENGLISH_STOP_WORDS | {
    "ya", "kun", "yakun", "singapore", "sg", "just", "like", "really", "im", "dont", "don", "lol", "haha", "yes", "oh", "got", "know",
    "video", "fyp", "foryou", "foryoupage", "viral", "tiktok", "shorts", "user", "s", "t", "u", "thank", "thanks", "pls", "need", "want"})
out_t, out_d = [], []
for name, sub, k in [("client", U[U.yakun_related], 8), ("industry", U[U.industry], 6)]:
    s = sub[sub.clean.str.split().str.len() >= 4]
    tv = TfidfVectorizer(stop_words=STOP, ngram_range=(1, 2), min_df=4, max_df=0.5)
    X = tv.fit_transform(s.clean); terms = np.array(tv.get_feature_names_out())
    nmf = NMF(n_components=k, random_state=5342, init="nndsvda", max_iter=500); W = nmf.fit_transform(X)
    lab = W.argmax(1); share = pd.Series(lab).value_counts(normalize=True)
    for i, comp in enumerate(nmf.components_):
        top = terms[comp.argsort()[::-1][:12]]
        ex = s.iloc[np.argsort(-W[:, i])[:3]].text_en.astype(str).str[:120].tolist()
        out_t.append({"set": name, "topic": i, "share_of_docs": round(share.get(i, 0), 3), "top_terms": ", ".join(top),
                      "example_1": ex[0], "example_2": ex[1], "example_3": ex[2]})
    out_d.append(pd.DataFrame({"uid": s.uid.values, "set": name, "topic": lab}))
    cv = CountVectorizer(stop_words=STOP, ngram_range=(2, 3), min_df=3); C = cv.fit_transform(s.clean)
    f = pd.Series(np.asarray(C.sum(0)).ravel(), index=cv.get_feature_names_out()).sort_values(ascending=False).head(25)
    print(f"\n#### {name}: {len(s)} docs | top phrases:", ", ".join(f"{a}({b})" for a, b in f.items()))
T = pd.DataFrame(out_t); T.to_csv("out/step4_topics.csv", index=False, encoding="utf-8-sig")
pd.concat(out_d).to_csv("out/step4_topic_assignments.csv", index=False, encoding="utf-8-sig")
for _, r in T.iterrows(): print(r.set, r.topic, r.share_of_docs, "|", r.top_terms)
