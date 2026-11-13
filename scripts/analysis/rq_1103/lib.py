import openpyxl, pandas as pd, numpy as np, re
from sklearn.metrics import cohen_kappa_score as k
R='/mnt/user-data/outputs/returned_1103/'; AI='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
def load(f,s):
    rows=list(openpyxl.load_workbook(R+f,read_only=True,data_only=True)[s].iter_rows(values_only=True))
    h=list(rows[1]); return pd.DataFrame([r[:len(h)] for r in rows[2:] if r and r[0] and r[0]!='示例'],columns=h).set_index(h[0])
def ac1(x,y):
    x,y=list(map(str,x)),list(map(str,y)); cats=sorted(set(x)|set(y)); q=max(len(cats),2); n=len(x)
    pa=np.mean([a==b for a,b in zip(x,y)]); pi=[(x.count(c)+y.count(c))/(2*n) for c in cats]; pe=sum(p*(1-p) for p in pi)/(q-1)
    return (pa-pe)/(1-pe) if pe<1 else np.nan
is1=lambda v: 1 if str(v).strip() in('1','1.0') else 0
S_MAP={'S1':'S4','S2':'S2','S3':'S1','S4':'S3'}; F_MAP={'F1':'F1','F2':'F3','F3':'F4','F4':'F2'}
def human_vars(D,remap=False):
    out=pd.DataFrame(index=D.index)
    for c in D.columns:
        m=re.match(r'^(H[1-5]|Y[1-6]|N[1-6]) ',str(c))
        if m: out[m.group(1)]=D[c].apply(is1)
    for c,key in [('A1 相关性','A1'),('A2 来源','A2'),('A3 商业披露','A3'),('E 老派看法','E'),('F 情感','F')]:
        if c in D: out[key]=D[c]
    if remap: out['A2']=out['A2'].map(S_MAP); out['F']=out['F'].map(F_MAP)
    if 'SC 豆浆咖啡' in D: out['SC']=D['SC 豆浆咖啡'].apply(is1)
    return out
def ai_vars(A,cols):
    out=pd.DataFrame(index=A.index)
    for src,pre,n in [('B_heritage','H',5),('C_youth','Y',6),('D_draws','N',6)]:
        if src in A:
            for i in range(1,n+1): out[f'{pre}{i}']=A[src].fillna('').astype(str).str.contains(fr'\b{pre}{i}\b').astype(int)
    for src,key in [('A1_relevance','A1'),('A2_source','A2'),('A3_disclosure','A3'),('E_dated','E'),('F_sentiment','F'),('SC_soya_coffee','SC')]:
        if src in A: out[key]=A[src]
    if 'E' in out: out['E']=out['E'].where(out['E'].isin(['D0','D1']))
    return out[[c for c in out if c in cols]]
def add_merged(D):
    for pre,name in [('H','any H（有 heritage）'),('Y','any Y（有年轻化手法）'),('N','any N（有非 heritage 吸引点）')]:
        cs=[c for c in D if re.fullmatch(pre+r'\d',c)]
        if cs: D[name]=(D[cs].sum(1)>0).astype(int)
    return D
def compare(X,Y,lab,tab,rows):
    idx=X.index.intersection(Y.index)
    for c in X.columns:
        if c not in Y: continue
        x,y=X.loc[idx,c],Y.loc[idx,c]; m=x.notna()&y.notna()&(x.astype(str)!='None')&(y.astype(str)!='None'); x,y=x[m].astype(str),y[m].astype(str)
        if c in('A2','A3','E','F') and 'A1' in X:   # R0 条目不编后续
            keep=(X.loc[x.index,'A1'].astype(str)!='R0')&(Y.loc[x.index,'A1'].astype(str)!='R0'); x,y=x[keep],y[keep]
        if len(x)<5: continue
        kk=k(x,y) if len(set(x)|set(y))>1 else np.nan
        rows.append([tab,lab,c,len(x),round((x.values==y.values).mean(),2),None if kk!=kk else round(kk,2),round(ac1(x,y),2)])
rows=[]
cfg=[('V1','V1_官方帖50',5,2,'ai_precode_yakun_official.csv'),('V2','V2_竞品30',3,4,'ai_precode_competitor87.csv'),('V3','V3_用户内容60',5,1,'ai_precode_user_content.csv')]
