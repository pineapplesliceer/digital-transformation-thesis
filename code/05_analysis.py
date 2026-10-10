from pipeline_utils import RESULTS, cronbach_alpha
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

def main():
    p=RESULTS/"firm_year_panel.csv"
    df=pd.read_csv(p,dtype={"firm_id":str})
    vars_=["ROA","Digital","DigitalDensity","Size","Lev","Growth","Age","CFO"]
    desc=df[vars_].describe().T[["count","mean","std","min","max"]]
    desc.to_csv(RESULTS/"descriptive_statistics.csv",encoding="utf-8-sig")

    dims=[c for c in ["人工智能","大数据","云计算","区块链","数字应用",
                      "AI","BigData","Cloud","Blockchain","DigitalApplication"] if c in df.columns]
    reliability=[]
    if len(dims)>=2:
        alpha=cronbach_alpha(df[dims])
        reliability.append(["Cronbach_alpha",alpha])
        for c in dims:
            reliability.append([f"{c}_vs_Digital_corr",df[c].corr(df["Digital"])])
    pd.DataFrame(reliability,columns=["Test","Value"]).to_csv(
        RESULTS/"reliability_validity.csv",index=False,encoding="utf-8-sig")

    corr=df[vars_].corr()
    corr.to_csv(RESULTS/"correlation_matrix.csv",encoding="utf-8-sig")

    m1=smf.ols("ROA ~ Digital",data=df).fit(cov_type="HC1")
    m2=smf.ols("ROA ~ Digital + Size + Lev + Growth + Age + CFO",data=df).fit(cov_type="HC1")
    m3=smf.ols("ROA ~ Digital + Size + Lev + Growth + Age + CFO + C(year)",data=df).fit(
        cov_type="cluster", cov_kwds={"groups":df["firm_id"]})

    # Robustness: density and lagged Digital
    md=smf.ols("ROA ~ DigitalDensity + Size + Lev + Growth + Age + CFO + C(year)",data=df).fit(
        cov_type="cluster", cov_kwds={"groups":df["firm_id"]})
    lag=df.sort_values(["firm_id","year"]).copy()
    lag["L1_Digital"]=lag.groupby("firm_id")["Digital"].shift(1)
    lag=lag.dropna(subset=["L1_Digital"])
    ml=smf.ols("ROA ~ L1_Digital + Size + Lev + Growth + Age + CFO + C(year)",data=lag).fit(
        cov_type="cluster", cov_kwds={"groups":lag["firm_id"]})

    models={"M1":m1,"M2":m2,"M3":m3,"Density":md,"Lag1":ml}
    lines=[]
    for name,m in models.items():
        for var in ["Digital","DigitalDensity","L1_Digital","Size","Lev","Growth","Age","CFO"]:
            if var in m.params:
                lines.append([name,var,m.params[var],m.bse[var],m.pvalues[var],m.nobs,m.rsquared])
    pd.DataFrame(lines,columns=["Model","Variable","Coef","StdErr","PValue","N","R2"]).to_csv(
        RESULTS/"regression_results.csv",index=False,encoding="utf-8-sig")
    with open(RESULTS/"regression_summary.txt","w",encoding="utf-8") as f:
        for name,m in models.items():
            f.write(f"\n===== {name} =====\n{m.summary()}\n")
    print("Analysis complete. Outputs saved in results/.")

if __name__=="__main__":
    main()
