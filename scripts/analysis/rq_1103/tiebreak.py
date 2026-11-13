import sys; sys.path.insert(0,'/tmp/claude-0/rq'); exec(open('/tmp/claude-0/rq/s35_sheet.py').read().split("f=Font")[0])
T={ # (sheet, row): {var: value}
'S3':{1:{'CTA-LINK':1,'Y1':0},2:{'P2':'T-COMMUNITY','H3':0,'H5':0},3:{'P2':'T-COMMUNITY','CTA-NONE':1,'H3':0,'H5':1},
4:{'CTA-Q':0,'CTA-LINK':1,'H3':0},5:{'P2':'T-HERITAGE','H3':1},6:{'P2':'T-OTHER','CTA-NONE':1,'H3':0,'Y3':0,'Y0':1},
7:{'CTA-LINK':1,'Y3':1},8:{'Y2':1,'Y0':0},9:{'P2':'T-PROMO','CTA-LINK':1,'H2':0,'Y0':1},
10:{'P2':'T-STORE','CTA-Q':1,'H3':1,'Y4':1},11:{'P2':'T-FEST','CTA-LINK':1,'H1':1,'H3':0},12:{'CTA-NONE':1,'Y2':0,'Y4':0},
13:{'CTA-LINK':1,'H1':1},14:{'P2':'T-NEW','CTA-LINK':1,'H0':1},15:{'P2':'T-STORE','CTA-LINK':1,'H3':0,'H5':0,'Y0':1},
16:{'P2':'T-STORE','CTA-TAG':1,'H0':1},17:{'P2':'T-FEST','CTA-LINK':1,'Y3':1,'Y0':0},18:{'CTA-LINK':1,'H0':1,'Y0':1},
19:{'CTA-NONE':1,'H0':1,'Y0':1},20:{'P2':'T-HERITAGE','CTA-NONE':1,'Y0':1}},
'S5':{1:{'CTA-TAG':0},2:{'CTA-TAG':0,'CTA-LINK':1,'CTA-NONE':0,'H0':1,'Y2':1,'Y5':0,'Y0':0},3:{'P2':'T-STORE','CTA-TAG':0},
4:{'P2':'T-COMMUNITY','Y4':1},5:{'CTA-NONE':1,'H4':1},6:{'P2':'T-COMMUNITY','CTA-LINK':0,'CTA-NONE':1},7:{'P2':'T-COMMUNITY'},
8:{'CTA-LINK':1,'CTA-NONE':0},9:{'CTA-LINK':1,'CTA-NONE':0},10:{'P2':'T-COMMUNITY','H0':1},11:{'CTA-TAG':0,'H4':1,'H0':0},
12:{'H4':1,'H0':0},13:{'CTA-TAG':0,'Y3':1,'Y5':0,'Y6':0},15:{'P2':'T-COLLAB','CTA-LINK':0,'Y3':0},16:{'P2':'T-COMMUNITY','CTA-NONE':1},
17:{'P2':'T-COMMUNITY','CTA-NONE':1,'Y6':0},19:{'CTA-NONE':1,'H3':0,'H0':1},20:{'P2':'T-NEW','CTA-LINK':1},
21:{'H1':0,'Y6':0,'Y0':1},22:{'Y4':0,'Y0':1},23:{'CTA-NONE':1,'Y1':1,'Y0':0},24:{'CTA-TAG':0,'CTA-LINK':1,'CTA-NONE':0,'Y2':1},
25:{'CTA-TAG':0,'CTA-LINK':0,'CTA-NONE':1,'H4':0,'Y1':1,'Y0':0},26:{'CTA-TAG':0,'CTA-NONE':1,'Y5':1},27:{'P2':'T-FEST','Y4':1},
28:{'P2':'T-COMMUNITY','H0':1},29:{'P2':'T-PROMO','CTA-Q':0,'Y0':1},30:{'CTA-LINK':1}}}
rows=[]
for sheet,(fa,na),(fb_,nb),tag in [('S3_YaKun前20帖',('coding_v2_组员4.xlsx','组员4'),('coding_v2_组员5.xlsx','组员5'),'S3'),('S5_竞品前30帖',('coding_v2_组员5.xlsx','组员5'),('coding_v2_组员3.xlsx','组员3'),'S5')]:
    A=load(fa,sheet);B=load(fb_,sheet);VA,VB=vars_(A),vars_(B)
    for i,u in enumerate(A.index,1):
        r={'set':tag,'n':i,'uid':u,'brand':A.loc[u,'品牌'],'platform':A.loc[u,'平台'],'engagement':A.loc[u,'互动数'],'format':A.loc[u,'形式（自动）']}
        for v in VARS:
            a,b=VA.loc[u,v],VB.loc[u,v]
            if str(a)==str(b): r[v]=a; r[v+'_src']='两人一致'
            else:
                t=T[tag][i][v]; assert str(t) in (str(a),str(b)), (tag,i,v,t,a,b)
                r[v]=t; r[v+'_src']='Claude 第三方裁定'
        rows.append(r)
    missing=[(i,v) for i,u in enumerate(A.index,1) for v in VARS if str(VA.loc[u,v])!=str(VB.loc[u,v]) and v not in T[tag].get(i,{})]
    print(tag,'missing',missing)
D=pd.DataFrame(rows); D.to_csv('S3S5_final_codes.csv',index=False)
print(D.groupby('set').size())
