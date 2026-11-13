"""给总表每条 text_en 打 heritage 轴分（SemAxis，同 score.py）+ vMFD 忠诚/权威 + VADER 情感"""
import pandas as pd, numpy as np, re, sys, logging, warnings
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import STOPWORDS
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import vMFD
logging.disable(logging.INFO); warnings.filterwarnings("ignore")
IN, OUT, W2V = sys.argv[1], sys.argv[2], sys.argv[3]
wv = KeyedVectors.load(W2V + "/w2v_500k.kv"); A = np.load(W2V + "/heritage_axis.npy")
stop = set(STOPWORDS) | {"ya", "kun", "yakun", "kaya", "toast", "singapore", "sg"}
vo = vMFD.vMFD(); sia = SentimentIntensityAnalyzer()
def toks(s):
    s = re.sub(r"&#0?39;", "'", str(s)); s = re.sub(r"http\S+|@\S+", " ", s)
    return [w for w in re.sub(r"[^a-z\s]", " ", s.lower()).split() if w not in stop]
def heritage(s):
    t = [w for w in toks(s) if w in wv]
    if not t: return (np.nan, np.nan, np.nan, 0)
    v = np.array([float(wv[w] @ A / np.linalg.norm(wv[w])) for w in t])
    return (np.abs(v).mean(), v.mean(), v.var(), len(t))
def moral(s):
    try:
        m = vo.calculate_metrics(" ".join(toks(s)))
        return (m["valence"]["loyalty"], m["valence"]["authority"], m["strength"]["loyalty"], m["strength"]["authority"])
    except Exception:
        return (np.nan,) * 4
def vader(s):
    s = re.sub(r"http\S+", " ", str(s)); c = sia.polarity_scores(s)["compound"]
    return c, ("positive" if c >= 0.05 else "negative" if c <= -0.05 else "neutral")
M = pd.read_csv(IN, low_memory=False)
H = pd.DataFrame(M.text_en.apply(heritage).tolist(), columns=["h_strength", "h_valence", "h_ambivalence", "h_nwords"])
MO = pd.DataFrame(M.text_en.apply(moral).tolist(), columns=["loyalty_valence", "authority_valence", "loyalty_strength", "authority_strength"])
V = pd.DataFrame(M.text_en.apply(vader).tolist(), columns=["vader_compound", "vader_label"])
M = pd.concat([M, H, MO, V], axis=1)
M["h_reliable"] = M.h_nwords >= 5                       # 少于 5 个有效词：分数不稳，不进主分析
for c in ["h_strength", "h_valence", "h_ambivalence", "loyalty_valence", "authority_valence", "loyalty_strength", "authority_strength", "vader_compound"]:
    M[c] = M[c].round(4)
M.to_csv(OUT, index=False, encoding="utf-8-sig")
print(M.shape, "| h_reliable:", int(M.h_reliable.sum()))
