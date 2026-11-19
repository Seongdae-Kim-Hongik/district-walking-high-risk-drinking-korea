#!/bin/bash
# District standardized mortality ratios for liver disease and suicide, 2011-2024.
import os, sqlite3, unicodedata
import pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DB = os.environ.get("ST_SQLITE", "district_panel.sqlite")
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
X = pd.read_sql("SELECT tag, year, fbd_region, cases, E FROM disease_panel WHERE tag IN ('LIVD','SUIC') AND year BETWEEN 2011 AND 2024", con); X["fbd_region"] = X.fbd_region.map(NFC)
g = X.groupby(["tag", "fbd_region"])[["cases", "E"]].sum().reset_index(); g["SIR"] = g.cases / g.E
W = g.pivot(index="fbd_region", columns="tag", values="SIR").rename(columns={"LIVD": "SIR_LIVD", "SUIC": "SIR_SUIC"}).reset_index()
c = g.pivot(index="fbd_region", columns="tag", values="cases").rename(columns={"LIVD": "deaths_LIVD", "SUIC": "deaths_SUIC"}).reset_index()
W = W.merge(c, on="fbd_region"); assert len(W) == 229 and W.notna().all().all()
fp = os.path.join(ROOT, "02_패널", "HDRK_linkage_mort_261113.csv"); W.to_csv(fp, index=False, encoding="utf-8-sig")
print("[99HD2]", W.describe().round(3).to_string()); print("저장", fp)
