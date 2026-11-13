import pandas as pd, numpy as np, re, warnings; warnings.filterwarnings('ignore')
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import STOPWORDS
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from scipy.stats import kruskal, mannwhitneyu, spearmanr
U='/mnt/user-data/uploads/文稿:YaKun_vMFD/'
M=pd.read_csv(U+'analysis_outputs/master_scored.csv',low_memory=False).set_index('uid')
L=pd.read_csv(U+'analysis_outputs/heritage_labeling_AUC_逐条_1103.csv'); L=L[L.agree==True]
test=pd.DataFrame({'uid':L.uid,'y':L.both.astype(int)})
off=pd.read_csv('/tmp/claude-0/rq/heritage_binary_official.csv')[['uid','Hbin']].rename(columns={'Hbin':'y'})
r2=pd.read_csv(U+'analysis_outputs/RQ2_逐条_1103.csv')
r=r2[['uid','anyH']].rename(columns={'anyH':'y'})
dev=pd.concat([off,r]); dev['y']=dev.y.astype(int); dev=dev[~dev.uid.isin(test.uid)].drop_duplicates('uid')
dev=dev[dev.uid.map(M.text_en).notna().values]
stop=set(STOPWORDS)|{'ya','kun','yakun','kaya','toast','singapore','sg'}
def toks(s):
    s=re.sub(r"http\S+|@\S+|#"," ",str(s)); return [w for w in re.sub(r"[^a-z\s]"," ",s.lower()).split() if w not in stop]
wv=KeyedVectors.load('/tmp/claude-0/wv/gn500k.kv')
def emb(t):
    t=[w for w in toks(t) if w in wv]
    return np.mean([wv[w]/np.linalg.norm(wv[w]) for w in t],0) if t else np.zeros(wv.vector_size)
allM=M[M.text_en.notna()]
X=np.vstack([emb(t) for t in allM.text_en]); idx={u:i for i,u in enumerate(allM.index)}
Xd=X[[idx[u] for u in dev.uid]]; yd=dev.y.values
lr=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced').fit(Xd,yd)
full=lr.predict_proba(X)[:,1]
Xt=X[[idx[u] for u in test.uid if u in idx]]; yt=test.y.values[[u in idx for u in test.uid]]
print('dev',len(dev),'test AUC (sanity, expect ~0.73):',round(roc_auc_score(yt,lr.predict_proba(Xt)[:,1]),3))
# cross-fitted scores for training items
oof=pd.Series(full,index=allM.index)
skf=StratifiedKFold(5,shuffle=True,random_state=5342)
for tr,te in skf.split(Xd,yd):
    m=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced').fit(Xd[tr],yd[tr])
    oof.loc[dev.uid.values[te]]=m.predict_proba(Xd[te])[:,1]
print('OOF AUC on dev labels:',round(roc_auc_score(yd,oof.loc[dev.uid].values),3))
S=oof.rename('h')
out=[]
# A. RQ2 by platform/dataset
a=r2[['uid','dataset','platform']].copy(); a['h']=a.uid.map(S)
g=a.groupby('dataset').h.agg(['count','median','mean']).round(3).sort_values('median',ascending=False); print('\nA. RQ2 heritage score by source'); print(g)
print('KW p',kruskal(*[x.h.dropna() for _,x in a.groupby('dataset')]).pvalue)
gp=a.groupby('platform').h.agg(['count','median']).round(3).sort_values('median',ascending=False); print(gp)
g.to_csv('A_rq2_by_source.csv')
# also: with vs without heritage label (sanity)
a['anyH']=a.uid.map(r2.set_index('uid').anyH); print('sanity anyH medians',a.groupby('anyH').h.median().round(3).to_dict())
# B. tourist vs local (human labels, both coders agree)
d=pd.read_csv(U+'analysis_outputs/RQ4_最终编码_草稿.csv'); d=d.rename(columns={'uid（勿改）':'uid'})
ag=d[(d['组员1 G']==d['组员2 G'])&d['组员1 G'].isin(['T1','T2'])].copy(); ag['h']=ag.uid.map(S)
print('\nB. both coders agree:',ag['组员1 G'].value_counts().to_dict())
print(ag.groupby('组员1 G').h.agg(['count','median','mean']).round(3))
t1,t2=ag[ag['组员1 G']=='T1'].h.dropna(),ag[ag['组员1 G']=='T2'].h.dropna()
print('MWU p',round(mannwhitneyu(t1,t2).pvalue,4))
# also the 'final G' (incl. adjudicated) where available
fg=d[d['最终 G'].isin(['T1','T2'])].copy(); fg['h']=fg.uid.map(S); print('final G (resolved only)',fg.groupby('最终 G').h.agg(['count','median']).round(3).to_dict())
ag[['uid','组员1 G','h']].to_csv('B_tourist_vs_local.csv',index=False)
# C. heritage score vs engagement per view (user videos)
for ds in ['M5 TikTok UGC','M11 YouTube videos']:
    v=M[(M.dataset==ds)&(M.yakun_related==True)&(~M.author_type.isin(['brand','brand_or_franchise']))].copy()
    v=v[(v.views>0)]; v['epv']=v.engagement/v.views; v['h']=v.index.map(S)
    v=v.dropna(subset=['h','epv'])
    rho=spearmanr(v.h,v.epv); v['tert']=pd.qcut(v.h,3,labels=['low','mid','high'])
    print(f'\nC. {ds}: n={len(v)} Spearman rho={rho.correlation:.3f} p={rho.pvalue:.4f}')
    tt=v.groupby('tert').agg(n=('epv','size'),epv_median=('epv','median'),views_median=('views','median'),eng_median=('engagement','median')).round(4); print(tt)
    print(' high vs low MWU p',round(mannwhitneyu(v[v.tert=='high'].epv,v[v.tert=='low'].epv).pvalue,4))
    tt.to_csv(f'C_{ds.split()[1]}_tertiles.csv')
S.rename_axis('uid').reset_index().to_csv('heritage_score_crossfitted.csv',index=False)
