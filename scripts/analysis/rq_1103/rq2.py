import pandas as pd,numpy as np
from scipy.stats import chi2_contingency
P='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
u=pd.read_csv(P+'ai_precode_user_content.csv'); o=pd.read_csv(P+'ai_precode_yakun_official.csv')
sp=lambda s:s.fillna('').astype(str).str.replace(' ','').str.split(';')
for i in range(1,6):
    u[f'H{i}']=sp(u.B_heritage).apply(lambda x:f'H{i}' in x); o[f'H{i}']=sp(o.B_heritage).apply(lambda x:f'H{i}' in x)
for i in range(1,7): u[f'N{i}']=sp(u.D_draws).apply(lambda x:f'N{i}' in x)
H=[f'H{i}' for i in range(1,6)]; N=[f'N{i}' for i in range(1,7)]
u['anyH']=u[H].any(axis=1); o['anyH']=o[H].any(axis=1)
excl=['suspected_bot','commercial_listing','promo_site','travel_site','news_media']
b=u[u.A1_relevance.isin(['R1','R2'])&~u.author_type.isin(excl)].copy()
print('base n',len(b),' (R1/R2', u.A1_relevance.isin(['R1','R2']).sum(),')')
print('anyH share',round(b.anyH.mean()*100,1), b.anyH.sum())
t=b.groupby('dataset').agg(n=('anyH','size'),heritage_pct=('anyH','mean')); t['heritage_pct']=(t.heritage_pct*100).round(1); print(t)
print('meaning % of all base:',(b[H].mean()*100).round(1).to_dict())
hb=b[b.anyH]; ho=o[o.anyH]
cmp=pd.DataFrame({'用户_含heritage中占比':(hb[H].mean()*100).round(1),'品牌_含heritage中占比':(ho[H].mean()*100).round(1),'用户_n':hb[H].sum(),'品牌_n':ho[H].sum()}); print('users heritage n',len(hb),'brand heritage n',len(ho),'brand anyH share',round(o.anyH.mean()*100,1)); print(cmp)
print('non-heritage draws % base:',(b[N].mean()*100).round(1).to_dict())
print('E D1',(b.E_dated=='D1').sum(),'of',b.E_dated.isin(['D0','D1']).sum())
print('F',(b.F_sentiment.value_counts(normalize=True)*100).round(1).to_dict())
print('SC',b.SC_soya_coffee.sum(), round(b.SC_soya_coffee.mean()*100,1))
print('PR among N1',b[b.N1].PR_price_ref.value_counts(dropna=False).to_dict(),'N1 n',b.N1.sum())
sc=b[b.SC_soya_coffee==1]; print('SC F',sc.F_sentiment.value_counts().to_dict(),'SC N1',sc.N1.sum(),'SC PR',sc.PR_price_ref.value_counts().to_dict())
print('F by anyH'); print(pd.crosstab(b.anyH,b.F_sentiment,normalize='index').round(3)*100)
b.to_csv('rq2_rows.csv',index=False,encoding='utf-8-sig')
