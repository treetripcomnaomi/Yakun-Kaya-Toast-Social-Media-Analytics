import pandas as pd, numpy as np, matplotlib, textwrap
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#c3c2b7','axes.labelcolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
C={'Ya Kun':'#2a78d6','Toast Box':'#eb6834','Old Chang Kee':'#1baf7a','% Arabica':'#eda100'}; B=list(C); T='#0b0b0b'; S='#52514e'; G='#b9b8b3'
def fin(fig,ax_list,name,note):
    for ax in ax_list: ax.grid(axis='y',color='#e9e8e4',lw=0.6); ax.set_axisbelow(True)
    nt=textwrap.fill(note,115); fig.text(0.01,0.01,nt,fontsize=7.5,color=S,va='bottom'); fig.tight_layout(rect=(0,0.04+0.03*nt.count('\n'),1,1)); fig.savefig('charts/'+name,dpi=200); plt.close(fig)
def bars(ax,labels,vals,ns,colors,title,ref=True):
    b=ax.bar(range(len(vals)),vals,0.6,color=colors)
    for r,v,n in zip(b,vals,ns): ax.text(r.get_x()+r.get_width()/2,v,f'{v:.2f}\n(n={n})',ha='center',va='bottom',fontsize=8,color=S)
    if ref: ax.axhline(1,color=G,lw=1,ls='--'); 
    ax.set_xticks(range(len(vals)),labels,fontsize=8.5); ax.set_ylim(0,max(vals)*1.3); ax.set_title(title,loc='left',fontsize=11,color=T)
d=pd.read_csv('rq1_ig_final.csv')
d['Y3s']=d.C_youth.fillna('').str.contains(r'\bY[234]\b')
d['T']=np.select([d.Hbin.eq(1)&~d.Y3s,d.Hbin.eq(1)&d.Y3s,d.Hbin.eq(0)&d.Y3s],['Heritage only','Heritage + new\n(reinterpretation)','New tactics only'],'Neither')
order=['Heritage only','Heritage + new\n(reinterpretation)','New tactics only','Neither']
g=d.groupby('T').rel.agg(['median','size']).reindex(order)
fig,axs=plt.subplots(1,2,figsize=(10,4),gridspec_kw={'width_ratios':[1,2]})
h=d.groupby('Hbin').rel.agg(['median','size'])
bars(axs[0],['No heritage','Heritage'],[h.loc[0,'median'],h.loc[1,'median']],[h.loc[0,'size'],h.loc[1,'size']],[G,'#2a78d6'],'Heritage vs not (p = 0.006)')
bars(axs[1],order,g['median'].values,g['size'].values,['#2a78d6','#2a78d6',G,G],'Four post types (p = 0.038, small effect)')
for ax in axs: ax.set_ylabel('Median relative engagement')
fin(fig,axs,'rq1_heritage_types.png','Ya Kun Instagram posts, Jul 2024 - Oct 2026 (n = 243). Relative engagement = post engagement / median of the same year (1 = typical post; dashed line). New tactics = collab, new product, merch (codes that passed reliability).')
fig,axs=plt.subplots(1,2,figsize=(10,4))
f=d.groupby('format').rel.agg(['median','size']).reindex(['carousel','image','reel_video'])
bars(axs[0],['Carousel','Single image','Reel / video'],f['median'].values,f['size'].values,['#2a78d6',G,G],'By format')
d['vid']=d.format.eq('reel_video'); x=d.groupby(['vid','Hbin']).rel.agg(['median','size'])
lab=['Video,\nno heritage','Video +\nheritage','Non-video,\nno heritage','Non-video +\nheritage']
idx=[(True,0),(True,1),(False,0),(False,1)]
bars(axs[1],lab,[x.loc[i,'median'] for i in idx],[x.loc[i,'size'] for i in idx],[G,'#2a78d6',G,'#2a78d6'],'Video works better with heritage')
for ax in axs: ax.set_ylabel('Median relative engagement')
fin(fig,axs,'rq1_format.png','Ya Kun Instagram posts (n = 243). Format from platform metadata (no coding). Descriptive comparison; posting time and topic not controlled.')
h=pd.read_csv('/tmp/claude-0/rq/heritage_binary_official.csv'); w=h[h.win6.astype(str)=='True']
fig,axs=plt.subplots(1,2,figsize=(10,4))
sh=[w[w.brand==b].Hbin.mean()*100 for b in B]; ns=[len(w[w.brand==b]) for b in B]
bb=axs[0].bar(range(4),sh,0.6,color=[C[b] for b in B])
for r,v,n in zip(bb,sh,ns): axs[0].text(r.get_x()+r.get_width()/2,v,f'{v:.0f}%\n(n={n})',ha='center',va='bottom',fontsize=8,color=S)
axs[0].set_xticks(range(4),B,fontsize=8.5); axs[0].set_ylim(0,55); axs[0].set_title('Share of posts using heritage',loc='left',fontsize=11,color=T); axs[0].set_ylabel('% of posts, last 6 months')
wi=w[w.platform=='Instagram']; x=np.arange(4)
for j,(hv,lab,col) in enumerate([(0,'No heritage',G),(1,'Heritage',None)]):
    vals=[wi[(wi.brand==b)&(wi.Hbin==hv)].engagement.median() for b in B]
    bb=axs[1].bar(x+(j-0.5)*0.36,vals,0.34,color=[G]*4 if col else [C[b] for b in B],label=lab)
    for r,v in zip(bb,vals): axs[1].text(r.get_x()+r.get_width()/2,v,f'{v:.0f}',ha='center',va='bottom',fontsize=8,color=S)
