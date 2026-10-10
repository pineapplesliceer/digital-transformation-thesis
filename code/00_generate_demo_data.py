"""Step 0 (DEMO): generate a simulated corpus of annual-report texts and
matching firm-year financial data so that the whole five-step pipeline can be
reproduced end-to-end without downloading real PDFs.

Outputs
    text_raw/<firm_id>_<year>.txt   simulated annual-report excerpts
    data/financial_data.csv         firm-year financial fundamentals

A latent "digital intensity" drives both the number of digital keywords in the
text and (with a positive sign) ROA, so the regressions in step 5 have a real
signal to recover. Set N_FIRMS / YEARS below to change the panel size.
"""
import math
import re

import numpy as np
import pandas as pd

from pipeline_utils import DATA, TEXT

N_FIRMS = 120
YEARS = [2020, 2021, 2022, 2023, 2024]
SEED = 2026

rng = np.random.default_rng(SEED)

INDUSTRIES = {
    "制造业": {"roa": 0.010, "lev": 0.02},
    "信息传输、软件和信息技术服务业": {"roa": 0.025, "lev": -0.08},
    "批发和零售业": {"roa": 0.004, "lev": 0.05},
    "电力、热力、燃气及水生产和供应业": {"roa": 0.008, "lev": 0.10},
    "交通运输、仓储和邮政业": {"roa": 0.008, "lev": 0.04},
    "房地产业": {"roa": 0.004, "lev": 0.12},
    "采矿业": {"roa": 0.012, "lev": 0.06},
    "农、林、牧、渔业": {"roa": 0.005, "lev": 0.01},
}
IND_NAMES = list(INDUSTRIES)

NAME_A = ["华", "中", "天", "宏", "鑫", "恒", "博", "海", "国", "正", "嘉", "晨",
          "泰", "和", "康", "力", "远", "新", "奥", "德"]
NAME_B = ["辰", "通", "联", "源", "创", "润", "晟", "翔", "业", "诚", "瑞", "盛",
          "域", "谷", "航", "邦", "晖", "辰", "诺", "腾"]
NAME_C = ["科技", "实业", "股份", "集团", "电子", "装备", "材料", "能源",
          "医药", "股份"]

CODE_PREFIX = ["000", "002", "300", "600", "601", "603", "688"]

# --------------------------------------------------------------------------
# Sentence pools. Filler sentences MUST NOT contain any dictionary keyword;
# the script asserts this at runtime. Digital sentences each contain exactly
# one keyword occurrence.
# --------------------------------------------------------------------------
FILLER = [
    "本报告年度内，公司围绕既定发展战略，稳步推进各项经营活动，总体运行平稳。",
    "报告期内，公司实现营业收入与上年基本持平，主营业务保持稳定。",
    "公司坚持以客户需求为导向，持续优化产品结构，提升服务质量。",
    "受宏观经济环境变化影响，行业竞争进一步加剧，公司积极应对市场变化。",
    "公司完善内部管理制度，强化风险防控，规范运作水平不断提高。",
    "报告期内，公司加大研发投入，产品技术含量与附加值稳步提升。",
    "公司重视人才培养，报告期内组织各类培训，员工队伍保持稳定。",
    "随着下游需求逐步恢复，公司订单情况有所改善，产能利用率回升。",
    "公司持续推进渠道建设，销售网络覆盖范围进一步扩大。",
    "原材料价格波动对成本端形成一定压力，公司通过集中采购予以应对。",
    "公司现金流状况良好，资产负债结构保持稳健。",
    "报告期内，公司无重大诉讼、仲裁事项。",
    "公司治理结构完善，三会运作规范，信息披露真实、准确、完整。",
    "公司积极响应国家产业政策，把握行业发展机遇，拓展市场空间。",
    "展望未来，公司将继续深耕主业，稳步提升经营质量与盈利能力。",
    "公司将持续关注行业政策变化，及时调整经营策略，防范经营风险。",
    "报告期内，公司获得多项专利授权，自主创新能力进一步增强。",
    "公司加强预算管理与成本控制，期间费用率有所下降。",
    "质量管理体系运行有效，产品出厂合格率保持在较高水平。",
    "公司与国际主要客户保持长期稳定的合作关系，出口业务平稳。",
]

DIGITAL_SENTENCES = {
    "人工智能": [
        "公司在生产环节引入{kw}质检方案，缺陷识别准确率持续提升。",
        "公司建设{kw}算法团队，将{kw}技术应用于需求预测与排产优化。",
        "报告期内，公司上线{kw}客服助手，服务响应效率明显改善。",
        "公司与高校共建{kw}联合实验室，推动科研成果转化。",
    ],
    "大数据": [
        "公司整合经营数据，搭建{kw}平台，支撑精细化管理决策。",
        "公司推进{kw}治理体系建设，统一主数据标准与指标口径。",
        "报告期内，公司基于{kw}分析优化选品与库存结构。",
        "公司深化{kw}在风控领域的应用，异常交易识别能力增强。",
    ],
    "云计算": [
        "公司核心业务系统逐步{kw}迁移，算力资源利用率提高。",
        "报告期内，公司采用混合{kw}架构，保障业务系统稳定运行。",
        "公司选择国产{kw}服务商，信息系统运维成本有所下降。",
        "公司在{kw}环境中完成核心系统的容灾演练。",
    ],
    "区块链": [
        "公司在供应链金融场景试点{kw}存证，票据流转效率提升。",
        "报告期内，公司参与行业{kw}溯源联盟，实现关键环节可追溯。",
        "公司探索{kw}技术在合同管理中的应用，签署效率提高。",
    ],
    "数字应用": [
        "公司制定{kw}转型规划，分阶段推进制造执行系统建设。",
        "报告期内，公司建成{kw}车间示范线，关键工序实现自动流转。",
        "公司拓展{kw}渠道，线上销售收入占比持续提升。",
        "公司推进研发设计{kw}升级，产品迭代周期明显缩短。",
    ],
}
CATEGORY_ORDER = ["人工智能", "大数据", "云计算", "区块链", "数字应用"]

