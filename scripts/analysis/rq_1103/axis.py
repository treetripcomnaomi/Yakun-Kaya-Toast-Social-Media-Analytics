import pandas as pd, numpy as np, re, warnings; warnings.filterwarnings('ignore')
from gensim.models import KeyedVectors
from gensim.parsing.preprocessing import STOPWORDS
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
U='/mnt/user-data/uploads/文稿:YaKun_vMFD/'
M=pd.read_csv(U+'analysis_outputs/master_scored.csv',low_memory=False).set_index('uid')
L=pd.read_csv(U+'analysis_outputs/heritage_labeling_AUC_逐条_1103.csv'); L=L[L.agree==True]
test=pd.DataFrame({'uid':L.uid,'y':L.both.astype(int)}); test['text']=test.uid.map(M.text_en)
off=pd.read_csv('/tmp/claude-0/rq/heritage_binary_official.csv')[['uid','Hbin','text_en']].rename(columns={'Hbin':'y','text_en':'text'})
r=pd.read_csv(U+'analysis_outputs/RQ2_逐条_1103.csv')[['uid','anyH']].rename(columns={'anyH':'y'}); r['text']=r.uid.map(M.text_en)
dev=pd.concat([off,r]); dev=dev[~dev.uid.isin(test.uid)].dropna(subset=['text']).drop_duplicates('uid')
print('dev',len(dev),dev.y.mean().round(3),'| test',len(test),test.y.mean().round(3),test.text.isna().sum())
S=pd.read_csv(U+'seed_words_v1.csv'); S=S[S.status=='keep']
H0=list(S[S.side=='heritage'].word); N0=list(S[S.side=='novelty'].word)
H1=H0+['kopitiam','hainanese','nanyang','olden','grandma','grandmother','decades','hawker','uncle','oldschool','kampung','nostalgically','traditions','heirloom','since']
N1=N0+['limited','launch','exclusive','merch','giveaway','unboxing','newest','trend','tiktok','aesthetic']
stop=set(STOPWORDS)|{'ya','kun','yakun','kaya','toast','singapore','sg'}
def toks(s):
    s=re.sub(r"http\S+|@\S+|#"," ",str(s)); return [w for w in re.sub(r"[^a-z\s]"," ",s.lower()).split() if w not in stop]
def axis(wv,H,N):
    h=np.mean([wv[w]/np.linalg.norm(wv[w]) for w in H if w in wv],0); n=np.mean([wv[w]/np.linalg.norm(wv[w]) for w in N if w in wv],0)
    a=h-n; return a/np.linalg.norm(a)
def score(wv,A,text,agg):
    t=[w for w in toks(text) if w in wv]
    if not t: return 0.0
    v=np.array([wv[w]@A/np.linalg.norm(wv[w]) for w in t])
    if agg=='mean': return v.mean()
    if agg=='top3': return np.sort(v)[-3:].mean()
    if agg=='max': return v.max()
def emb(wv,text):
    t=[w for w in toks(text) if w in wv]
    return np.mean([wv[w]/np.linalg.norm(wv[w]) for w in t],0) if t else np.zeros(wv.vector_size)
res=[]; store={}
for en,path in [('GoogleNews','/tmp/claude-0/wv/gn500k.kv'),('GloVe-Twitter','/tmp/claude-0/wv/gt500k.kv')]:
    wv=KeyedVectors.load(path)
    for sn,(H,N) in {'原种子词':(H0,N0),'加领域种子词':(H1,N1)}.items():
        A=axis(wv,H,N)
        for agg in ['mean','top3','max']:
            d=dev.text.apply(lambda s:score(wv,A,s,agg)); t=test.text.apply(lambda s:score(wv,A,s,agg))
            res.append([en,sn,agg,round(roc_auc_score(dev.y,d),3),round(roc_auc_score(test.y,t),3)]); store[(en,sn,agg)]=t
    Xd=np.vstack(dev.text.apply(lambda s:emb(wv,s))); Xt=np.vstack(test.text.apply(lambda s:emb(wv,s)))
    from sklearn.model_selection import cross_val_predict
    lr=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced')
    cv=cross_val_predict(lr,Xd,dev.y,cv=5,method='predict_proba')[:,1]
    lr.fit(Xd,dev.y); t=lr.predict_proba(Xt)[:,1]
    res.append([en,'数据学习的方向（AI 标签训练）','mean-emb',round(roc_auc_score(dev.y,cv),3),round(roc_auc_score(test.y,t),3)]); store[(en,'learned','x')]=t
R=pd.DataFrame(res,columns=['词向量','种子词','合成方式','dev AUC（AI 标签）','test AUC（人工标签 112 条）'])
print(R.to_string()); R.to_csv('axis_variants.csv',index=False)
best=R.iloc[R['dev AUC（AI 标签）'].idxmax()]; print('CHOSEN BY DEV:',best.to_dict())
# bootstrap CI on test for chosen and baseline
key=(best['词向量'],'learned','x') if best['种子词'].startswith('数据') else (best['词向量'],best['种子词'],best['合成方式'])
rng=np.random.default_rng(5342); y=test.y.values
for nm,k in [('baseline',('GoogleNews','原种子词','mean')),('chosen',key)]:
    s=np.asarray(store[k]); b=[]
    for _ in range(2000):
        i=rng.integers(0,len(y),len(y))
        if y[i].min()!=y[i].max(): b.append(roc_auc_score(y[i],s[i]))
    print(nm,k,round(roc_auc_score(y,s),3),np.percentile(b,[2.5,97.5]).round(3))
    off_m=test.uid.str.startswith('M2M3').values
    print('  official subset',off_m.sum(),round(roc_auc_score(y[off_m],s[off_m]),3))
s=np.asarray(store[key]); nonoff=~test.uid.str.startswith('M2M3').values
print('chosen non-official subset',nonoff.sum(),round(roc_auc_score(y[nonoff],s[nonoff]),3))
b=[]
for _ in range(2000):
    i=rng.choice(np.where(nonoff)[0],nonoff.sum())
    if y[i].min()!=y[i].max(): b.append(roc_auc_score(y[i],s[i]))
print(' CI',np.percentile(b,[2.5,97.5]).round(3))
wv=KeyedVectors.load('/tmp/claude-0/wv/gn500k.kv')
Xd=np.vstack(dev.text.apply(lambda t:emb(wv,t))); lr=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced').fit(Xd,dev.y)
allM=M[M.text_en.notna()]; X=np.vstack(allM.text_en.apply(lambda t:emb(wv,t)))
out=pd.DataFrame({'uid':allM.index,'dataset':allM.dataset,'h_learned':lr.predict_proba(X)[:,1].round(4)}); out.to_csv('heritage_learned_scores.csv',index=False)
np.save('heritage_learned_direction.npy',lr.coef_[0]); print('scored',len(out))
