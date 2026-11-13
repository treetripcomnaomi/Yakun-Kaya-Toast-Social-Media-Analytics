from gensim.models import KeyedVectors
import numpy as np
wv = KeyedVectors.load('w2v_500k.kv')
H = ["heritage","tradition","legacy","history","historic","longstanding","roots","generations","nostalgia","nostalgic","memories","childhood","grandparents","ancestral","bygone"]
N = ["trendy","latest","innovative","futuristic","experimental","viral","stylish","fashionable","collab","streetwear","upgraded","newest","trendiest","hip","cutting_edge","hottest","revamped"]
u=lambda v: v/np.linalg.norm(v)
A=u(np.mean([u(wv[w]) for w in H],0)-np.mean([u(wv[w]) for w in N],0))
np.save('heritage_axis.npy',A); print("axis saved", A.shape)
