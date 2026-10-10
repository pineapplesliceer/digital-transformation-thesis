"""Shared configuration and helpers for the five-step text-mining pipeline.

Directory layout (created automatically, relative to the project root):
    raw_reports/   step 1 input  : PDF annual reports named like 000001_2024.pdf
    text_raw/      step 1 output : extracted plain text (000001_2024.txt)
    text_clean/    step 2 output : cleaned plain text
    data/          dictionaries, financial data, demo data
    results/       step 3-5 outputs (measurement, panel, tables)
"""
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RAW = BASE_DIR / "raw_reports"
TEXT = BASE_DIR / "text_raw"
CLEAN = BASE_DIR / "text_clean"
DATA = BASE_DIR / "data"
RESULTS = BASE_DIR / "results"

for _d in (RAW, TEXT, CLEAN, DATA, RESULTS):
    _d.mkdir(parents=True, exist_ok=True)


def parse_report_name(path):
    """'000001_2024.pdf' -> ('000001', 2024)."""
    stem = Path(path).stem
    firm, year = stem.split("_")
    return firm, int(year)


def winsorize_series(s, lower=0.01, upper=0.99):
    """Winsorize a numeric series at the given quantiles."""
    s = pd.to_numeric(s, errors="coerce")
    lo, hi = s.quantile(lower), s.quantile(upper)
    return s.clip(lo, hi)


def cronbach_alpha(df):
    """Cronbach's alpha for a dataframe of item columns (rows = observations)."""
    df = df.dropna()
    k = df.shape[1]
    if k < 2 or len(df) < 2:
        return float("nan")
    item_var = df.var(axis=0, ddof=1).sum()
    total_var = df.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return float("nan")
    return float(k / (k - 1) * (1 - item_var / total_var))
