from pipeline_utils import DATA, RESULTS, CLEAN, parse_report_name
import pandas as pd
import math

def main():
    dictionary = pd.read_csv(DATA/"digital_dictionary.csv")
    groups = dictionary.groupby("category")["keyword"].apply(list).to_dict()
    files = sorted(CLEAN.glob("*.txt"))
    if not files:
        demo = DATA/"measurement_results_DEMO.csv"
        if demo.exists():
            pd.read_csv(demo).to_csv(RESULTS/"measurement_results.csv", index=False, encoding="utf-8-sig")
            print("No real cleaned reports. Copied DEMO NLP measurement to results/measurement_results.csv")
            return
        raise SystemExit("No cleaned reports and no DEMO measurement file.")
    rows=[]
    for p in files:
        firm, year = parse_report_name(p)
        txt=p.read_text(encoding="utf-8",errors="ignore")
        counts={cat:sum(txt.count(k) for k in words) for cat,words in groups.items()}
        total=sum(counts.values())
        total_chars=max(1, len(txt))
        row={"firm_id":firm,"year":year,**counts,
             "digital_words":total,"total_words":total_chars,
             "Digital":math.log1p(total),
             "DigitalDensity":math.log1p(10000*total/total_chars)}
        rows.append(row)
    out=pd.DataFrame(rows).sort_values(["firm_id","year"])
    out.to_csv(RESULTS/"measurement_results.csv",index=False,encoding="utf-8-sig")
    print("Saved", RESULTS/"measurement_results.csv", "rows:", len(out))

if __name__ == "__main__":
    main()
