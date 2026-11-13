import pandas as pd,numpy as np
from sklearn.metrics import cohen_kappa_score as k
P='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
d=pd.read_csv('/tmp/claude-0/rq/heritage_valid_rows.csv')
ai=pd.concat([pd.read_csv(P+f)[['uid','B_heritage']] for f in ['ai_precode_yakun_official.csv','ai_precode_competitor87.csv','ai_precode_user_content.csv']])
ai['aiH']=ai.B_heritage.fillna('H0').astype(str).str.contains(r'H[1-5]').astype(int)
x=d.merge(ai,on='uid')
print('overlap',len(x)); print(x.groupby('dataset').size())
def ac1(a,b):
    pa=(a==b).mean(); p=(a.mean()+b.mean())/2; pe=2*p*(1-p); return (pa-pe)/(1-pe)
for lab,col in [('Coder_A','A'),('Coder_B','B')]:
    a,b=x[col].astype(int),x.aiH
    print(lab,'vs AI: n',len(x),'agree',round((a==b).mean(),2),'kappa',round(k(a,b),2),'AC1',round(ac1(a,b),2))
a,b=x.A.astype(int),x.B.astype(int); print('A vs B same items',round(k(a,b),2))
print(x[['dataset','A','B','aiH','B_heritage']].to_string())
