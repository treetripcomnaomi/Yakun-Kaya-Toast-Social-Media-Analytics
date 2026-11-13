from gensim.models import KeyedVectors
import numpy as np, random
wv = KeyedVectors.load('w2v_500k.kv')
H = ["heritage","tradition","legacy","history","historic","longstanding","roots","generations","nostalgia","nostalgic","memories","childhood","grandparents","ancestral","bygone","oldschool","age_old"]
N = ["trendy","latest","innovative","futuristic","experimental","viral","stylish","fashionable","collab","streetwear","upgraded","newest","trendiest","hip","cutting_edge","hottest","revamped"]
print("missing:", [w for w in H+N if w not in wv]); H=[w for w in H if w in wv]; N=[w for w in N if w in wv]
u=lambda v: v/np.linalg.norm(v)
def axis(h,n): return u(np.mean([u(wv[w]) for w in h],0)-np.mean([u(wv[w]) for w in n],0))
A=axis(H,N)
for side,lst in (("H",H),("N",N)):
    out=[]
    for w in lst:
        s=float(np.dot(u(wv[w]),axis([x for x in H if x!=w],[x for x in N if x!=w]))); out.append(f"{w} {s:+.2f}")
    print(side, len(lst), " | ".join(out))
vocab=[w for w in wv.index_to_key[:60000] if w.isalpha() and w.islower()]
M=np.array([u(wv[w]) for w in vocab]); sc=M@A; o=np.argsort(sc)
print("\nMOST NOVELTY:", [vocab[i] for i in o[:30]])
print("\nMOST HERITAGE:", [vocab[i] for i in o[-30:][::-1]])
# split-half stability on word scores
rs=[]
for k in range(20):
    random.seed(k); h=H[:]; n=N[:]; random.shuffle(h); random.shuffle(n)
    a1=axis(h[:len(h)//2],n[:len(n)//2]); a2=axis(h[len(h)//2:],n[len(n)//2:])
    rs.append(np.corrcoef(M@a1,M@a2)[0,1])
print("\nsplit-half r (20 random splits, 60k words): mean %.2f min %.2f"%(np.mean(rs),np.min(rs)))
for w in ["kopi","kaya","toast","breakfast","grandma","uncle","1944","since","family","collab","uniqlo","adidas","aesthetic","viral","tiktok","singapore","hawker","kopitiam"]:
    if w in wv: print(w, round(float(u(wv[w])@A),3))
