"""编码表 v2（按编码手册 v1.1）：每位编码员一份；uid 用于之后算 κ。"""
import pandas as pd, numpy as np, sys, re
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
M = pd.read_csv(sys.argv[1], low_memory=False, dtype={"item_id": str, "parent_id": str}); OUTDIR = sys.argv[2]
P = pd.read_csv(sys.argv[3], low_memory=False, dtype={"post_id": str})
SEED = 5342; rng = np.random.default_rng(SEED)
F = "Arial"; HF = PatternFill("solid", fgColor="1F3864"); EX = PatternFill("solid", fgColor="D9D9D9"); IN = PatternFill("solid", fgColor="FFF2CC")
AUTO = PatternFill("solid", fgColor="DDEBF7"); th = Side(style="thin", color="BFBFBF")
P["d"] = pd.to_datetime(P.published_date)
P["uid"] = "M2M3_" + P.post_id
def show_text(r):
    t = str(r.text_en)
    return t if not bool(r.translated) else t + "  [machine-translated by Claude]"
# ---------- 样本 ----------
eng = P[P.use_for_engagement.astype(str) == "True"]
top20 = (eng[eng.brand == "Ya Kun"].sort_values("engagement", ascending=False).groupby("platform").head(10)
         .sort_values(["platform", "engagement"], ascending=[True, False]))
six = eng[(eng.d >= "2026-04-25") & (eng.d <= "2026-10-18") & (eng.brand != "Ya Kun")]
top30 = (six.sort_values("engagement", ascending=False).groupby(["brand", "platform"]).head(5)
         .sort_values(["brand", "platform", "engagement"], ascending=[True, True, False]))
yk_rest = P[(P.brand == "Ya Kun") & ~P.post_id.isin(top20.post_id)]
v1 = yk_rest.sample(50, random_state=SEED).sort_values("published_date")
comp_pool = P[(P.brand != "Ya Kun") & (P.last_6m.astype(str) == "True") & ~P.post_id.isin(top30.post_id)]
v2 = comp_pool.groupby("brand").sample(n=10, random_state=SEED).sort_values(["brand", "published_date"])
user = M[M.yakun_related & (M.content_type != "official_post") & (M.author_type != "brand")
         & ~M.text_en.astype(str).str.contains(r"\(political, off-topic\)") & (M.text_en.astype(str).str.split().str.len() >= 4)]
def strat(df, plan):
    parts = []
    for ds, n in plan.items():
        g = df[df.dataset == ds]; parts.append(g.sample(min(n, len(g)), random_state=SEED))
    return pd.concat(parts)
v3 = strat(user, {"M5 TikTok UGC": 15, "M11 YouTube videos": 8, "M11 YouTube comments": 17, "M4 official-post comments": 15, "M7 Brand24": 5})
tour_pool = user[~user.uid.isin(v3.uid)]
t100 = strat(tour_pool, {"M5 TikTok UGC": 45, "M11 YouTube videos": 25, "M11 YouTube comments": 20, "M4 official-post comments": 10})
t100 = t100.sample(frac=1, random_state=SEED)       # 打乱顺序，避免按平台扎堆
xhs = M[(M.dataset == "M6 Xiaohongshu notes") & M.yakun_related].sort_values("published_date")
# ---------- 代码 ----------
H = ["H1 创始历史", "H2 传统工艺", "H3 个人/家庭记忆", "H4 新加坡身份", "H5 kopitiam文化", "H0 无heritage"]
Y = ["Y1 潮流形式", "Y2 联名", "Y3 新品/新口味", "Y4 周边/盲盒", "Y5 创作者/名人", "Y6 互动玩法", "Y0 无年轻化"]
CTA = ["CTA-Q 提问", "CTA-TAG @朋友", "CTA-GIVE 抽奖", "CTA-LINK 链接/App/到店", "CTA-NONE 无号召"]
N = ["N1 价格", "N2 促销", "N3 审美/出片", "N4 口味/品质", "N5 方便/门店", "N6 服务"]
TF = ["TF1 正宗heritage", "TF2 必吃/打卡", "TF3 普通早餐/方便", "TF4 游客陷阱/不值"]
LISTS = {"P2 主题（单选）": "T-NEW,T-PROMO,T-FEST,T-HERITAGE,T-COLLAB,T-STORE,T-COMMUNITY,T-OTHER",
         "A1 相关性": "R1,R2,R3,R0", "A2 来源": "S1,S2,S3,S4", "A3 商业披露": "P1,P0", "E 老派看法": "D1,D0",
         "F 情感": "F1,F2,F3,F4", "PR 价格参照（选了N1才填）": "PR1,PR2,PR3,PR0", "SC 豆浆咖啡": "1,0",
         "G 游客判断": "T1,T2,T3,T0", "P1 形式（核对）": "image,carousel,reel_video,video,slideshow", "P1 是否正确": "对,不对"}