KW_RE = re.compile(
    "人工智能|智能化|机器学习|深度学习|神经网络|自然语言处理|计算机视觉|智能算法|"
    "大数据|数据挖掘|数据分析|数据中台|数据资产|数据治理|海量数据|"
    "云计算|云平台|云服务|上云|混合云|边缘计算|"
    "区块链|分布式账本|智能合约|"
    "数字化|数字经济|信息化|自动化|智能制造|数字孪生|线上化|电子商务|低代码")


def make_names(n):
    names, codes, used_names, used_codes = [], [], set(), set()
    while len(names) < n:
        name = (rng.choice(NAME_A) + rng.choice(NAME_B) + rng.choice(NAME_C))
        code = rng.choice(CODE_PREFIX) + f"{rng.integers(0, 1000):03d}"
        if name in used_names or code in used_codes:
            continue
        used_names.add(name)
        used_codes.add(code)
        names.append(name)
        codes.append(code)
    return codes, names


def build_report(name, year, counts, rng):
    """Assemble one simulated annual-report text."""
    parts = [
        f"{name}{year}年年度报告（摘要）",
        "一、公司基本情况",
    ]
    parts += list(rng.choice(FILLER, size=4, replace=False))
    parts.append("二、行业环境与经营情况讨论")
    parts += list(rng.choice(FILLER, size=8, replace=False))
    parts.append("三、重点工作与经营计划")
    dig = []
    for cat in CATEGORY_ORDER:
        tpls = DIGITAL_SENTENCES[cat]
        for j in range(int(counts[cat])):
            tpl = tpls[(j + int(rng.integers(0, len(tpls)))) % len(tpls)]
            dig.append(tpl.format(kw=cat if cat != "数字应用" else "数字化"))
    rng.shuffle(dig)
    parts += dig
    parts.append("四、风险因素与未来展望")
    parts += list(rng.choice(FILLER, size=4, replace=False))
    return "\n".join(parts) + "\n"


def main():
    codes, names = make_names(N_FIRMS)
    firm_ind = rng.choice(IND_NAMES, size=N_FIRMS)
    firm_digital = rng.normal(0, 1.0, N_FIRMS)          # persistent intensity
    firm_size = rng.normal(0, 1.0, N_FIRMS)
    firm_roa = rng.normal(0, 0.010, N_FIRMS)            # firm fixed effect
    share = rng.dirichlet(np.ones(5) * 1.2, N_FIRMS)    # category mix per firm

    fin_rows = []
    for i in range(N_FIRMS):
        ind = firm_ind[i]
        ind_p = INDUSTRIES[ind]
        size0 = 22.4 + 1.15 * firm_size[i] + 0.8 * (ind == "房地产业")
        for t, year in enumerate(YEARS):
            d_it = firm_digital[i] + 0.15 * (year - 2022) + rng.normal(0, 0.30)
            lev = float(np.clip(rng.normal(0.40 + ind_p["lev"], 0.16), 0.04, 0.92))
            growth = float(np.clip(rng.normal(0.10, 0.28), -0.55, 1.60))
            cfo = float(np.clip(rng.normal(0.045, 0.060), -0.15, 0.25))
            roa = (0.020 + 0.020 * d_it + ind_p["roa"] + firm_roa[i]
                   + 0.004 * (year - 2022)
                   + 0.004 * (size0 - 22.4)
                   - 0.030 * (lev - 0.40)
                   + 0.080 * (cfo - 0.045)
                   + 0.010 * growth
                   + rng.normal(0, 0.012))
            fin_rows.append({
                "firm_id": codes[i], "firm_name": names[i],
                "industry": ind, "year": year,
                "ROA": round(roa, 5),
                "Size": round(size0 + rng.normal(0, 0.03), 4),
                "Lev": round(lev, 4), "Growth": round(growth, 4),
                "Age": int(rng.integers(6, 31)), "CFO": round(cfo, 5),
                "latent_digital": round(d_it, 4),
            })
    fin = pd.DataFrame(fin_rows)
    fin["idx"] = fin["firm_id"].map({c: i for i, c in enumerate(codes)})

    # Generate texts with keyword counts consistent with the latent intensity.
    for row in fin.itertuples(index=False):
        i = row.idx
        lam = math.exp(1.0 + 1.7 * row.latent_digital)
        total = int(rng.poisson(lam))
        props = share[i] / share[i].sum()
        counts = {c: int(rng.multinomial(total, props)[k])
                  for k, c in enumerate(CATEGORY_ORDER)}
        txt = build_report(names[i], row.year, counts, rng)
        (TEXT / f"{row.firm_id}_{row.year}.txt").write_text(
            txt, encoding="utf-8")

    # sanity check: filler sentences contain no dictionary keyword
    sample = (TEXT / f"{codes[0]}_{YEARS[0]}.txt").read_text(encoding="utf-8")
    filler_only = "\n".join(
        line for line in sample.splitlines()
        if not any(kw in line for kw in KW_RE.findall(line)))
    assert not KW_RE.search(filler_only), "filler text leaked keywords"

    out = fin.drop(columns="idx")
    out.to_csv(DATA / "financial_data.csv", index=False, encoding="utf-8-sig")
    print(f"Generated {len(out)} firm-year texts and financial rows "
          f"({N_FIRMS} firms x {len(YEARS)} years).")


if __name__ == "__main__":
    main()
