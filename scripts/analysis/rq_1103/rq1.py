import pandas as pd,numpy as np
from scipy.stats import kruskal, spearmanr, mannwhitneyu
P='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
a=pd.read_csv(P+'ai_precode_yakun_official.csv'); m=pd.read_csv(P+'master_scored.csv',low_memory=False)
d=a.merge(m[['uid','platform','published_date','likes','comments','shares','saves','views','engagement','h_valence','h_reliable']],on='uid',how='left')
has=lambda s,codes: s.fillna('').astype(str).apply(lambda x:any(c in x.replace(' ','').split(';') for c in codes))
d['Hs']=has(d.B_heritage,['H1','H4']); d['Ys']=has(d.C_youth,['Y2','Y6'])
d['Ha']=has(d.B_heritage,['H1','H2','H3','H4','H5']); d['Ya']=has(d.C_youth,['Y1','Y2','Y3','Y4','Y5','Y6'])
def typ(h,y): return np.select([h&~y,h&y,~h&y],['纯传统','重新诠释','纯年轻化'],'都没有')
d['type_s']=typ(d.Hs,d.Ys); d['type_a']=typ(d.Ha,d.Ya)
d['year']=pd.to_datetime(d.published_date).dt.year
print(d.platform.value_counts(), d.engagement.isna().sum())
ig=d[(d.platform=='Instagram')&d.engagement.notna()].copy()
print('IG n',len(ig), ig.published_date.min(), ig.published_date.max())
order=['纯传统','重新诠释','纯年轻化','都没有']
for t in ['type_s','type_a']:
    g=ig.groupby(t).engagement.agg(['count','median','mean']).reindex(order).round(0); print(t);print(g)
    print('KW p=',kruskal(*[x.engagement for _,x in ig.groupby(t)]).pvalue)
# control year: median within year
print(ig.groupby(['year','type_s']).engagement.agg(['count','median']).unstack())
# year-normalised: engagement / median of that year
ig['rel']=ig.engagement/ig.groupby('year').engagement.transform('median')
g=ig.groupby('type_s').rel.agg(['count','median']).reindex(order).round(2); print('年内相对互动 strict');print(g, kruskal(*[x.rel for _,x in ig.groupby('type_s')]).pvalue)
for c in ['Hs','Ys']:
    x,y=ig[ig[c]].rel,ig[~ig[c]].rel; print(c,'有',len(x),round(x.median(),2),'无',len(y),round(y.median(),2),'MWU p',round(mannwhitneyu(x,y).pvalue,4))
# single codes
for code,col in [('H1','B_heritage'),('H4','B_heritage'),('Y2','C_youth'),('Y6','C_youth')]:
    f=has(ig[col],[code]); print(code,f.sum(),round(ig[f].rel.median(),2),round(ig[~f].rel.median(),2),round(mannwhitneyu(ig[f].rel,ig[~f].rel).pvalue,4))
# topic P2
print(ig.groupby('P2').agg(n=('rel','size'),rel_med=('rel','median'),eng_med=('engagement','median')).sort_values('rel_med',ascending=False).round(2))
# h_valence corr
r=ig[ig.h_reliable==True]; print('spearman h_valence vs rel',len(r),spearmanr(r.h_valence,r.rel))
# collab periods
ig['pd']=pd.to_datetime(ig.published_date)
for lab,s,e in [('adidas 2024-08','2024-08-01','2024-08-31'),('Fullerton SG60 2025-07','2025-07-01','2025-07-31')]:
    w=ig[(ig.pd>=s)&(ig.pd<=e)]; print(lab,len(w), w[['published_date','type_s','engagement','rel']].to_string())
# tiktok
tt=d[d.platform=='TikTok']; print('TikTok',len(tt)); print(tt.groupby('type_s').engagement.agg(['count','median']))
d.to_csv('/tmp/claude-0/rq/rq1_rows.csv',index=False,encoding='utf-8-sig')
