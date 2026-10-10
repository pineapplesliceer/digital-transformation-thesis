from pipeline_utils import TEXT, CLEAN, parse_report_name
import re

NEGATIVE_NOISE = [
    r"第\s*\d+\s*页", r"年度报告", r"公司代码[:：]?\s*\d{6}"
]

def clean_text(s):
    s = s.replace("\u3000", " ")
    for pat in NEGATIVE_NOISE:
        s = re.sub(pat, " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9%.,，。；;：:（）()\- ]", "", s)
    return s.strip()

def main():
    files = sorted(TEXT.glob("*.txt"))
    if not files:
        print("No extracted TXT files found; skip cleaning in DEMO mode.")
        return
    for p in files:
        firm, year = parse_report_name(p)
        out = clean_text(p.read_text(encoding="utf-8", errors="ignore"))
        (CLEAN/f"{firm}_{year}.txt").write_text(out, encoding="utf-8")
    print(f"Cleaned {len(files)} reports.")

if __name__ == "__main__":
    main()
