import sys; sys.path.insert(0,'/tmp/claude-0/rq'); exec(open('lib.py').read())
import re
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment
P2S="T-NEW,T-PROMO,T-FEST,T-HERITAGE,T-COLLAB,T-STORE,T-COMMUNITY,T-OTHER"
VARS=['P2','CTA-Q','CTA-TAG','CTA-GIVE','CTA-LINK','CTA-NONE','H1','H2','H3','H4','H5','H0','Y1','Y2','Y3','Y4','Y5','Y6','Y0']
NAMES={'P2':'P2 主题','CTA-Q':'CTA-Q 提问','CTA-TAG':'CTA-TAG @朋友','CTA-GIVE':'CTA-GIVE 抽奖','CTA-LINK':'CTA-LINK 链接/App/到店','CTA-NONE':'CTA-NONE 无号召','H1':'H1 创始历史','H2':'H2 传统工艺','H3':'H3 个人/家庭记忆','H4':'H4 新加坡身份','H5':'H5 kopitiam文化','H0':'H0 无heritage','Y1':'Y1 潮流形式','Y2':'Y2 联名','Y3':'Y3 新品/新口味','Y4':'Y4 周边/盲盒','Y5':'Y5 创作者/名人','Y6':'Y6 互动玩法','Y0':'Y0 无年轻化'}
def vars_(D):
    out={}
    for c in D.columns:
        code=str(c).split(' ')[0]
        if code=='P2': out['P2']=D[c].apply(lambda v:'' if v is None else str(v))
        elif code in VARS: out[code]=D[c].apply(is1)
    return pd.DataFrame(out,index=D.index)
f=Font(name='Arial',size=11); fb=Font(name='Arial',size=11,bold=True)
yel=PatternFill('solid',start_color='FFF2CC'); grey=PatternFill('solid',start_color='E7E6E6')
for sheet,(fa,na),(fb_,nb),out,who in [
  ('S3_YaKun前20帖',('coding_v2_组员4.xlsx','组员4'),('coding_v2_组员5.xlsx','组员5'),'S3_分歧裁定_组员4组员5.xlsx','组员4 和组员5'),
  ('S5_竞品前30帖',('coding_v2_组员5.xlsx','组员5'),('coding_v2_组员3.xlsx','组员3'),'S5_分歧裁定_组员5组员3.xlsx','组员5 和组员3')]:
    A=load(fa,sheet);B=load(fb_,sheet);VA,VB=vars_(A),vars_(B)
    txt=[c for c in A.columns if '文案' in str(c)][0]
    wb=openpyxl.Workbook(); ws=wb.active; ws.title='说明'
    nd=sum(1 for u in A.index for v in VARS if str(VA.loc[u,v])!=str(VB.loc[u,v]))
    info=[('这是什么',f'Step 3/5 老师必交的人工编码（{sheet}），{who}两人的最终裁定表。共 {len(A)} 条，{nd} 个格子两人编得不一样。'),
    ('为什么要做','老师要「主题 × 平均互动」表和 3 条洞察，需要每条帖一个最终编码。两人一致的格子已经填好（灰色），只需要讨论黄色格子。信度（κ）用的是讨论前的原始编码，已经算好，裁定不会改变 κ。'),
    ('怎么做','两人一起看「裁定」页：每行先看「分歧在哪」那一列，再读文案、点链接看原帖，按编码手册定义在黄色格子里定一个答案。1 = 有，留空 = 没有；P2 主题从下拉里选一个。最后在「理由」写一句。'),
    ('规则','只按定义判断，不按原来谁填的；讨论不出结果的写「仍有分歧」。不要改灰色格子和 coding_v2 原文件。这一步规定必须由组员人工完成，Claude 不参与裁定。'),
    ('交回',f'存成 {out.replace(".xlsx","_定稿.xlsx")}，传回 Drive「组员交件」。'),
    ('',''),('P2 主题代码（完整定义见编码手册）','T-NEW 新品 · T-PROMO 促销优惠 · T-FEST 节日 · T-HERITAGE 传统/品牌故事 · T-COLLAB 联名 · T-STORE 门店 · T-COMMUNITY 社区/公益 · T-OTHER 其他'),
    ('每行至少一个','H 列至少一个 1（不沾 heritage 就 H0）；Y 列同理（Y0）；CTA 列同理（CTA-NONE）。')]
    for r in info: ws.append(list(r))
    for row in ws.iter_rows():
        for c in row: c.font=f; c.alignment=Alignment(wrap_text=True,vertical='top')
    for r in range(1,ws.max_row+1): ws.cell(r,1).font=fb
    ws.column_dimensions['A'].width=24; ws.column_dimensions['B'].width=100
    d=wb.create_sheet('裁定')
    base=['序号','uid（勿改）','品牌','平台','链接','互动数','文案','分歧在哪']
    d.append(base+[NAMES[v] for v in VARS]+['理由'])
    for c in d[1]: c.font=fb; c.alignment=Alignment(wrap_text=True,vertical='top')
    dv1=DataValidation(type='list',formula1='"1"',allow_blank=True); dvp=DataValidation(type='list',formula1=f'"{P2S}"',allow_blank=True)
    d.add_data_validation(dv1); d.add_data_validation(dvp)
    for i,u in enumerate(A.index,1):
        diffs=[]; vals=[]
        for v in VARS:
            a,b=VA.loc[u,v],VB.loc[u,v]
            if str(a)!=str(b):
                sh=lambda x: (x or '空') if v=='P2' else ('1' if x==1 else '空')
                diffs.append(f'{NAMES[v]}：{na}={sh(a)} / {nb}={sh(b)}'); vals.append(None)
            else: vals.append(a if v=='P2' else (1 if a==1 else None))
        d.append([i,u,A.loc[u,'品牌'],A.loc[u,'平台'],A.loc[u,'链接'],A.loc[u,'互动数'],str(A.loc[u,txt]),'\n'.join(diffs) or '无分歧']+vals+[''])
        r=d.max_row
        for j,v in enumerate(VARS):
            cell=d.cell(r,9+j)
            if str(VA.loc[u,v])!=str(VB.loc[u,v]): cell.fill=yel; (dvp if v=='P2' else dv1).add(cell)
            else: cell.fill=grey
        d.cell(r,9+len(VARS)).fill=yel
    for row in d.iter_rows(min_row=2):
        for c in row: c.font=f; c.alignment=Alignment(wrap_text=True,vertical='top')
    from openpyxl.utils import get_column_letter as L
    for j,w in enumerate([5,24,10,10,26,8,60,42]+[12]+[9]*(len(VARS)-1)+[36],1): d.column_dimensions[L(j)].width=w
    d.freeze_panes='I2'
    wb.save('/mnt/user-data/outputs/'+out); print(out,len(A),nd)
