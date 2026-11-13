import pandas as pd, numpy as np, re, warnings; warnings.filterwarnings('ignore')
exec(open('run.py').read().split("allM=M[M.text_en.notna()]")[0])
from sklearn.linear_model import LogisticRegression
allM=M[M.text_en.notna()]
Xd=np.vstack([emb(M.text_en[u]) for u in dev.uid]); yd=dev.y.values
lr=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced').fit(Xd,yd); w=lr.coef_[0]
S=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/seed_words_v1.csv'); print(S.columns.tolist(), S.status.value_counts().to_dict() if 'status' in S else '')
S=S[S.status=='keep'] if 'status' in S else S
H=[x for x in S[S.side=='heritage'].word if x in wv]; N=[x for x in S[S.side=='novelty'].word if x in wv]
u=lambda x: wv[x]/np.linalg.norm(wv[x])
ax=np.mean([u(x) for x in H],0)-np.mean([u(x) for x in N],0)
# reference vocab for z-scoring: words appearing in our corpus
from collections import Counter
cnt=Counter(t for txt in allM.text_en for t in toks(txt) if t in wv)
vocab=[t for t,c in cnt.items() if c>=5]; V=np.vstack([u(t) for t in vocab])
old_all=V@ax/np.linalg.norm(ax); new_all=V@w
def z(v,arr): return (v-arr.mean())/arr.std()
words=H[:8]+N[:7]+['kaya','kopi','toast','coffee','breakfast','hawker','singapore','uncle','grandma','family','hometown','kopitiam','egg','soya','adidas','merch','airport','nanyang','hainanese']
rows=[]
for t in words:
    if t not in wv: print('missing',t); continue
    g='heritage seed' if t in H else ('novelty seed' if t in N else 'our data')
    rows.append((t,g,z(u(t)@ax/np.linalg.norm(ax),old_all),z(u(t)@w,new_all),cnt.get(t,0)))
R=pd.DataFrame(rows,columns=['word','group','v1_seed_axis_z','learned_axis_z','freq_in_our_data']).round(2)
print(R.sort_values('learned_axis_z',ascending=False).to_string())
R.to_csv('word_positions.csv',index=False)
# top words learned (frequent in our data)
s=pd.Series(new_all,index=vocab); f=pd.Series(cnt)
top=s[f[s.index]>=20].sort_values()
print('TOP heritage-side:',top.tail(25).index.tolist()); print('TOP novelty-side:',top.head(25).index.tolist())

zs=pd.Series(z(new_all,new_all),index=vocab); zo=pd.Series(z(old_all,old_all),index=vocab)
ok=f[zs.index]>=20
hi=zs[ok].sort_values().tail(15)[::-1]; lo=zs[ok].sort_values().head(15)
pd.DataFrame({'word':list(hi.index)+list(lo.index),'side':['heritage']*15+['other']*15,'learned_z':list(hi.values)+list(lo.values),'v1_z':[zo[w_] for w_ in list(hi.index)+list(lo.index)],'freq':[cnt[w_] for w_ in list(hi.index)+list(lo.index)]}).round(2).to_csv('learned_top_words.csv',index=False)
mv=['egg','breakfast','family','uncle','hawker','coffee','airport','merch']
pd.DataFrame({'word':mv,'v1':[zo[m] for m in mv],'learned':[zs[m] for m in mv],'freq':[cnt[m] for m in mv]}).round(2).to_csv('moved_words.csv',index=False)
print(open('learned_top_words.csv').read()); print(open('moved_words.csv').read())
