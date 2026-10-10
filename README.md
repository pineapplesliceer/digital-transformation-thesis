# 基于年报文本挖掘的企业数字化转型测度及其对企业绩效的影响研究

> **课程**：大数据智能分析理论方法
> **班级**：大数据管理与应用1班　**专业**：大数据管理与应用
> **姓名**：刘昕卓　**学号**：202364019

一套完整的「文本挖掘 → 指标测度 → 面板构建 → 实证回归」研究材料，包含**预演论文全文（Word）、五步流水线 Python 脚本、企业-年度面板与全部结果表、数据来源说明**，可一键复现。

---

## 一、研究概述

以企业年报文本为素材，按 **文本采集 → 文本清洗 → 词典测度 → 面板构建 → 回归分析** 五步流水线构建企业数字化转型测度（五维度 33 关键词词频法），并在 **120 家企业 × 5 年（2020—2024，共 600 个公司—年度观测）** 的平衡面板上检验其与经营绩效（ROA）的关系。

**核心结果**

| 指标 | 结果 |
|------|------|
| 测度信度 | 五维量表 Cronbach's α = **0.784** |
| 基准回归（M3） | Digital 系数 **0.0125**（p<0.01，企业聚类稳健标准误，R² = 0.603） |
| 替换测度 | DigitalDensity 系数 **0.0073**（p<0.01，R² = 0.501） |
| 滞后一期 | L1.Digital 系数 **0.0114**（p<0.01，N = 480，R² = 0.516） |

经济含义：Digital 每提高一个单位（约对应词频扩大 1.7 倍），ROA 平均提高约 1.25 个百分点，相当于样本 ROA 均值（2.97%）的 42%。

---

## 二、仓库结构

```
├── paper/            预演毕业论文全文（Word，含封面、目录、正文、参考文献）
├── code/             五步流水线脚本（可复现）
│   ├── 00_generate_demo_data.py   # [数据] 生成模拟年报语料与财务数据
│   ├── 01_extract_text.py         # [第1步] PDF 年报 → 纯文本（pypdf 逐页抽取）
│   ├── 02_clean_text.py           # [第2步] 文本清洗（去噪 / 正则化 / 去异常字符）
│   ├── 03_nlp_measure.py          # [第3步] 五维度词典词频统计 → Digital / DigitalDensity
│   ├── 04_merge_panel.py          # [第4步] 测度 × 财务数据 → 公司-年度平衡面板
│   ├── 05_analysis.py             # [第5步] 描述统计 / 信度效度 / 相关矩阵 / 多元回归
│   ├── pipeline_utils.py          # 公共配置：目录、文件名解析、缩尾、Cronbach's α
│   └── requirements.txt
├── data/             词典与数据
│   ├── digital_dictionary.csv     # 数字化词典（5 维度 33 关键词）
│   ├── financial_data.csv         # 公司-年度财务数据（含生成用潜在强度列）
│   └── firm_year_panel.xlsx       # 测量结果表：企业-年度面板（Excel 版）
└── results/          流水线真实运行输出
    ├── measurement_results.csv    # 每份文本的分维度词频与测度值
    ├── firm_year_panel.csv        # 面板数据（CSV 版，与 xlsx 内容一致）
    ├── descriptive_statistics.csv # 描述性统计
    ├── reliability_validity.csv   # Cronbach's α 与维度-总量相关
    ├── correlation_matrix.csv     # Pearson 相关系数矩阵
    ├── regression_results.csv     # 回归系数表（M1/M2/M3/Density/Lag1）
    └── regression_summary.txt     # 回归完整输出
```

---

## 三、如何复现

```bash
pip install -r code/requirements.txt
cd code
python 00_generate_demo_data.py   # 生成 text_raw/*.txt 与 data/financial_data.csv（种子 2026，可复现）
python 02_clean_text.py           # 清洗 → text_clean/
python 03_nlp_measure.py          # 词频测度 → results/measurement_results.csv
python 04_merge_panel.py          # 合并面板 → results/firm_year_panel.csv
python 05_analysis.py             # 全部结果表 → results/
```

> **使用真实年报**：将 PDF（命名 `股票代码_年份.pdf`）放入 `raw_reports/`，先运行 `01_extract_text.py`，再依次执行 02 → 05。
> 模拟语料文件（`text_raw/`、`text_clean/`，各 600 个 txt）不随仓库分发，由 `00_generate_demo_data.py` 一键重建（随机种子固定，结果完全可复现）。

---

## 四、数据来源说明

| 文件 | 来源与处理步骤 |
|------|----------------|
| `data/digital_dictionary.csv` | 参照吴非等（2021，《管理世界》）的五维度框架整理的企业数字化关键词词典，共 5 类 33 词，两列（category, keyword）：人工智能、大数据、云计算、区块链、数字应用。 |
| `data/financial_data.csv` | 由 `00_generate_demo_data.py` 以随机种子 2026 模拟生成的公司-年度财务数据（ROA / Size / Lev / Growth / Age / CFO），生成时植入「数字化强度 → ROA」的真实效应，用于验证流水线的估计能力。 |
| `text_raw/*.txt`（不入库） | 由 00 脚本按真实年报摘要结构（公司概况 → 行业讨论 → 重点工作 → 风险展望）模拟生成，各维度关键词出现次数由潜在数字化强度经泊松抽样决定。 |
| `results/measurement_results.csv` | `03_nlp_measure.py` 对清洗后文本逐份统计五个维度的关键词词频，并计算 Digital = ln(1 + 关键词总数)、DigitalDensity = 关键词总数 / 文本字数 × 10000。 |
| `results/firm_year_panel.csv` / `data/firm_year_panel.xlsx` | `04_merge_panel.py` 将测度结果与财务数据按「股票代码_年份」合并为平衡面板（120 家企业 × 5 年 = 600 条），并做 1%/99% 分位缩尾。 |
| `results/descriptive_statistics.csv` | `05_analysis.py` 对 ROA、Digital、DigitalDensity、Size、Lev、Growth、Age、CFO 计算样本量、均值、标准差、最小值、最大值。 |
| `results/reliability_validity.csv` | 五个维度词频作为「题项」计算 Cronbach's α，并计算各维度与总测度的相关系数作为结构效度证据。 |
| `results/correlation_matrix.csv` | 主要变量的 Pearson 相关系数矩阵及显著性。 |
| `results/regression_results.csv` / `regression_summary.txt` | 五个模型的最小二乘估计结果：M1（仅 Digital）、M2（加控制变量）、M3（再加年份固定效应 + 企业层面聚类稳健标准误）、Density（替换测度）、Lag1（解释变量滞后一期，N=480）。 |

**说明**：受课程作业条件限制，年报文本为按真实披露结构模拟生成的教学语料，研究结论定位为**方法论演示**，不构成对真实市场的因果估计。

---

## 五、主要参考文献

1. 吴非, 胡慧芷, 林慧妍, 等. 企业数字化转型与资本市场表现——来自股票流动性的经验证据[J]. 管理世界, 2021, 37(7): 130-144.
2. 袁淳, 肖土盛, 耿春晓, 等. 数字化转型与企业分工：专业化还是纵向一体化[J]. 中国工业经济, 2021(9): 137-155.
3. 戚聿东, 肖旭. 数字经济时代的企业管理变革[J]. 管理世界, 2020, 36(6): 135-152.
4. 刘淑春, 闫津臣, 张思雪, 等. 企业管理数字化变革能提升投入产出效率吗[J]. 管理世界, 2021, 37(5): 170-190.
5. Loughran T, McDonald B. When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks[J]. Journal of Finance, 2011, 66(1): 35-65.
