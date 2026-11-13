import pandas as pd,numpy as np
from scipy.stats import kruskal,mannwhitneyu,chi2_contingency
ones=set(int(x) for x in open('ai_off_labels.txt').read().split())
k=pd.read_csv('off_key.csv'); k['Hbin']=k.k.isin(ones).astype(int)
m=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/master_scored.csv',low_memory=False)
k=k.merge(m[['uid','engagement','views','likes','comments','text_en']],on='uid',how='left')
k['pd']=pd.to_datetime(k.published_date); k['win6']=(k.pd>='2026-04-25')&(k.pd<='2026-10-18')
k.to_csv('heritage_binary_official.csv',index=False,encoding='utf-8-sig')
w=k[k.win6]
t=w.groupby(['brand','platform']).Hbin.agg(['size','sum','mean']); t['mean']=(t['mean']*100).round(1); print('6个月窗口'); print(t)
t2=w.groupby('brand').Hbin.agg(['size','sum','mean']); t2['mean']=(t2['mean']*100).round(1); print(t2)
ct=pd.crosstab(w.brand,w.Hbin); print('chi2 p',chi2_contingency(ct)[1])
# National Day share of heritage posts (Jul-Aug) per brand
w2=w.assign(nd=w.pd.dt.month.isin([7,8]))
print(w2.groupby(['brand','nd']).Hbin.agg(['size','mean']).round(2))
print('non-Jul/Aug heritage share'); print(w2[~w2.nd].groupby('brand').Hbin.agg(['size','mean']).round(3))
# engagement within brand IG 6mo: heritage vs not
for b,g in w[w.platform=='Instagram'].groupby('brand'):
    a,c=g[g.Hbin==1].engagement.dropna(),g[g.Hbin==0].engagement.dropna()
    if len(a)>2 and len(c)>2: print(b,'IG heritage med',a.median(),len(a),'non',c.median(),len(c),'p',round(mannwhitneyu(a,c).pvalue,3))
# Ya Kun all-time
y=k[k.brand=='Ya Kun']; print('Ya Kun all',len(y),y.Hbin.sum(),round(y.Hbin.mean()*100,1))
# RQ1 with binary heritage
r=pd.read_csv('rq1_rows.csv').merge(k[['uid','Hbin']],on='uid')
ig=r[r.platform=='Instagram'].copy(); ig['rel']=ig.engagement/ig.groupby('year').engagement.transform('median')
ig['type_b']=np.select([(ig.Hbin==1)&~ig.Ys,(ig.Hbin==1)&ig.Ys,(ig.Hbin==0)&ig.Ys],['纯传统','重新诠释','纯年轻化'],'都没有')
g=ig.groupby('type_b').agg(n=('rel','size'),eng_med=('engagement','median'),eng_mean=('engagement','mean'),rel_med=('rel','median')).round(2); print(g)
print('KW',kruskal(*[x.rel for _,x in ig.groupby('type_b')]).pvalue)
a,c=ig[ig.Hbin==1].rel,ig[ig.Hbin==0].rel; print('Hbin yes',len(a),round(a.median(),2),'no',len(c),round(c.median(),2),'p',mannwhitneyu(a,c).pvalue)
print('agreement Hbin vs old AI anyH on YaKun:', pd.crosstab(ig.Hbin,ig.Ha))
ig.to_csv('rq1_rows_v2.csv',index=False,encoding='utf-8-sig')
