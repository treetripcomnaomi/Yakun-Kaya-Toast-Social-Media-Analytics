import pandas as pd, numpy as np, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
P = pd.read_csv(sys.argv[1], dtype={"post_id": str}, low_memory=False)
OUT = sys.argv[2]
F = "Arial"; HFILL = PatternFill("solid", fgColor="1F3864"); EXFILL = PatternFill("solid", fgColor="D9D9D9")
INFILL = PatternFill("solid", fgColor="FFF2CC"); thin = Side(style="thin", color="BFBFBF")
B = ["H1","H2","H3","H4","H5","H0"]; C = ["Y1","Y2","Y3","Y4","Y5","Y6","Y0"]; D = ["N1","N2","N3","N4","N5","N6"]
NAMES = {"H1":"H1 创始历史","H2":"H2 传统工艺","H3":"H3 个人/家庭记忆","H4":"H4 新加坡身份","H5":"H5 kopitiam文化","H0":"H0 无heritage",
 "Y1":"Y1 潮流形式","Y2":"Y2 联名","Y3":"Y3 新品/新口味","Y4":"Y4 周边/盲盒","Y5":"Y5 创作者/名人","Y6":"Y6 互动玩法","Y0":"Y0 无年轻化",
 "N1":"N1 价格","N2":"N2 促销","N3":"N3 审美/出片","N4":"N4 口味/品质","N5":"N5 方便/门店","N6":"N6 服务"}
def cap(r):
    return r.text_en if bool(r.translated) else r.caption
P["caption_show"] = P.apply(cap, axis=1)
P["engagement"] = pd.to_numeric(P.engagement, errors="coerce")

