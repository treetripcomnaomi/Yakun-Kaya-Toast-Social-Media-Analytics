import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':'#c3c2b7','axes.labelcolor':'#52514e','xtick.color':'#52514e','ytick.color':'#52514e','axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'#fcfcfb','axes.facecolor':'#fcfcfb'})
C={'Ya Kun':'#2a78d6','Toast Box':'#eb6834','Old Chang Kee':'#1baf7a','% Arabica':'#eda100'}
B=list(C); T='#0b0b0b'; S='#52514e'
M=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/step1_step5_metrics.csv')
M=M[M.platform.isin(['Instagram','TikTok'])]
def grouped(ax,metric,plats,fmt,title):
    x=np.arange(len(plats)); w=0.19
    for i,b in enumerate(B):
        vals=[M[(M.brand==b)&(M.platform==p)][metric].iloc[0] for p in plats]
        vals=[0 if pd.isna(v) else v for v in vals]
        bars=ax.bar(x+(i-1.5)*w,vals,w-0.02,color=C[b],label=b)
        for r,v in zip(bars,vals): ax.text(r.get_x()+r.get_width()/2,r.get_height(),fmt(v),ha='center',va='bottom',fontsize=8,color=S)
    ax.set_ylim(0,ax.get_ylim()[1]*1.18); ax.set_xticks(x,plats); ax.set_title(title,loc='left',color=T,fontsize=11); ax.grid(axis='y',color='#e9e8e4',lw=0.6); ax.set_axisbelow(True)
def save(fig,n,note):
    import textwrap; nt=textwrap.fill(note,115); fig.text(0.01,0.01,nt,fontsize=7.5,color=S,ha='left',va='bottom'); fig.tight_layout(rect=(0,0.04+0.025*nt.count(chr(10)),1,1)); fig.savefig('charts/'+n,dpi=200); plt.close(fig)
SRC='Source: Apify scrape of official accounts, 25 Apr - 18 Oct 2026 (177 days). NMC5342 Ya Kun group.'
fig,ax=plt.subplots(figsize=(7,4)); grouped(ax,'followers',['Instagram','TikTok'],lambda v:f'{v/1000:.1f}k' if v>=1000 else f'{v:.0f}','Audience size: followers by platform'); ax.legend(frameon=False,ncol=4,loc='upper center',fontsize=8)
save(fig,'step5_followers.png','Followers recorded 24 Oct 2026. TikTok = accounts scraped; manual audit lists Ya Kun & Toast Box TikTok at 2.7k (account to be confirmed).')
fig,ax=plt.subplots(figsize=(7,4)); grouped(ax,'avg_posts_per_day',['Instagram','TikTok'],lambda v:f'{v:.2f}','Posting frequency: average posts per day'); ax.legend(frameon=False,ncol=4,fontsize=8)
save(fig,'step5_posts_per_day.png',SRC+' Ya Kun TikTok: 0 posts (inactive since Mar 2025).')
fig,axs=plt.subplots(1,2,figsize=(9,4))
for ax,p in zip(axs,['Instagram','TikTok']):
    vals=[M[(M.brand==b)&(M.platform==p)].avg_engagement_per_post.iloc[0] for b in B]; vals=[0 if pd.isna(v) else v for v in vals]
    bars=ax.bar(range(4),vals,0.6,color=[C[b] for b in B])
    for r,v in zip(bars,vals): ax.text(r.get_x()+r.get_width()/2,r.get_height(),f'{v:.0f}' if v else 'no posts',ha='center',va='bottom',fontsize=8,color=S)
    ax.set_xticks(range(4),B,fontsize=8); ax.set_title(f'{p}: avg engagement per post',loc='left',fontsize=11,color=T); ax.grid(axis='y',color='#e9e8e4',lw=0.6); ax.set_axisbelow(True)
save(fig,'step5_engagement_per_post.png',SRC+' Engagement: IG = likes + comments; TikTok = likes + comments + shares + saves.')
fig,axs=plt.subplots(1,2,figsize=(9,4))
for ax,p in zip(axs,['Instagram','TikTok']):
    vals=[M[(M.brand==b)&(M.platform==p)].engagement_rate_per_post.iloc[0]*100 for b in B]; vals=[0 if pd.isna(v) else v for v in vals]
    bars=ax.bar(range(4),vals,0.6,color=[C[b] for b in B])
    for r,v in zip(bars,vals): ax.text(r.get_x()+r.get_width()/2,r.get_height(),f'{v:.2f}%' if v else 'no posts',ha='center',va='bottom',fontsize=8,color=S)
    ax.set_xticks(range(4),B,fontsize=8); ax.set_title(f'{p}: engagement rate per post',loc='left',fontsize=11,color=T); ax.grid(axis='y',color='#e9e8e4',lw=0.6); ax.set_axisbelow(True)
