import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gensim.models import KeyedVectors
wv = KeyedVectors.load('w2v_500k.kv'); A = np.load('heritage_axis.npy')
H = ["heritage","tradition","legacy","history","historic","longstanding","roots","generations","nostalgia","nostalgic","memories","childhood","grandparents","ancestral","bygone"]
N = ["trendy","latest","innovative","futuristic","experimental","viral","stylish","fashionable","collab","streetwear","upgraded","newest","trendiest","hip","cutting_edge","hottest","revamped"]
E = ["family","uncle","grandma","hometown","hawker","breakfast","coffee","toast","kaya","airport","singapore","merch","instagram","tiktok","adidas","uniqlo"]
E = [w for w in E if w in wv]
s = lambda w: float(wv[w] @ A / np.linalg.norm(wv[w]))
rows = [(w, s(w), 'Heritage seed word') for w in H] + [(w, s(w), 'Novelty seed word') for w in N] + [(w, s(w), 'Example word (not a seed)') for w in E]
rows.sort(key=lambda r: r[1])
col = {'Heritage seed word':'#2a78d6','Novelty seed word':'#eb6834','Example word (not a seed)':'#8a8a85'}
fig, ax = plt.subplots(figsize=(8, 12), dpi=200)
y = np.arange(len(rows))
ax.barh(y, [r[1] for r in rows], color=[col[r[2]] for r in rows], height=0.72, edgecolor='white', linewidth=1)
ax.set_yticks(y); ax.set_yticklabels([r[0].replace('_',' ') for r in rows], fontsize=8.5, color='#333333')
for lab in ax.get_yticklabels():
    if lab.get_text().replace(' ','_') in E: lab.set_fontweight('bold')
ax.axvline(0, color='#555555', linewidth=1)
ax.set_xlabel('Projection on heritage axis  (cosine similarity;  + heritage-oriented,  − novelty-oriented)', fontsize=9, color='#333333')
ax.grid(axis='x', color='#e5e5e2', linewidth=0.8); ax.set_axisbelow(True)
for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color('#999999'); ax.tick_params(axis='x', labelsize=8, colors='#555555'); ax.tick_params(axis='y', length=0)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=c, label=k) for k, c in col.items()], loc='lower right', fontsize=8.5, frameon=False)
ax.set_title('Where words fall on the heritage–novelty axis', fontsize=12, fontweight='bold', loc='left', color='#1a1a1a', pad=24)
ax.text(0, 1.008, 'Ya Kun heritage vec-tionary (v1), Google News word2vec; 15 heritage and 17 novelty seed words', transform=ax.transAxes, fontsize=8, color='#666666')
plt.tight_layout()
out = '/sessions/' + __import__('os').environ['HOME'].split('/sessions/')[1] + '/mnt/文稿:YaKun_vMFD/fig_heritage_axis_words.png'
plt.savefig(out, bbox_inches='tight', facecolor='white'); print(out)
for r in rows: 
    if r[2].startswith('Example'): print(r[0], round(r[1],3))
