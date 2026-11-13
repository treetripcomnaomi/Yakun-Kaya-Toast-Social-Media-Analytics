import openpyxl,pandas as pd,re
R='/mnt/user-data/outputs/returned_1103/'
def load(f,s):
    rows=list(openpyxl.load_workbook(R+f,read_only=True,data_only=True)[s].iter_rows(values_only=True))
    h=list(rows[1]); return pd.DataFrame([r[:len(h)] for r in rows[2:] if r and r[0] and str(r[0]).startswith('M')],columns=h).set_index(h[0])
is1=lambda v:1 if str(v).strip() in('1','1.0') else 0
def codes(D):
    o=pd.DataFrame(index=D.index); o['brand']=D['品牌']; o['platform']=D['平台']; o['eng']=D['互动数']; o['P2']=D['P2 主题（单选）']
    for c in D.columns:
        m=re.match(r'^(H[1-5]|Y[1-6]) ',str(c))
        if m: o[m.group(1)]=D[c].apply(is1)
    o['anyH']=o[[f'H{i}' for i in range(1,6)]].max(axis=1); o['anyY']=o[[f'Y{i}' for i in range(1,7)]].max(axis=1)
    o['H1|H4']=o[['H1','H4']].max(axis=1); o['Y2|Y6']=o[['Y2','Y6']].max(axis=1)
    return o
out=[]
for tab,s,a,b in [('S5','S5_竞品前30帖',5,3),('S3','S3_YaKun前20帖',4,5)]:
    A=codes(load(f'coding_v2_组员{a}.xlsx',s)); B=codes(load(f'coding_v2_组员{b}.xlsx',s)).reindex(A.index)
    print(tab,len(A))
    for v in ['anyH','H1|H4','H3','H4','H5','anyY','Y1','Y2','Y3','Y6']:
        both=(A[v]&B[v]); either=(A[v]|B[v])
        g=pd.DataFrame({'brand':A.brand,'both':both,'either':either}).groupby('brand').agg(n=('both','size'),both=('both','sum'),either=('either','sum'))
        for br,r in g.iterrows(): out.append([tab,br,v,r.n,r.both,r.either])
    print(pd.crosstab(A.brand,A.platform))
T=pd.DataFrame(out,columns=['表','品牌','变量','n','两人都选','任一人选'])
T['范围']=T.apply(lambda r:f"{r.两人都选}–{r.任一人选}/{r.n}",axis=1)
print(T.pivot_table(index='变量',columns='品牌',values='范围',aggfunc='first').to_string())
