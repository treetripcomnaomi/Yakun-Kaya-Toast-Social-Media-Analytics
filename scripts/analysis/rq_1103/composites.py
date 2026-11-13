import sys; sys.path.insert(0,'/tmp/claude-0/rq')
import os; FILT=os.environ.get("FILT")=="1"
from lib import *
combos={'H1|H4':['H1','H4'],'H1|H4|H5':['H1','H4','H5'],'H1|H2|H4':['H1','H2','H4'],'Y2|Y6':['Y2','Y6'],'Y2|Y3':['Y2','Y3'],'Y2|Y3|Y6':['Y2','Y3','Y6'],'Y2|Y4|Y5|Y6':['Y2','Y4','Y5','Y6'],'H4|H5':['H4','H5'],'anyH':['H1','H2','H3','H4','H5'],'anyY':['Y1','Y2','Y3','Y4','Y5','Y6']}
def addc(D):
    for n,cs in combos.items():
        cs=[c for c in cs if c in D]
        if cs: D[n]=(D[cs].sum(axis=1)>0).astype(int)
    return D[[c for c in combos if c in D]]
cfg=[('V1','V1_官方帖50',5,2,'ai_precode_yakun_official.csv'),('V2','V2_竞品30',3,4,'ai_precode_competitor87.csv'),('V3','V3_用户内容60',5,1,'ai_precode_user_content.csv')]
rows=[]
for tab,s,a,b,f in cfg:
    HA=human_vars(load(f'coding_v2_组员{a}.xlsx',s),remap=(a==1)); HB=human_vars(load(f'coding_v2_组员{b}.xlsx',s),remap=(b==1))
    coded=lambda D:D.apply(lambda r:any(str(v) not in('0','None','nan') for v in r),axis=1)
    HA,HB=(HA[coded(HA)],HB[coded(HB)]) if FILT else (HA,HB)
    A=pd.read_csv(AI+f).set_index('uid'); AIv=ai_vars(A,set(HA.columns))
    HA,HB,AIv=addc(HA),addc(HB),addc(AIv)
    compare(HA,HB,'人vs人',tab,rows); compare(HA,AIv,f'组员{a}vsAI',tab,rows); compare(HB,AIv,f'组员{b}vsAI',tab,rows)
D=pd.DataFrame(rows,columns=['表','对比','变量','n','一致率','kappa','AC1'])
pd.set_option('display.width',250)
print(D.pivot_table(index=['表','变量'],columns='对比',values=['kappa','AC1'],aggfunc='first').to_string())
