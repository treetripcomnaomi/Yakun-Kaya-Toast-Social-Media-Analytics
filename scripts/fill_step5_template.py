from openpyxl import load_workbook
from openpyxl.comments import Comment
from openpyxl.styles import Font, Alignment
import warnings; warnings.filterwarnings("ignore")
SRC = "/mnt/user-data/attachments/3d0b6125-65cb-5da2-8a82-53c83af33aed/7a4e0c23-Social_Media_Audit_Class_Practice.xlsx"
wb = load_workbook(SRC)
base = wb["Class Practice"]
# 数据：M1（2026-10-24 手工记录）+ 抓取（最近 6 个月 2026-04-25 至 2026-10-18）
FB = {"Ya Kun": 26000, "Toast Box": 73000, "Old Chang Kee": 34000, "% Arabica": 36000}
IG = {"Ya Kun": 20000, "Toast Box": 24000, "Old Chang Kee": 35000, "% Arabica": 21000}
TT = {"Ya Kun": 225, "Toast Box": 361, "Old Chang Kee": 6064, "% Arabica": 83}          # 抓取 authorMeta/fans
TT_FOLLOWING = {"Ya Kun": 6, "Toast Box": 6, "Old Chang Kee": 48, "% Arabica": 7}
import pandas as _pd
_S = _pd.read_csv("/tmp/claude-0/an/out/step1_step5_metrics.csv")
_S = _S[_S.platform.isin(["Instagram","TikTok"])]
PW = {(r.brand, r.platform): r.avg_posts_per_week for r in _S.itertuples()}
ENG = {(r.brand, r.platform): int(r.total_engagement_in_period) for r in _S.itertuples()}
_OLD_PW = {("Ya Kun","Instagram"):1.92, ("Ya Kun","TikTok"):0, ("Toast Box","Instagram"):2.00, ("Toast Box","TikTok"):0.27,
      ("Old Chang Kee","Instagram"):5.92, ("Old Chang Kee","TikTok"):1.23, ("% Arabica","Instagram"):3.69, ("% Arabica","TikTok"):1.62}
_OLD_ENG = {("Ya Kun","Instagram"):9400, ("Ya Kun","TikTok"):0, ("Toast Box","Instagram"):4045, ("Toast Box","TikTok"):176,
       ("Old Chang Kee","Instagram"):46376, ("Old Chang Kee","TikTok"):1043, ("% Arabica","Instagram"):6766, ("% Arabica","TikTok"):222}
IG_FOLLOWING = {"Ya Kun": 82, "Toast Box": 68, "Old Chang Kee": 170}   # Social Blade, 2026-10-30
TONE = {("Ya Kun","Instagram"):"Friendly", ("Toast Box","Instagram"):"Mixed", ("Toast Box","TikTok"):"Playful",
        ("Old Chang Kee","Instagram"):"Playful", ("Old Chang Kee","TikTok"):"Playful", ("% Arabica","Instagram"):"Inspirational", ("% Arabica","TikTok"):"Inspirational"}
WHY = {("Ya Kun","Instagram"):"warm, comforting daily-ritual copy ('A day at Ya Kun, one meal at a time')",
       ("Toast Box","Instagram"):"mix of promotions (Kopi Package), heritage craft (Nanyang Supremo) and friendly anniversary posts",
       ("Toast Box","TikTok"):"mascot dances (Kopi Kia), puns ('Berry excited?')",
       ("Old Chang Kee","Instagram"):"memes, puns and fyp-style humour ('Shan Shen Bu your way out of work')",
       ("Old Chang Kee","TikTok"):"memes and humour, same as IG",
       ("% Arabica","Instagram"):"minimal, aesthetic, aspirational lines ('Slow life, in a fast-paced world')",
       ("% Arabica","TikTok"):"same minimal aspirational voice as IG"}
