import sys,re,os,warnings; warnings.filterwarnings('ignore'); os.chdir('/tmp/claude-0/rq'); exec(open('lib.py').read())
import torch
from transformers import RobertaTokenizer, AutoModelForSequenceClassification
tok=RobertaTokenizer('/tmp/claude-0/rob/vocab.json','/tmp/claude-0/rob/merges.txt')
mod=AutoModelForSequenceClassification.from_pretrained('/tmp/claude-0/rob').eval()
U='/mnt/user-data/uploads/文稿:YaKun_vMFD/analysis_outputs/'
M=pd.read_csv(U+'master_scored.csv',low_memory=False).set_index('uid')
mp={'F1':'P','F2':'U','F3':'N','F4':'M'}
H={c:human_vars(load(f,'V3_用户内容60'),remap=(c=='组员1'))['F'].map(mp) for f,c in [('coding_v2_组员5.xlsx','组员5'),('coding_v2_组员1.xlsx','组员1')]}
test=H['组员5'].index.union(H['组员1'].index)
def prep(s): return ' '.join('@user' if w.startswith('@') else ('http' if w.startswith('http') else w) for w in str(s).split())
def pred(s):
    with torch.no_grad(): o=mod(**tok(prep(s),return_tensors='pt',truncation=True,max_length=512)).logits
    return ['N','U','P'][int(o.argmax())]
P=pd.Series({u:pred(M.text_en.get(u,'')) for u in test})
def target(s):
    sents=re.split(r'(?<=[.!?。！？\n])\s*',str(s)); k=[x for x in sents if re.search(r'ya ?kun|亚坤|亞坤',x,re.I)]
    return ' '.join(k) if k else str(s)
P2=pd.Series({u:pred(target(M.text_en.get(u,''))) for u in test})
out=[]
for nm,pp in [('Twitter-RoBERTa（整段）',P),('Twitter-RoBERTa（只看提到 Ya Kun 的句子）',P2)]:
    for c,h in H.items():
        m=h.reindex(test).isin(['P','U','N']); x,y=h.reindex(test)[m],pp[m]
        out.append([nm,c,int(m.sum()),round(k(x,y),2),round(ac1(x,y),2),round((x==y).mean(),2)])
R=pd.DataFrame(out,columns=['方法','对照组员','n','κ','AC1','一致率']); print(R.to_string())
print(R.groupby('方法',sort=False)[['κ','AC1','一致率']].mean().round(2))
old=pd.read_csv('/tmp/claude-0/sent/sentiment_methods.csv'); pd.concat([old,R]).to_csv('/tmp/claude-0/sent/sentiment_methods.csv',index=False)
