import pandas as pd, re, sys
from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0
F = sys.argv[1]; OUT = sys.argv[2]
df = pd.read_excel(F, 'Mentions', header=1).iloc[:, 1:]
n0 = len(df)
df['text'] = (df.Title.fillna('') + ' ' + df.Content.fillna('')).str.strip()
x_empty = (df.text == '').sum()
t = df.text.str.lower()
loose = t.str.contains(r'ya ?kun|yakun', regex=True) & t.str.contains(r'kaya|toast|kopi|coffee|egg|singapore|\bsg\b|breakfast|outlet|cafe|pie|mall|teh', regex=True)
strict = t.str.contains(r'ya ?kun kaya|yakun kaya|#\s?yakun|@yakun|ya kun (?:coffee|cafe|outlet|kopi|toast|set|far east|jurong)', regex=True)
noise = t.str.contains(r'lam yakun|fayakun|kun fa|yakun lahu|ya kun mah|ya kun mau|cerita bahasa indramayu|ceramah|kh hasan|sandiwara|wa kosim|raden chulaeng|misteri rangdu|kopiane mbah|nyandarua|ayblar|winora|tarling|full album|dikawin|pelet|yakun topdi|bauchi|fresh yakun|yakun sayang|hilman fauzi|xe đụng|hikoya', regex=True)
d = df[(loose | strict) & ~noise].copy()
n_rel = len(d)
d = d.drop_duplicates('text'); n_uniq = len(d)
def src(r):
    x = r.text.lower(); dm = str(r.Domain)
    if re.search(r'thrills singaporeans|delights singaporeans|comment on|comentario|commenti|komentar|تعليق|hozzászólása', x): return 'spam'
    if re.search(r'yakunmyanmar|yakun_indonesia|yakun\.com', x + dm): return 'brand_or_franchise'
    if re.search(r'promo|promotion|diskon|giveaway|deals|onsales|syioknya|free ', x + dm): return 'promo_site'
    if re.search(r'mall|directory|hotel|changiairport|junction8|313somerset|amazon|tour packages|atamed|amk hub|moe\.edu|townsquare', x + dm) and not re.search(r'youtube|reddit', dm): return 'commercial_listing'
    if re.search(r'stomp|wikipedia|tnp|oldest restaurants|foodification|drinkjournal', x + dm): return 'news_media'
    if re.search(r'itinerary|guide|layover guide|days in|walking|dishes to try|tour|vietdaily|hanoi|eranet|trotterz|magictrips|cravejourney|culturedwanderer|mimi|rebeccaandtheworld|hollandvillage|merlion', x + dm) and not re.search(r'youtube|tiktok|reddit|naver', dm): return 'travel_site'
    return 'ordinary_user'
d['source_type'] = d.apply(src, axis=1)
def lang(s):
    try: return detect(s)
    except Exception: return 'unknown'
d['lang'] = d.text.apply(lang)
d['latin_ratio'] = d.text.apply(lambda s: round(sum(c.isascii() for c in s)/max(len(s),1),2))
d = d.rename(columns={'ID':'id','Date':'date','Category':'platform','Domain':'domain','Source':'url','Sentiment':'brand24_sentiment'})
cols = ['id','date','platform','domain','url','source_type','lang','latin_ratio','brand24_sentiment','text']
d[cols].to_csv(OUT, index=False, encoding='utf-8-sig')
print(f'raw {n0} | X without text {x_empty} | relevant {n_rel} | unique {n_uniq}')
print(d.source_type.value_counts().to_string())
print('lang:', d.lang.value_counts().head(8).to_dict())
o = d[(d.source_type=='ordinary_user')]
print('ordinary_user English:', (o.lang=='en').sum())