def sheet(wb, title, note, info_cols, rows, code_cols, example=None):
    ws = wb.create_sheet(title)
    heads = info_cols + code_cols + ["备注（拿不准写原因）"]
    ws.append([note]); ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(heads))
    ws["A1"].font = Font(name=F, bold=True, color="C00000"); ws["A1"].alignment = Alignment(wrap_text=True, vertical="top"); ws.row_dimensions[1].height = 42
    ws.append(heads)
    for j in range(1, len(heads) + 1):
        c = ws.cell(2, j); c.font = Font(name=F, bold=True, color="FFFFFF", size=9); c.fill = HF; c.alignment = Alignment(wrap_text=True, horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 48
    if example:
        ws.append(example)
        for j in range(1, len(heads) + 1):
            c = ws.cell(3, j); c.fill = EX; c.font = Font(name=F, italic=True, color="595959", size=9); c.alignment = Alignment(wrap_text=True, vertical="top")
    start = ws.max_row + 1
    for r in rows: ws.append(r + [""] * (len(heads) - len(r)))
    n = ws.max_row; c0 = len(info_cols) + 1
    for j, h in enumerate(code_cols, c0):
        col = get_column_letter(j)
        f1 = LISTS.get(h, "1"); dv = DataValidation(type="list", formula1=f'"{f1}"', allow_blank=True); ws.add_data_validation(dv); dv.add(f"{col}{start}:{col}{n}")
    for row in ws.iter_rows(min_row=start, max_row=n):
        for c in row:
            c.font = Font(name=F, size=9); c.alignment = Alignment(wrap_text=True, vertical="top"); c.border = Border(top=th, bottom=th, left=th, right=th)
        for c in row[c0 - 1:c0 - 1 + len(code_cols)]: c.fill = IN; c.alignment = Alignment(horizontal="center", vertical="top")
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("http"):
                c.hyperlink = c.value; c.font = Font(name=F, size=9, color="0563C1", underline="single")
    widths = {"文案 / 文本（英文；非英文已翻译）": 60, "链接": 24, "uid（勿改）": 14}
    for j, h in enumerate(heads, 1):
        ws.column_dimensions[get_column_letter(j)].width = widths.get(h, 7 if j >= c0 and j < c0 + len(code_cols) else 11)
    ws.column_dimensions[get_column_letter(len(heads))].width = 24
    ws.freeze_panes = ws.cell(start, c0); return ws
def post_rows(df):
    out = []
    for r in df.itertuples():
        hr = r.d.hour if hasattr(r.d, "hour") else 0
        out.append([r.uid, r.brand, r.platform, r.url, r.published_date, int(r.engagement) if pd.notna(r.engagement) else "",
                    show_text(r)[:1500], r.format, ("周末" if r.d.dayofweek >= 5 else "工作日")])
    return out
POST_INFO = ["uid（勿改）", "品牌", "平台", "链接", "发布日期", "互动数", "文案 / 文本（英文；非英文已翻译）", "形式（自动）", "工作日/周末（自动）"]
def user_rows(df, tourist=False):
    out = []
    for r in df.itertuples():
        orig = "" if not bool(r.translated) else "（原文为非英文，见 cleaned_data/translations_en.csv）"
        row = [r.uid, r.dataset, r.platform, r.url if isinstance(r.url, str) else "", r.published_date, show_text(r)[:1500] + orig]
        if tourist: row += [r.location_country if isinstance(r.location_country, str) else "", r.lang]
        out.append(row)
    return out
USER_INFO = ["uid（勿改）", "数据来源", "平台", "链接", "日期", "文案 / 文本（英文；非英文已翻译）"]
for coder in ["CoderA", "CoderB"]:
    wb = Workbook(); ws = wb.active; ws.title = "说明"
    G = [("编码员", coder), ("怎么用", "每张表只改黄色格子：适用的从下拉选 1，或从下拉选代码；不适用留空。不要和另一位编码员讨论，全部编完再对。代码定义见「Ya Kun 编码手册 v1.1」。"),
         ("建议顺序", "① S3_YaKun前20帖（老师要求，先编）→ ② S5_竞品前30帖 → ③ RQ4_游客检验100 + RQ4b_小红书 → ④ V1/V2/V3 验证子集（用来检验 AI 初编，AI 的标签不显示在这里）"),
         ("形式和时间", "「形式」「工作日/周末」已由数据自动填好（浅蓝/白色列），S3/S5 表里只需在「P1 是否正确」核对一下。"),
         ("多选", "H 列至少选一个 1（没有 heritage 就选 H0）；Y 列同理（没有就选 Y0）；CTA 列至少一个（没有就选 CTA-NONE）。"),
         ("游客判断", "必须有明确文字线索才判 T1/T2；地点、语言只作辅助，不能单独判断。T3 = 在海外加盟店消费。判断不了就 T0。只有 T1 才填 TF 列。"),
         ("价格参照", "只有选了 N1 价格时才填 PR：PR1 和 kopitiam/熟食中心比，PR2 和咖啡连锁比，PR3 和 Ya Kun 自己以前或其他饮品比，PR0 没有参照。"),
         ("样本说明", f"随机种子 {SEED}；S3 = Ya Kun 2024-07 起各平台互动前 10；S5 = 竞品最近 6 个月各平台互动前 5；V1/V2/V3 与 S3/S5 不重复；游客 100 条与 V3 不重复。")]
    for a, b in G: ws.append([a, b])
    ws.column_dimensions["A"].width = 14; ws.column_dimensions["B"].width = 120
    for row in ws.iter_rows():
        for c in row: c.font = Font(name=F, size=10); c.alignment = Alignment(wrap_text=True, vertical="top")
    PCODES = ["P1 是否正确", "P2 主题（单选）"] + CTA + H + Y
    ex = ["示例", "Ya Kun", "Instagram", "https://www.instagram.com/p/示例/", "2024-08-26", 1200, "SOLVE THE MYSTERY, SPORT THE HOODIE! LAST GIVEAWAY… tag 2 friends…", "carousel", "工作日",
          "对", "T-COLLAB", "", "1", "1", "", "", "", "", "", "", "", "1", "", "1", "", "1", "", "1", "", "adidas 联名卫衣 + 解谜抽奖：Y2 联名、Y4 周边、Y6 互动玩法"]
    sheet(wb, "S3_YaKun前20帖", "Step 3（老师要求）：Ya Kun IG、TikTok 各互动前 10 帖。两名组员各自编码，信度在你们两人之间算。", POST_INFO, post_rows(top20), PCODES, ex)
    sheet(wb, "S5_竞品前30帖", "Step 5：每个竞品每个平台最近 6 个月互动前 5 帖（共 30 条）。同样的类目，方便和 Step 3 对比。", POST_INFO, post_rows(top30), PCODES)
    sheet(wb, "RQ4_游客检验100", "RQ4 门槛：能判断（T1 或 T2）≥ 60% 且两人 κ ≥ 0.7 才保留 RQ4。地点和语言只作辅助线索。", USER_INFO + ["地点/频道国家（辅助）", "语言（辅助）"],
          user_rows(t100, tourist=True), ["G 游客判断"] + TF)
    sheet(wb, "RQ4b_小红书", "RQ4 补充：小红书提到 Ya Kun 的全部笔记（免费版正文只有前约 60 字，请点链接看全文；IP 属地组员补录后会填进来）。判断规则同 RQ4_游客检验100。", USER_INFO + ["IP属地（补录后填）", "语言（辅助）"],
          user_rows(xhs, tourist=True), ["G 游客判断"] + TF)
    sheet(wb, "V1_官方帖50", "验证 AI 初编：Ya Kun 官方帖随机 50 条，编 B（heritage 含义）和 C（年轻化手法）。", POST_INFO, post_rows(v1), H + Y)
    sheet(wb, "V2_竞品30", "验证 AI 初编：竞品最近 6 个月随机 30 条（每品牌 10），编 B、C、D。", POST_INFO, post_rows(v2), H + Y + N)
    sheet(wb, "V3_用户内容60", "验证 AI 初编：提到 Ya Kun 的用户内容分层随机 60 条，编 A、B、D、E、F、PR、豆浆咖啡。", USER_INFO, user_rows(v3),
          ["A1 相关性", "A2 来源", "A3 商业披露"] + H + N + ["PR 价格参照（选了N1才填）", "SC 豆浆咖啡", "E 老派看法", "F 情感"])
    wb.save(f"{OUTDIR}/coding_v2_{coder}.xlsx")
key = pd.concat([top20.assign(sheet="S3")[["uid", "sheet"]], top30.assign(sheet="S5")[["uid", "sheet"]], t100.assign(sheet="RQ4")[["uid", "sheet"]], xhs.assign(sheet="RQ4b")[["uid", "sheet"]],
                 v1.assign(sheet="V1")[["uid", "sheet"]], v2.assign(sheet="V2")[["uid", "sheet"]], v3.assign(sheet="V3")[["uid", "sheet"]]])
key.to_csv(f"{OUTDIR}/coding_v2_sample_key.csv", index=False, encoding="utf-8-sig")
print(key.sheet.value_counts().to_dict()); print("top20 platforms", top20.platform.value_counts().to_dict(), "| t100", t100.dataset.value_counts().to_dict(), "| v3", v3.dataset.value_counts().to_dict())