def coding_sheet(wb, title, df, codes, extra_note, example):
    ws = wb.create_sheet(title)
    info = ["编号", "品牌", "平台", "链接（点开看帖子）", "发布日期", "形式", "文案（非英文已译成英文）"]
    heads = info + [NAMES[c] for c in codes] + ["备注（拿不准时写原因）"]
    ws.append([extra_note]); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(heads))
    ws["A1"].font = Font(name=F, bold=True, color="C00000"); ws["A1"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[1].height = 48
    ws.append(heads)
    for j, h in enumerate(heads, 1):
        c = ws.cell(2, j); c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HFILL
        c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 36
    ws.append(example)                                   # 第 3 行灰色示例
    for j in range(1, len(heads)+1):
        c = ws.cell(3, j); c.fill = EXFILL; c.font = Font(name=F, italic=True, color="595959")
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for i, (_, r) in enumerate(df.iterrows(), 1):
        ws.append([f"{title[:2]}-{i:03d}", r.brand, r.platform, r.url, r.published_date, r.format, str(r.caption_show)[:1500]] + [""]*len(codes) + [""])
    n = ws.max_row
    dv = DataValidation(type="list", formula1='"1"', allow_blank=True, showDropDown=False)
    dv.error = "只能填 1（适用）或留空（不适用）"; ws.add_data_validation(dv)
    c0 = len(info) + 1; c1 = len(info) + len(codes)
    dv.add(f"{get_column_letter(c0)}4:{get_column_letter(c1)}{n}")
    for row in ws.iter_rows(min_row=4, max_row=n):
        for c in row:
            c.font = Font(name=F, size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
            c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        for c in row[c0-1:c1+1]: c.fill = INFILL; c.alignment = Alignment(horizontal="center", vertical="top")
        row[3].hyperlink = row[3].value; row[3].font = Font(name=F, size=10, color="0563C1", underline="single")
    widths = [9, 12, 10, 28, 11, 11, 70] + [9]*len(codes) + [28]
    for j, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(j)].width = w
    ws.freeze_panes = ws.cell(4, c0)
    ws.auto_filter.ref = f"A2:{get_column_letter(len(heads))}{n}"
    return ws

wb = Workbook(); ws = wb.active; ws.title = "说明"
G = [("怎么用这份表", ""),
 ("1", "每个人用自己的那份文件（文件名带 CoderA 或 CoderB），独立编码，编完之前不要和对方讨论。"),
 ("2", "只改黄色格子：适用就从下拉选 1，不适用就留空。每一行的 B 组（H 列）至少要有一个 1，没有 heritage 就选 H0；C 组（Y 列）同理，没有年轻化手法就选 Y0。"),
 ("3", "先读文案；判断 Y1 潮流形式、Y4 周边这类需要看画面的，点链接看一眼帖子。"),
 ("4", "只编帖子明确表达的内容，不推测。拿不准就留空并在备注写原因。"),
 ("5", "第 3 行灰色是示例，不用编。"),
 ("", ""),
 ("代码", "含义（例子）"),
 ("H1 创始历史", "品牌故事、年份、创始人：since 1944、Loi Ah Koon、老字号"),
 ("H2 传统工艺", "做法、配方、器具：炭烤、手工 kaya、布袋冲咖啡"),
 ("H3 个人/家庭记忆", "回忆、怀旧、家人：grew up eating this、my grandpa、小时候"),
 ("H4 新加坡身份", "国家、本地、家的味道：SG60、taste of home、uniquely Singaporean"),
 ("H5 kopitiam文化", "点单用语、吃法、早餐仪式：kopi C kosong、半熟蛋加酱油、每天早上都来"),
 ("H0 无heritage", "没有任何 heritage 含义：只说好吃、门店公告、纯促销"),
 ("Y1 潮流形式", "梗、热门音乐、挑战、POV、搞笑短剧"),
 ("Y2 联名", "和其他品牌、机构合作：adidas、UNIQLO、Fullerton Hotel"),
 ("Y3 新品/新口味", "新品、限定、融合口味：豆浆咖啡、Iced Moki、辣椒蟹 toastwich"),
 ("Y4 周边/盲盒", "钥匙扣、盲盒、联名服饰"),
 ("Y5 创作者/名人", "KOL 合作、明星出镜（如周润发光顾）"),
 ("Y6 互动玩法", "抽奖、竞猜、解谜、@朋友"),
 ("Y0 无年轻化", "传统形式的产品图、公告"),
 ("N1–N6（只在「竞品随机样本」表里编）", "N1 价格、N2 促销、N3 审美/出片、N4 口味/品质、N5 方便/门店、N6 服务"),
 ("", ""),
 ("分组规则（不用手动分，编完自动算）", "有 H1–H5、Y 只有 Y0 → 纯传统；有 H1–H5 且有 Y1–Y6 → 重新诠释；只有 H0 且有 Y1–Y6 → 纯年轻化；H0 且 Y0 → 都没有"),
 ("Top5 主题表", "每条写一句话说帖子在讲什么，30 条都写完后，再在「主题」列归类（新店/空间、节日、促销、联名、产品故事、其他），可以自己加类别"),
]
for a, b in G: ws.append([a, b])
ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 110
for row in ws.iter_rows():
    for c in row: c.font = Font(name=F, size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
for r in (1, 8): ws.cell(r, 1).font = Font(name=F, bold=True, size=12); ws.cell(r, 2).font = Font(name=F, bold=True, size=12)

yk = P[P.brand == "Ya Kun"].sort_values(["platform", "published_date"])
ex = ["示例", "Ya Kun", "Instagram", "https://www.instagram.com/p/示例/", "2025-08-08", "carousel",
      "Unveiling our SG60 exclusive mystery surprise keychain, with 5 unique designs…"] + ["","","","1","","" , "","","","1","","",""] + ["SG60 → H4；钥匙扣盲盒 → Y4"]
coding_sheet(wb, "YaKun官方帖", yk, B + C, f"Ya Kun 官方帖：全部 {len(yk)} 条（IG + TikTok，2024-07-01 起）。编 B 组（heritage 含义）和 C 组（年轻化手法），多选，适用填 1。", ex)

# 竞品随机样本：最近 6 个月、非 7 天内；每品牌 IG 20 条、TikTok 10 条（不足则全取）
rng = np.random.default_rng(5342)
pool = P[(P.brand != "Ya Kun") & (P.last_6m.astype(str) == "True")]
samp = []
for (b, pf), g in pool.groupby(["brand", "platform"]):
    k = 20 if pf == "Instagram" else 10
    samp.append(g.sample(min(k, len(g)), random_state=5342))
samp = pd.concat(samp).sort_values(["brand", "platform", "published_date"])
ex2 = ["示例", "Toast Box", "Instagram", "https://www.instagram.com/p/示例/", "2026-04-15", "carousel",
       "Our new pink concept store at Punggol Coast Mall is open! Try the Lychee Rose Dream…"] + [""]*5 + ["1"] + ["","","1","","","",""] + ["","","1","","",""] + ["新概念店+限定新品 → Y3；粉色主题拍照 → N3"]
coding_sheet(wb, "竞品随机样本", samp, B + C + D, f"竞品官方帖随机样本：最近 6 个月，每个品牌 IG 20 条、TikTok 10 条（不足则全取），共 {len(samp)} 条，随机种子 5342。编 B、C、D 三组。", ex2)

# Top 5 主题表
top = (pool[pool.use_for_engagement.astype(str) == "True"].sort_values("engagement", ascending=False)
       .groupby(["brand", "platform"]).head(5).sort_values(["brand", "platform", "engagement"], ascending=[True, True, False]))
ws = wb.create_sheet("竞品Top5主题")
heads = ["编号", "品牌", "平台", "排名", "链接", "发布日期", "形式", "互动数", "文案（非英文已译成英文）", "一句话：这条帖子在讲什么", "主题（写完 30 条后归类）", "备注"]
ws.append([f"竞品 Top 5：最近 6 个月每个竞品、每个平台互动最高的 5 条（IG 互动 = 点赞+评论；TikTok = 点赞+评论+分享+收藏），共 {len(top)} 条。只填黄色两列。"])
ws.merge_cells("A1:L1"); ws["A1"].font = Font(name=F, bold=True, color="C00000")
ws.append(heads)
for j in range(1, 13):
    c = ws.cell(2, j); c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HFILL; c.alignment = Alignment(wrap_text=True, horizontal="center")
ws.append(["示例", "Old Chang Kee", "Instagram", 1, "https://www.instagram.com/p/示例/", "2026-04-03", "image", 2500,
           "$0.70 Salted Egg Quail Egg OnStik — OCK 70th Anniversary Special Promo…", "70 周年庆，满 $7 加 7 毛钱换咸蛋鹌鹑蛋串", "促销 / 周年", ""])
for j in range(1, 13):
    c = ws.cell(3, j); c.fill = EXFILL; c.font = Font(name=F, italic=True, color="595959"); c.alignment = Alignment(wrap_text=True, vertical="top")
rk = top.groupby(["brand", "platform"]).cumcount() + 1
for i, ((_, r), k) in enumerate(zip(top.iterrows(), rk), 1):
    ws.append([f"T5-{i:03d}", r.brand, r.platform, int(k), r.url, r.published_date, r.format, int(r.engagement), str(r.caption_show)[:1500], "", "", ""])
for row in ws.iter_rows(min_row=4, max_row=ws.max_row):
    for c in row: c.font = Font(name=F, size=10); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
    row[9].fill = INFILL; row[10].fill = INFILL
    row[4].hyperlink = row[4].value; row[4].font = Font(name=F, size=10, color="0563C1", underline="single")
    row[7].number_format = "#,##0"
for j, w in enumerate([9, 13, 10, 6, 28, 11, 10, 9, 60, 36, 20, 20], 1): ws.column_dimensions[get_column_letter(j)].width = w
ws.freeze_panes = "B4"
wb.save(OUT)
print("YaKun", len(yk), "| 竞品样本", len(samp), samp.groupby(["brand","platform"]).size().to_dict(), "| Top5", len(top))
