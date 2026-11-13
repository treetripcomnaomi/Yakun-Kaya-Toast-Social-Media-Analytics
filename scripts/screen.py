from gensim.models import KeyedVectors
import numpy as np
wv = KeyedVectors.load('w2v_500k.kv')
H = ["heritage","tradition","traditional","legacy","history","historic","timeless","longstanding","founded","roots","generations","nostalgia","nostalgic","memories","childhood","grandparents","ancestral","handed_down","authentic","old_school","classic","iconic","vintage","retro"]
N = ["trendy","modern","contemporary","new","latest","innovative","novel","futuristic","experimental","reinvented","viral","hype","cool","stylish","fashionable","collaboration","collab","limited_edition","streetwear","fusion","upgraded","aesthetic"]
miss=[w for w in H+N if w not in wv]; print("NOT IN VOCAB:", miss)
H=[w for w in H if w in wv]; N=[w for w in N if w in wv]
u=lambda v: v/np.linalg.norm(v)
def axis(h,n): return u(np.mean([u(wv[w]) for w in h],0)-np.mean([u(wv[w]) for w in n],0))
print("\nLeave-one-out score (+ = heritage side, - = novelty side)")
for side,lst in (("H",H),("N",N)):
    for w in lst:
        a = axis([x for x in H if x!=w],[x for x in N if x!=w])
        s=float(np.dot(u(wv[w]),a))
        flag = "  <-- WRONG SIDE" if (side=="H" and s<=0) or (side=="N" and s>=0) else ("  <-- weak" if abs(s)<0.1 else "")
        print(f"{side} {w:16s} {s:+.3f}{flag}")
print("\nNeighbours of ambiguous words")
for w in ["classic","iconic","vintage","retro","history","founded","new","cool","novel","aesthetic","fusion","authentic","roots"]:
    if w in wv: print(w, [x for x,_ in wv.most_similar(w,topn=8)])
