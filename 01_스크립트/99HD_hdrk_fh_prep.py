#!/bin/bash
# Survey outcome (high-risk drinking among current drinkers) and auxiliary outcomes: logit, delta-method sampling variance, effective sample sizes.
import os, unicodedata
import numpy as np, pandas as pd
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.normpath(os.path.join(HERE, ".."))
M = pd.read_parquet(os.path.join(ROOT, "02_패널", "MASTER_시군구_연도_wide.parquet")); M.columns = [NFC(c) for c in M.columns]
M = M[(M.year >= 2011) & (M.year <= 2024)].copy(); M["fbd_region"] = M.fbd_region.map(NFC)
tb = "kchs__DT_H_DR_HIGH__"
d = pd.DataFrame({"year": M.year.values, "fbd_region": M.fbd_region.values, "population": M.population.astype(float).values})
for it in ["SR", "SR_SE", "N", "CR", "CR_SE"]: d[it] = M[tb + it].astype(float).values
for nm, col in [("wh", "kchs__DT_117075_H_DR_HIGH_WH__"), ("mon", "kchs__DT_H_DR_MONTH__")]:
    d[f"{nm}_SR"] = M[col + "SR"].astype(float).values; d[f"{nm}_SE"] = M[col + "SR_SE"].astype(float).values
assert len(d) == 229 * 14
assert d[["SR", "SR_SE", "N", "CR", "CR_SE"]].notna().all().all() and (d.SR > 0).all() and (d.SR < 100).all()
n0 = int((d.SR_SE <= 0).sum()); d["SE_used"] = d.SR_SE.clip(lower=0.05); d["CRSE_used"] = d.CR_SE.clip(lower=0.05)
lg = lambda pp: np.log(pp / (1 - pp))
p = d.SR / 100; d["y_logit"] = lg(p); d["v_logit"] = (d.SE_used / 100) ** 2 / (p * (1 - p)) ** 2
pc = d.CR / 100; d["y_logit_cr"] = lg(pc); d["v_logit_cr"] = (d.CRSE_used / 100) ** 2 / (pc * (1 - pc)) ** 2
d["n_eff"] = np.maximum(np.round(p * (1 - p) / (d.SE_used / 100) ** 2), 10); d["y_eff"] = np.round(p * d.n_eff)
for nm in ["wh", "mon"]:
    q = d[f"{nm}_SR"] / 100; d[f"y_logit_{nm}"] = lg(q); d[f"v_logit_{nm}"] = (d[f"{nm}_SE"].clip(lower=0.05) / 100) ** 2 / (q * (1 - q)) ** 2
print(f"[99HD] rows {len(d)} · SE≤0 칸 {n0} · SR {d.SR.min():.1f}-{d.SR.max():.1f} · SE 중앙 {d.SR_SE.median():.2f} · n_eff 중앙 {d.n_eff.median():.0f} · N 중앙 {d.N.median():.0f}")
print(f"[99HD] 보조 WH 관측 {int(d.wh_SR.notna().sum())} · MONTH 관측 {int(d.mon_SR.notna().sum())}; 결측 WH 지역 {sorted(d.loc[d.wh_SR.isna(), 'fbd_region'].unique())}")
print("[99HD] 연도별 인구가중 SR:", d.groupby("year").apply(lambda g: round(np.average(g.SR, weights=g.population), 2)).to_dict())
fp = os.path.join(ROOT, "02_패널", "HDRK_fh_outcomes.csv"); d.to_csv(fp, index=False, encoding="utf-8-sig"); print("[99HD] 저장", fp, d.shape)
