from pipeline_utils import DATA, RESULTS, winsorize_series
import pandas as pd

def main():
    measure = RESULTS/"measurement_results.csv"
    finance = DATA/"financial_data.csv"

    # Fully runnable DEMO fallback.
    if not finance.exists():
        demo = pd.read_csv(DATA/"firm_year_panel_DEMO.csv", dtype={"firm_id":str})
        demo["firm_id"] = demo["firm_id"].str.zfill(6)
        demo.to_csv(RESULTS/"firm_year_panel.csv",index=False,encoding="utf-8-sig")
        print("financial_data.csv not found; using supplied DEMO panel.")
        return

    m=pd.read_csv(measure,dtype={"firm_id":str})
    f=pd.read_csv(finance,dtype={"firm_id":str})
    m["firm_id"]=m["firm_id"].str.zfill(6); f["firm_id"]=f["firm_id"].str.zfill(6)
    required={"firm_id","year","ROA","Size","Lev","Growth","Age","CFO"}
    missing=required-set(f.columns)
    if missing:
        raise SystemExit(f"financial_data.csv missing columns: {sorted(missing)}")
    panel=f.merge(m,on=["firm_id","year"],how="inner",validate="one_to_one")
    for c in ["ROA","Size","Lev","Growth","Age","CFO","Digital","DigitalDensity"]:
        panel[c]=winsorize_series(panel[c])
    panel.to_csv(RESULTS/"firm_year_panel.csv",index=False,encoding="utf-8-sig")
    print("Merged panel rows:",len(panel))

if __name__ == "__main__":
    main()