save(fig,'step5_engagement_rate.png',SRC+' Rate = avg engagement per post / followers. TikTok rates inflated by very small follower bases (e.g. % Arabica 83).')
# Step 4
w=pd.read_csv('step4_30d_rows.csv'); pm={'M11 YouTube comments':'YouTube','M11 YouTube videos':'YouTube','M4 official-post comments':'IG comments','M5 TikTok UGC':'TikTok','M6 Xiaohongshu notes':'Xiaohongshu'}
w['plat']=w.dataset.map(pm); t=pd.crosstab(w.plat,w.grp).reindex(['TikTok','Xiaohongshu','YouTube','IG comments']).fillna(0)
fig,ax=plt.subplots(figsize=(7,4)); x=np.arange(len(t)); 
for i,(g,col,lab) in enumerate([('client','#2a78d6','Ya Kun (client)'),('industry','#eb6834','Industry (kaya toast / SG breakfast)')]):
    bars=ax.bar(x+(i-0.5)*0.36,t[g],0.34,color=col,label=f'{lab}: {int(t[g].sum())}')
    for r,v in zip(bars,t[g]): ax.text(r.get_x()+r.get_width()/2,v,int(v),ha='center',va='bottom',fontsize=8,color=S)
ax.set_ylim(0,t.values.max()*1.25); ax.set_xticks(x,t.index); ax.legend(frameon=False,fontsize=8); ax.set_title('Mentions in the past 30 days (25 Sep - 24 Oct 2026)',loc='left',fontsize=11,color=T); ax.grid(axis='y',color='#e9e8e4',lw=0.6); ax.set_axisbelow(True)
save(fig,'step4_volume_30d.png','Counts are items our keyword scrapes retrieved (user posts and comments), not full platform volume. Brand24 (18 Aug - 17 Sep): 97 Ya Kun mentions.')
r=pd.read_csv('/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/RQ2_逐条_1103.csv'); ind=pd.read_csv('industry_sentiment_AI.csv')
mp={'F1':'Positive','F2':'Neutral','F3':'Negative','F4':'Mixed'}; mi={'P':'Positive','U':'Neutral','N':'Negative','M':'Mixed'}
rbl=pd.read_csv('/tmp/claude-0/sent/roberta_labels.csv').set_index('uid').roberta.map(mi); c30=r[r.uid.isin(w[w.grp=='client'].uid)].uid.map(rbl); call=r.uid.map(rbl)
rows=[('Ya Kun, past 30 days',c30),('Industry, past 30 days',ind[ind.in30].uid.map(rbl)),('Ya Kun, all collected',call),('Industry, random 200',ind[~ind.in30].uid.map(rbl))]
cats=['Negative','Neutral','Positive']; col={'Negative':'#e34948','Mixed':'#c9a0a0','Neutral':'#d6d5d0','Positive':'#2a78d6'}
fig,ax=plt.subplots(figsize=(8,3.6))
for i,(lab,s) in enumerate(rows[::-1]):
    sh=s.value_counts(normalize=True)*100; left=0
    for c in cats:
        v=sh.get(c,0); ax.barh(i,v,left=left,color=col[c],edgecolor='#fcfcfb',lw=2,label=c if i==0 else None)
        if v>=6: ax.text(left+v/2,i,f'{v:.0f}%',ha='center',va='center',fontsize=8,color='#fcfcfb' if c in('Positive','Negative') else T)
        left+=v
    ax.text(101,i,f'n={len(s)}',va='center',fontsize=8,color=S)
ax.set_yticks(range(4),[l for l,_ in rows[::-1]],fontsize=9); ax.set_xlim(0,110); ax.set_xticks([0,25,50,75,100],['0%','25%','50%','75%','100%'])
ax.legend(frameon=False,ncol=3,fontsize=8,loc='upper center',bbox_to_anchor=(0.45,1.18)); ax.spines['left'].set_visible(False)
save(fig,'step4_sentiment.png','Twitter-RoBERTa sentiment model (Barbieri et al., 2020) on English text (non-English translated). Agreement with human coders: kappa 0.51 (humans with each other: 0.52). Robustness check with AI codebook coding gives the same pattern.')
print(t)
