# Regressions added 2026-11-09 for the final report.
# Run from the project folder (文稿:YaKun_vMFD). Needs pandas, numpy, statsmodels.
# A. RQ1: log(relative engagement) on heritage + controls, Ya Kun IG 243 posts  -> heritage x1.56, p<.001, R2 0.26
# B. RQ4: log(views) on heritage axis score + controls, 412 Ya Kun-related TikTok user videos -> b=-0.175 (~16% fewer views per SD), p=.029, R2 0.40
import pandas as pd, numpy as np, statsmodels.formula.api as smf

# ---------- A. RQ1 ----------
r = pd.read_csv('analysis_outputs/RQ1_逐条_v2_1103.csv', dtype={'post_id': str})
o = pd.read_csv('cleaned_data/official_posts_clean.csv', dtype={'post_id': str}).drop_duplicates('post_id').set_index('post_id')
b = pd.read_csv('analysis_outputs/人际联结_官方帖256_1103.csv').set_index('uid')
r['format'] = r.post_id.map(o.format)
r['coauth'] = r.post_id.map(o.is_coauthor_post).fillna(False).astype(int)
r['fest'] = pd.to_datetime(r.published_date).dt.month.isin([1, 2, 8, 9, 12]).astype(int)
r['N'] = r.C_youth.fillna('').str.split(';').apply(lambda c: any(x in ('Y2', 'Y3', 'Y4') for x in c)).astype(int)  # collab/new product/merch
r['bond'] = r.uid.map(b.bond).fillna(0).astype(int)
mA = smf.ols('np.log(rel) ~ Hbin + N + coauth + C(format, Treatment("carousel")) + bond + fest + C(year)', r).fit(cov_type='HC3')
print('A. RQ1'); print(mA.summary().tables[1]); print('exp(coef):', np.exp(mA.params).round(2).to_dict(), 'R2', round(mA.rsquared, 3))

# ---------- B. RQ4 ----------
M = pd.read_csv('analysis_outputs/master_scored.csv', low_memory=False)
S = pd.read_csv('analysis_outputs/heritage轴_交叉拟合分数_1106.csv').set_index('uid').h
T = pd.read_csv('cleaned_data/tiktok_ugc_clean.csv', dtype={'video_id': str}).set_index('video_id')
v = M[(M.dataset == 'M5 TikTok UGC') & (M.yakun_related == True) & (~M.author_type.isin(['brand', 'brand_or_franchise']))].copy()
v = v[v.views > 0]; v['h'] = v.uid.map(S); v = v.dropna(subset=['h'])  # n = 412
v['vid'] = v.uid.str[3:]
v['dur'] = v.vid.map(T.duration_sec); v['fmt'] = v.vid.map(T.format); v['author'] = v.vid.map(T.author_anon)
v['tourist'] = v.vid.map(T.tourist_cue)
v['age_days'] = (pd.Timestamp('2026-10-25') - pd.to_datetime(v.published_date, errors='coerce')).dt.days.clip(lower=0)
v['lviews'] = np.log1p(v.views); v['lfans'] = np.log1p(v.author_fans); v['ldur'] = np.log1p(v.dur); v['lage'] = np.log1p(v.age_days)
v['slide'] = v.fmt.astype(str).str.contains('slide', case=False).astype(int)
v['en'] = v.lang.astype(str).str.startswith('en').astype(int)
v['hz'] = (v.h - v.h.mean()) / v.h.std()
v['epv'] = v.engagement / v.views
f = 'lviews ~ hz + lfans + ldur + lage + slide + en'
mB = smf.ols(f, v).fit(cov_type='HC3'); print('\nB. RQ4 n', len(v)); print(mB.summary().tables[1]); print('R2', round(mB.rsquared, 3))
print('clustered by creator:', smf.ols(f, v).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(v.author)[0]}).pvalues.hz.round(4))
print('+ tourist cue:', smf.ols(f + ' + C(tourist)', v).fit(cov_type='HC3').pvalues.hz.round(4))
print('engagement per view:', smf.ols('epv ~ hz + lfans + ldur + lage + slide + en', v).fit(cov_type='HC3').pvalues.hz.round(4))