axs[1].set_xticks(x,B,fontsize=8.5); axs[1].set_title('IG median engagement: heritage vs not',loc='left',fontsize=11,color=T); axs[1].set_ylabel('Median engagement per post')
axs[1].text(0.99,0.97,'grey = no heritage; colour = heritage\nOnly Ya Kun: p = 0.05; others n.s.',transform=axs[1].transAxes,ha='right',va='top',fontsize=8,color=S)
axs[1].set_ylim(0,max(wi.groupby(['brand','Hbin']).engagement.median())*1.35)
fin(fig,axs,'rq3_heritage_by_brand.png','Official posts 25 Apr - 24 Oct 2026, IG + TikTok (left), IG only (right). Heritage = yes/no AI coding validated against two coders (kappa 0.77 / 0.72).')
bd=pd.read_csv('/tmp/claude-0/rq/bond256_rows.csv'); bd['year']=bd.year.astype(int); y=bd.groupby('year').bond.agg(['mean','size','sum'])
fig,axs=plt.subplots(1,2,figsize=(10,4))
bb=axs[0].bar(range(len(y)),y['mean']*100,0.6,color='#2a78d6')
for r,(i,row) in zip(bb,y.iterrows()): axs[0].text(r.get_x()+r.get_width()/2,row['mean']*100,f"{row['mean']*100:.0f}%\n({int(row['sum'])}/{int(row['size'])})",ha='center',va='bottom',fontsize=8,color=S)
axs[0].set_xticks(range(len(y)),[str(i) for i in y.index]); axs[0].set_ylim(0,35); axs[0].set_title('Ya Kun posts about sharing with others',loc='left',fontsize=11,color=T); axs[0].set_ylabel('% of official posts')
ig=bd[bd.platform=='Instagram'].dropna(subset=['rel']); ig['grp']=np.select([ig.Hbin.eq(1)&ig.bond.eq(0),ig.Hbin.eq(0)&ig.bond.eq(0),ig.Hbin.eq(1)&ig.bond.eq(1)],['Heritage only','Neither','Heritage + bonding'],'Bonding only')
o2=['Heritage only','Neither','Heritage + bonding','Bonding only']; q=ig.groupby('grp').rel.agg(['median','size']).reindex(o2)
bars(axs[1],[t.replace(' + ','\n+ ') for t in o2],q['median'].values,q['size'].values,['#2a78d6',G,'#86b6ef',G],'IG relative engagement')
axs[1].set_ylabel('Median relative engagement')
fin(fig,axs,'bond_trend.png','Ya Kun official posts (n = 256). Social bonding = post links Ya Kun to family, friends or colleagues; AI coding checked against one coder on 20 posts (kappa 0.89).')
print(y); print(q)