NOTE_PREV = "Not available: historical follower counts were not recorded. Fill from Social Blade or a dated screenshot if available; otherwise leave blank and write 'not available' (template data note)."
def fill(ws, comp):
    ws["A3"] = (f"Ya Kun vs {comp}. Period: last 6 months (2026-04-25 to 2026-10-18; posts within 7 days of the 25 Oct collection excluded). "
                "Followers recorded 24 Oct 2026 (M1 audit; TikTok from scraped profile). Yellow = input, blue = formula. Blank = not available.")
    ws["A3"].alignment = Alignment(wrap_text=True); ws.row_dimensions[3].height = 45
    for r, brand in [(10, "Ya Kun"), (15, comp)]:
        rows = {"Facebook": r, "X / Twitter": r+1, "Instagram": r+2, "TikTok": r+3, "LinkedIn": r+4}
        for net, rr in rows.items():
            ws[f"A{rr}"] = brand
        ws[f"D{rows['Facebook']}"] = FB[brand]
        ws[f"D{rows['Instagram']}"] = IG[brand]
        ws[f"D{rows['TikTok']}"] = TT[brand]
        ws[f"F{rows['TikTok']}"] = TT_FOLLOWING[brand]
        for net in ["Instagram", "TikTok"]:
            ws[f"G{rows[net]}"] = PW[(brand, net)]; ws[f"H{rows[net]}"] = ENG[(brand, net)]
        ws[f"C{rows['Instagram']}"].comment = Comment(NOTE_PREV, "Claude")
        ws[f"H{rows['Facebook']}"] = "not available"; ws[f"G{rows['Facebook']}"] = "not available"
        ws[f"G{rows['Facebook']}"].comment = Comment("Facebook posting data not collected (only followers in M1). Not a focus platform.", "Claude")
        ws[f"D{rows['X / Twitter']}"].comment = Comment("No account found / not audited — write 'not available'.", "Claude")
        ws[f"D{rows['LinkedIn']}"].comment = Comment("No account found / not audited — write 'not available'.", "Claude")
        ws[f"H{rows['Instagram']}"].comment = Comment("Total likes + comments over the period (IG hides shares/saves). Posts with hidden likes excluded.", "Claude")
        ws[f"H{rows['TikTok']}"].comment = Comment("Total likes + comments + shares + saves over the period.", "Claude")
        if brand in IG_FOLLOWING:
            ws[f"F{rows['Instagram']}"] = IG_FOLLOWING[brand]
            ws[f"F{rows['Instagram']}"].comment = Comment("Following from Social Blade (socialblade.com), retrieved 2026-10-30.", "Claude")
        else:
            ws[f"F{rows['Instagram']}"].comment = Comment("Social Blade page could not be read — check the profile in the app.", "Claude")
        for net in ["Instagram", "TikTok"]:
            if (brand, net) in TONE:
                ws[f"J{rows[net]}"] = TONE[(brand, net)]
                ws[f"J{rows[net]}"].comment = Comment(f"Claude's suggestion from recent captions: {WHY[(brand, net)]}. Group to confirm.", "Claude")
        if brand == "Ya Kun":
            ws[f"J{rows['TikTok']}"].comment = Comment("Inactive since Mar 2025 — no recent posts to judge tone.", "Claude")
    ws["D13"].comment = Comment("Scraped profile: 225 followers, last video 2025-03-06. M1 recorded 2.7k — to be verified (2.7k matches Ya Kun Thailand's account).", "Claude")
    ws["G13"].comment = Comment("Ya Kun TikTok posted 0 videos in the last 6 months (inactive since Mar 2025).", "Claude")
    ws["D18"].comment = Comment("Scraped TikTok follower count; M1 value to be verified.", "Claude") if comp == "Toast Box" else None
sheets = []
for comp, name in [("Toast Box", "YaKun vs Toast Box"), ("Old Chang Kee", "YaKun vs Old Chang Kee"), ("% Arabica", "YaKun vs Arabica")]:
    ws = wb.copy_worksheet(base); ws.title = name; fill(ws, comp); sheets.append(ws)
    for dv in base.data_validations.dataValidation:      # 复制下拉 / 数值校验
        ws.data_validations.append(dv)
    ws.merged_cells  # 已随 copy_worksheet 复制
# 把三张填好的表排在最前，保留原 Class Practice / Worked Example / Student Guide
order = [wb[s.title] for s in sheets] + [wb["Class Practice"], wb["Worked Example"], wb["Student Guide"]]
wb._sheets = order
wb.active = 0
wb.save("/mnt/user-data/outputs/Step5_Social_Media_Audit_YaKun.xlsx")
print("saved")
