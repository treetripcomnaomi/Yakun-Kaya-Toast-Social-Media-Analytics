import os,warnings; warnings.filterwarnings('ignore')
os.chdir('/tmp/claude-0/rq'); exec(open('/tmp/claude-0/sent/roberta.py').read().split('P=pd.Series')[0])
torch.set_num_threads(os.cpu_count())
r=pd.read_csv(U+'RQ2_逐条_1103.csv'); w=pd.read_csv('/tmp/claude-0/s45/step4_30d_rows.csv'); ind=pd.read_csv('/tmp/claude-0/s45/industry_sentiment_AI.csv')
sets={'Ya Kun，30 天':r[r.uid.isin(w[w.grp=='client'].uid)].uid,'行业，30 天':ind[ind.in30].uid,'Ya Kun，全部':r.uid,'行业，随机 200':ind[~ind.in30].uid}
allu=pd.concat(sets.values()).drop_duplicates()
pr={u:pred(M.text_en.get(u,'')) for u in allu}
rows=[]
for nm,s in sets.items():
    v=pd.Series([pr[u] for u in s]).value_counts(normalize=True)*100
    rows.append([nm,len(s)]+[round(v.get(c,0),1) for c in 'PUN'])
T=pd.DataFrame(rows,columns=['组','n','正面%','中性%','负面%']); print(T.to_string()); T.to_csv('/tmp/claude-0/sent/step4_roberta.csv',index=False)
a=r.set_index('uid').F_sentiment.map({'F1':'P','F2':'U','F3':'N','F4':'M'}); rb=pd.Series(pr)
m=a.reindex(rb.index).isin(['P','U','N']); from sklearn.metrics import cohen_kappa_score as k
print('AI vs RoBERTa on Ya Kun all',int(m.sum()),round(k(a.reindex(rb.index)[m],rb[m]),2))
