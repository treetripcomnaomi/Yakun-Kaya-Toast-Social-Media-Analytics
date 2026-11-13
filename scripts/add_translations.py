"""把 cleaned_data/translations_en.csv 的英文翻译并入各清洗文件：新增 text_en（打分用的英文文本）和 translated（是否翻译）。
在各清洗脚本之后运行；可重复运行。非英文内容由 Claude 按原语境翻译（保留 kaya、kopi、dabao 等本地词），见 translation_batch_all.json。
"""
import os, re, unicodedata, warnings, pandas as pd
warnings.filterwarnings("ignore")
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cleaned_data")
T = pd.read_csv(os.path.join(D, "translations_en.csv"), dtype=str, encoding="utf-8-sig")
T["translated"] = T.translated == "True"
nfkc = lambda s: unicodedata.normalize("NFKC", "" if pd.isna(s) else str(s))
JOBS = [("comments_youtube_clean.csv", "comment_id", lambda r: r.text),
        ("youtube_videos_clean.csv", "video_id", lambda r: f"{r.title} {'' if pd.isna(r.description) else r.description}"),
        ("tiktok_ugc_clean.csv", "video_id", lambda r: r.text),
        ("comments_official_clean.csv", "comment_id", lambda r: r.text),
        ("official_posts_clean.csv", "post_id", lambda r: r.caption),
        ("xhs_notes_clean.csv", "note_id", lambda r: r.text)]
for f, key, orig in JOBS:
    p = os.path.join(D, f); df = pd.read_csv(p, dtype={key: str}, low_memory=False)
    df = df.drop(columns=[c for c in ["text_en", "translated"] if c in df])
    t = T[T.file == f].drop_duplicates("id").set_index("id")
    base = df.apply(lambda r: nfkc(orig(r)), axis=1)
    df["translated"] = df[key].map(t.translated).fillna(False).astype(bool)
    df["text_en"] = df[key].map(t.text_en).where(df.translated, base)
    sq = lambda x: re.sub(r"nan$", "", re.sub(r"[\s|]+", "", nfkc(x)))[:120]
    stale = df.translated & (df[key].map(t.text_original).map(sq) != base.map(sq))
    if stale.any(): print(f"  ⚠ {f}: {int(stale.sum())} 条原文已变（如小红书补了完整正文），翻译需要更新")
    # 按文字系统修正语言：langdetect 常把繁体中文误判成韩文（ko）
    if f == "xhs_notes_clean.csv": df["lang"] = "zh"
    lc = next((c for c in ["lang", "caption_lang"] if c in df), None)
    if lc:
        txt = df.apply(lambda r: str(orig(r)), axis=1)
        script = txt.apply(lambda s: "ko" if re.search(r"[\uac00-\ud7a3]", s) else "ja" if re.search(r"[\u3040-\u30ff]", s)
                           else "zh" if re.search(r"[\u4e00-\u9fff]", s) else "th" if re.search(r"[\u0e00-\u0e7f]", s) else None)
        old = df[lc].astype(str).str.split("-").str[0].str.lower()
        df[lc] = script.where(script.notna() & (old.isin(["ko", "ja", "zh", "th", "unknown", "un", "nan"]) | (old != script)), df[lc])
    df.to_csv(p, index=False, encoding="utf-8-sig")
    print(f"{f}: {len(df)} 行，其中翻译 {int(df.translated.sum())} 条")
