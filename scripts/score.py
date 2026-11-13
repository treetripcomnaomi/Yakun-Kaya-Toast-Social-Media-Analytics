import pandas as pd, numpy as np, re, sys, logging
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import STOPWORDS
import vMFD
logging.disable(logging.INFO)
IN, OUT = sys.argv[1], sys.argv[2]
wv = KeyedVectors.load('w2v_500k.kv'); A = np.load('heritage_axis.npy')
stop = set(STOPWORDS) | {'ya','kun','yakun','kaya','toast','singapore','sg'}
vo = vMFD.vMFD()
def toks(s):
    s = re.sub(r'&#0?39;', "'", str(s)); s = re.sub(r'http\S+|@\S+', ' ', s)
    return [w for w in re.sub(r'[^a-z\s]', ' ', s.lower()).split() if w not in stop]
def heritage(s):
    t = [w for w in toks(s) if w in wv]
    if not t: return pd.Series({'h_strength':np.nan,'h_valence':np.nan,'h_ambivalence':np.nan,'h_nwords':0})
    v = np.array([float(wv[w]@A/np.linalg.norm(wv[w])) for w in t])
    return pd.Series({'h_strength':np.abs(v).mean(),'h_valence':v.mean(),'h_ambivalence':v.var(),'h_nwords':len(t)})
def moral(s):
    try:
        m = vo.calculate_metrics(' '.join(toks(s)))
        return pd.Series({'loyalty_valence':m['valence']['loyalty'],'authority_valence':m['valence']['authority'],
                          'loyalty_strength':m['strength']['loyalty'],'authority_strength':m['strength']['authority']})
    except Exception:
        return pd.Series({'loyalty_valence':np.nan,'authority_valence':np.nan,'loyalty_strength':np.nan,'authority_strength':np.nan})
d = pd.read_csv(IN)
d = pd.concat([d, d.text.apply(heritage), d.text.apply(moral)], axis=1).round(4)
d.to_csv(OUT, index=False, encoding='utf-8-sig')
print('scored', len(d), '| no matched words:', int((d.h_nwords==0).sum()))
print(d.groupby('source_type')[['h_valence','loyalty_valence','authority_valence']].mean().round(3).to_string())
o = d[(d.source_type=='ordinary_user') & (d.h_nwords>=3)].sort_values('h_valence')
print('\nMOST HERITAGE (ordinary users):')
for _,r in o.tail(6).iloc[::-1].iterrows(): print(round(r.h_valence,3), '|', r.text[:110].replace('\n',' '))
print('\nMOST NOVELTY (ordinary users):')
for _,r in o.head(6).iterrows(): print(round(r.h_valence,3), '|', r.text[:110].replace('\n',' '))
print('\ncorr heritage vs loyalty/authority valence:', round(d.h_valence.corr(d.loyalty_valence),2), round(d.h_valence.corr(d.authority_valence),2))
