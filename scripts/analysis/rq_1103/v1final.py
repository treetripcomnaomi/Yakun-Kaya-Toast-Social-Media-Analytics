import sys; sys.path.insert(0,'/tmp/claude-0/rq')
exec(open('lib.py').read())
s='V1_官方帖50'
HA=human_vars(load('coding_v2_组员5.xlsx',s)); HB=human_vars(load('coding_v2_组员2.xlsx',s)).reindex(HA.index)
Y=[f'Y{i}' for i in range(1,7)]
F=pd.read_excel('/mnt/user-data/attachments/3d0b6125-65cb-5da2-8a82-53c83af33aed/a405a1af-V1_________5__2.xlsx',sheet_name='分歧条目')
F=F[F['序号']!='示例'].set_index('uid（勿改）')
cmap={'Y1':'Y1 潮流形式（定稿）','Y2':'Y2 联名（定稿）','Y3':'Y3 新品/新口味（定稿）','Y4':'Y4 周边（定稿）','Y5':'Y5 创作者/名人（定稿）','Y6':'Y6 互动玩法（定稿）'}
C=HA[Y].copy()
for u in C.index:
    if u in F.index:
        for y in Y: C.loc[u,y]=1 if str(F.loc[u,cmap[y]]).strip() in('1','1.0') else 0
    else:
        assert (HA.loc[u,Y].values==HB.loc[u,Y].values).all(), u
print('consensus n',len(C),'overrides',C.index.isin(F.index).sum())
C.to_csv('V1_youth_final.csv')
A=pd.read_csv(AI+'ai_precode_yakun_official.csv').set_index('uid'); AIv=ai_vars(A,set(Y)).reindex(C.index)
def comb(D,cs): return (D[cs].sum(axis=1)>0).astype(int)
rows=[]
tests={**{y:[y] for y in Y},'任何新潮手法 Y1–Y6':Y,'Y2|Y6':['Y2','Y6'],'Y2|Y3|Y6':['Y2','Y3','Y6'],'Y2|Y4|Y5|Y6':['Y2','Y4','Y5','Y6'],'Y2|Y3|Y4':['Y2','Y3','Y4']}
for n,cs in tests.items():
    a,b=comb(C,cs),comb(AIv,cs)
    kk=k(a,b) if len(set(a)|set(b))>1 else float('nan')
    rows.append([n,int(a.sum()),int(b.sum()),round((a==b).mean(),2),round(kk,2),round(ac1(a,b),2)])
print(pd.DataFrame(rows,columns=['变量','定稿=1','AI=1','一致率','kappa','AC1']).to_string(index=False))
