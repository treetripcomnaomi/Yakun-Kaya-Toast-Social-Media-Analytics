import openpyxl,pandas as pd,numpy as np,sys
sys.path.insert(0,'/tmp/claude-0/rq')
from sklearn.metrics import cohen_kappa_score as k, roc_auc_score as auc
from scipy.stats import spearmanr
wb=openpyxl.load_workbook('/mnt/user-data/outputs/returned_1103/heritage_labeling_v2_AB.xlsx',data_only=True)
def sh(s):
    r=list(wb[s].iter_rows(min_row=2,values_only=True)); return pd.DataFrame([x[:5] for x in r if x[0] is not None],columns=['编号','平台','文本','h','备注']).set_index('编号')
A,B=sh('Coder_A'),sh('Coder_B')
key=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/heritage_labeling_key_v2.csv').set_index('编号')
D=key.join(A[['h','备注']].rename(columns={'h':'A','备注':'noteA'})).join(B[['h','备注']].rename(columns={'h':'B','备注':'noteB'}))
print('blank A',D.A.isna().sum(),'blank B',D.B.isna().sum())
print(D[[c for c in ['noteA','noteB'] ]].dropna(how='all'))
d=D.dropna(subset=['A','B'])
x,y=d.A.astype(int),d.B.astype(int)
pa=(x==y).mean(); p=(x.mean()+y.mean())/2; pe=2*p*(1-p); ac1=(pa-pe)/(1-pe)
print(f'n={len(d)} 一致率={pa:.2f} kappa={k(x,y):.2f} AC1={ac1:.2f}  A=1:{x.sum()} B=1:{y.sum()}')
d=d.assign(both=((x==1)&(y==1)).astype(int), either=((x==1)|(y==1)).astype(int), agree=(x==y))
m=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/master_scored.csv',low_memory=False).set_index('uid')
d=d.join(m[['h_strength','h_ambivalence']],on='uid')
for lab,sub,yv in [('两人一致的条目（主检验）',d[d.agree],'A'),('任一人=1',d,'either'),('两人都=1',d,'both')]:
    for s in ['h_valence','h_strength']:
        print(lab,s,'n=',len(sub),'AUC=',round(auc(sub[yv].astype(int),sub[s]),3))
ag=d[d.agree]
print(ag.groupby('A').h_valence.describe())
print(ag.groupby(['dataset','A']).size().unstack())
for ds,g in ag.groupby('dataset'):
    if g.A.nunique()>1: print(ds,len(g),round(auc(g.A.astype(int),g.h_valence),2))
d.to_csv('/tmp/claude-0/rq/heritage_valid_rows.csv',encoding='utf-8-sig')
