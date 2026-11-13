import sys,re,warnings; warnings.filterwarnings('ignore'); sys.path.insert(0,'/tmp/claude-0/rq')
import os; os.chdir('/tmp/claude-0/rq'); exec(open('lib.py').read())
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob; from afinn import Afinn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from gensim.models import KeyedVectors
U='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
M=pd.read_csv(U+'master_scored.csv',low_memory=False).set_index('uid')
AI=pd.read_csv(U+'ai_precode_user_content.csv',low_memory=False).set_index('uid')
mp={'F1':'P','F2':'U','F3':'N','F4':'M'}
H={}
for f,c in [('coding_v2_组员5.xlsx','组员5'),('coding_v2_组员1.xlsx','组员1')]:
    H[c]=human_vars(load(f,'V3_用户内容60'),remap=(c=='组员1'))['F'].map(mp)
test=H['组员5'].index.union(H['组员1'].index)
txt=M.text_en
sia=SentimentIntensityAnalyzer(); af=Afinn()
lab=lambda x,t: 'P' if x>t else ('N' if x<-t else 'U')
def target(s):
    sents=re.split(r'(?<=[.!?。！？\n])\s*',str(s)); k=[x for x in sents if re.search(r'ya ?kun|亚坤|亞坤',x,re.I)]
    return ' '.join(k) if k else str(s)
P=pd.DataFrame(index=test)
P['AI 按编码手册']=AI.F_sentiment.reindex(test).map(mp)
P['VADER（整段）']=[lab(sia.polarity_scores(str(txt.get(u,'')))['compound'],0.05) for u in test]
P['VADER（只看提到 Ya Kun 的句子）']=[lab(sia.polarity_scores(target(txt.get(u,'')))['compound'],0.05) for u in test]
P['TextBlob 词典']=[lab(TextBlob(str(txt.get(u,''))).sentiment.polarity,0.05) for u in test]
P['AFINN 词典']=[lab(af.score(str(txt.get(u,''))),0) for u in test]
# supervised, trained on AI labels excluding test
r=pd.read_csv(U+'RQ2_逐条_1103.csv').set_index('uid'); tr=r[~r.index.isin(test)]
tr=tr[tr.F_sentiment.isin(['F1','F2','F3'])]; ytr=tr.F_sentiment.map(mp); Xtr=txt.reindex(tr.index).fillna('')
tf=TfidfVectorizer(ngram_range=(1,2),min_df=2,sublinear_tf=True); lr=LogisticRegression(max_iter=3000,class_weight='balanced',C=3)
lr.fit(tf.fit_transform(Xtr),ytr); P['监督学习：TF-IDF（用 AI 标签训练）']=lr.predict(tf.transform(txt.reindex(test).fillna('')))
wv=KeyedVectors.load('/tmp/claude-0/wv/gn500k.kv')
def emb(s):
    t=[w for w in re.sub(r'[^a-z\s]',' ',str(s).lower()).split() if w in wv]
    return np.mean([wv[w] for w in t],0) if t else np.zeros(300)
lr2=LogisticRegression(max_iter=3000,class_weight='balanced').fit(np.vstack(Xtr.apply(emb)),ytr)
P['监督学习：词向量（用 AI 标签训练）']=lr2.predict(np.vstack(txt.reindex(test).fillna('').apply(emb)))
print('train n',len(tr),ytr.value_counts().to_dict())
rows=[]
for meth in P.columns:
    for c,h in H.items():
        m=h.reindex(test).isin(['P','U','N'])&P[meth].isin(['P','U','N'])
        x,y=h.reindex(test)[m],P[meth][m]
        rows.append([meth,c,int(m.sum()),round(k(x,y),2),round(ac1(x,y),2),round((x==y).mean(),2)])
R=pd.DataFrame(rows,columns=['方法','对照组员','n','κ','AC1','一致率'])
S=R.groupby('方法',sort=False)[['κ','AC1','一致率']].mean().round(2); print(R.to_string()); print(S.sort_values('κ',ascending=False))
hh=H['组员5'].reindex(test); h1=H['组员1'].reindex(test); m=hh.isin(['P','U','N'])&h1.isin(['P','U','N'])
print('human-human 3class',int(m.sum()),round(k(hh[m],h1[m]),2),round(ac1(hh[m],h1[m]),2),round((hh[m]==h1[m]).mean(),2))
R.to_csv('/tmp/claude-0/sent/sentiment_methods.csv',index=False)
