import pandas as pd, numpy as np
U='/mnt/user-data/uploads/文稿:YaKun_vMFD/'
d=pd.read_csv(U+'analysis_outputs/master_scored.csv',low_memory=False)
d['dt']=pd.to_datetime(d.published_date,errors='coerce',utc=True).dt.tz_localize(None).dt.normalize()
ug=d[d.content_type!='official_post']
print('author types non-official:',ug.author_type.value_counts().to_dict())
keep=ug.author_type.isin(['user','creator','ordinary_user'])
ug=ug[keep & (ug.dataset!='M7 Brand24')].copy()
ug['grp']=np.where(ug.yakun_related,'client','industry' )
ug=ug[ug.yakun_related|ug.industry]
S,E=pd.Timestamp('2026-09-25'),pd.Timestamp('2026-10-24')
w=ug[(ug.dt>=S)&(ug.dt<=E)]
print('30d window',S.date(),E.date()); print(pd.crosstab(w.dataset,w.grp,margins=True))
print(pd.crosstab(w.grp,w.vader_label,normalize='index').round(3), pd.crosstab(w.grp,w.vader_label))
print('ALL TIME'); print(pd.crosstab(ug.grp,ug.vader_label,normalize='index').round(3)); print(ug.grp.value_counts())
# latest date per dataset
print(ug.groupby('dataset').dt.max())
b=d[d.dataset=='M7 Brand24']; print('brand24',len(b),b.author_type.value_counts().to_dict(),b.brand24_sentiment.value_counts().to_dict())
w.to_csv('step4_30d_rows.csv',index=False); ug.to_csv('step4_all_rows.csv',index=False)
