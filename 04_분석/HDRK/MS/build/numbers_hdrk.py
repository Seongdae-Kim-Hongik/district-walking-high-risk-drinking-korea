# Reads result tables and computes every reported number.
import os, json, unicodedata
import pandas as pd, numpy as np
NFC = lambda s: unicodedata.normalize("NFC", str(s))
HERE = os.path.dirname(os.path.abspath(__file__)); AN = os.path.normpath(os.path.join(HERE, "..", "..", "..")); ROOT = os.path.dirname(AN)
R = os.path.join(AN, "HDRK", "results_std3")
rd = lambda f: pd.read_csv(os.path.join(R, f))
D = lambda r: dict(OR=float(r.OR), lo=float(r.lo), hi=float(r.hi), cred=bool(r.cred))
N = {}
FO = pd.read_csv(os.path.join(ROOT, "02_패널", "HDRK_fh_outcomes.csv"), encoding="utf-8-sig")
assert len(FO) == 3206 and FO.SR.notna().all()
N["n_cells"] = len(FO); N["n_resp_total"] = int(FO.N.sum()); N["n_resp_median"] = int(FO.N.median()); N["n_resp_min"] = int(FO.N.min())
ym = FO.groupby("year").SR.mean(); N["sr"] = {int(y): round(v, 1) for y, v in ym.items()}
p = FO.groupby("fbd_region").SR.mean(); N["p10"] = round(p.quantile(.1), 1); N["p90"] = round(p.quantile(.9), 1); N["sr_dist_min"] = round(p.min(), 1); N["sr_dist_max"] = round(p.max(), 1)
N["se_median"] = round(FO.SR_SE.median(), 1); N["sr_mean_all"] = round(float(FO.SR.mean()), 1)
s0 = rd("S0_screen.csv").iloc[0]; N["moran"] = round(s0.moran_I_pooled_logitSR, 2); N["moran_ymin"] = round(s0.moran_I_year_min, 2); N["moran_ymax"] = round(s0.moran_I_year_max, 2)
N["persist"] = round(s0.persistence_rank_rho, 2); N["phi_forced"] = round(s0.phi_forced_only, 2); N["p9010"] = round(s0.P90_P10_SR, 2)
N["kendallW"] = round(rd("S6_kendallW.csv").kendall_W[0], 2)
my = rd("S6_moran_year.csv").set_index("year"); N["moran_year"] = {int(y): round(v, 2) for y, v in my.moran_I.items()}; N["sr_popw"] = {int(y): round(v, 1) for y, v in my.SR_popweighted.items()}
f3 = rd("S3_main_fit.csv").iloc[0]; N["phi_main"] = round(f3.phi, 2); N["n_hot"] = int(f3.n_hotspot); N["n_cold"] = int(f3.n_coldspot); N["resid_moran"] = round(f3.resid_moran_I, 2); N["resid_moran_p"] = round(f3.resid_moran_p, 2)
N["largest_hot"] = int(f3.largest_hot); N["largest_cold"] = int(f3.largest_cold); N["or_sp_min"] = round(f3.OR_min, 2); N["or_sp_max"] = round(f3.OR_max, 2)
sp = rd("S3_spatial_OR.csv"); sp["sido"] = sp.sido.map(NFC); sp["fbd_region"] = sp.fbd_region.map(NFC)
N["hot_sido"] = sp[sp["class"] == "hotspot"].sido.value_counts().to_dict(); N["cold_sido"] = sp[sp["class"] == "coldspot"].sido.value_counts().to_dict()
iscounty = sp.fbd_region.str.endswith("군"); N["hot_county"] = int((iscounty & (sp["class"] == "hotspot")).sum()); N["cold_county"] = int((iscounty & (sp["class"] == "coldspot")).sum())
vf = rd("S3_vs_forced_only.csv").iloc[0]; N["sp_rho_vs_forced"] = round(vf.spearman_spatial_OR, 2); N["sd_main"] = round(vf.sd_logOR_main, 3); N["sd_forced"] = round(vf.sd_logOR_forced, 3)
N["hot_forced"] = int(vf.hot_forced); N["cold_forced"] = int(vf.cold_forced)
vp = rd("S3_varpart.csv").set_index("component").share; N["vp"] = {k: round(100 * v, 0) for k, v in vp.items()}
nt = vp.drop("temporal"); nt = nt / nt.sum(); N["vp_notime"] = {k: round(100 * v, 0) for k, v in nt.items()}
m = rd("S3_main_OR.csv").set_index("cov"); N["main"] = {k: D(r) for k, r in m.iterrows()}
mv = rd("S7_multiverse_summary.csv").set_index("cov"); N["mv"] = {k: dict(cred=float(r.cred_frac), sign=float(r.sign_agree), robust=bool(r.robust), n=int(r.n_specs), med=float(r.OR_median)) for k, r in mv.iterrows()}
kh = rd("S8_KH.csv"); N["kh"] = {f"{r.model}|{r['cov']}": D(r) for _, r in kh.iterrows()}; N["kh_waic"] = kh.groupby("model").WAIC.first().to_dict()
ROB = [k for k in mv.index if mv.loc[k, "robust"] and kh[(kh["cov"] == k) & kh.model.isin(["KH_II", "KH_IV"])].cred.all()]
assert ROB == ["walking_practice_rate", "ext__drinking_venues_per10k", "perceived_stress_rate", "tertiary_educated_share"], ROB
N["robust"] = ROB
bw = rd("S9_between_within.csv"); N["bw"] = {f"{r['cov']}|{r.component}": D(r) for _, r in bw.iterrows()}
nc = rd("S3_negcontrol.csv"); N["neg"] = {r["cov"]: D(r) for _, r in nc.iterrows()}; assert all(v["cred"] for v in N["neg"].values())
s2 = rd("S2_setcompare.csv").set_index("set").WAIC; N["waic"] = s2.round(1).to_dict()
lo1 = rd("S11_leave_one_sido.csv"); N["loo"] = lo1.groupby("cov").cred.sum().astype(int).to_dict(); N["loo_n"] = int(lo1.left_out.nunique())
N["rev_n"] = len(rd("S44_reverse_posthoc.csv")) if os.path.exists(os.path.join(R, "S44_reverse_posthoc.csv")) else 0
ye = rd("S3_year_effect.csv").set_index("year"); N["rw1"] = {int(y): round(v, 3) for y, v in ye.rw1.items()}
w = rd("S4_window_OR.csv"); N["win"] = {f"{r.window}|{r['cov']}": D(r) for _, r in w.iterrows()}
l = rd("S10_lag.csv"); N["lag"] = {f"{r.lag}|{r['cov']}": D(r) for _, r in l.iterrows()}
li = rd("S12_likelihood.csv"); N["lik"] = {f"{r.likelihood}|{r['cov']}": D(r) for _, r in li.iterrows()}
g13 = rd("S13_graph_prior.csv"); N["s13"] = {f"{r.variant}|{r['cov']}": D(r) for _, r in g13.iterrows()}
rs = rd("S16_RSR.csv"); N["rsr"] = {r["cov"]: D(r) for _, r in rs.iterrows()}
rg = rd("S17_region_slopes.csv"); N["reg"] = {f"{r.covariate}|{r.region}": D(r) | {"dW": float(r.dWAIC_vs_common)} for _, r in rg.iterrows()}
inf = rd("S18_influence.csv"); N["infl_n"] = int(inf.variant.iloc[0].split("_")[1]); N["infl"] = {r["cov"]: D(r) for _, r in inf.iterrows()}
cv = rd("S5_covid.csv"); N["covid"] = {r["cov"]: D(r) for _, r in cv.iterrows()}
sm = rd("S19_smoking_collinearity.csv"); N["smk"] = {r["cov"]: D(r) for _, r in sm.iterrows()}; s19 = sm.iloc[0]
N["smk_rho_area"] = float(s19.spearman_area_HDRK_smoking); N["smk_rho_cell"] = float(s19.spearman_cell); N["smk_rho_within"] = float(s19.spearman_within); N["smk_maxvif"] = float(s19.maxVIF_plus); N["smk_waic"] = float(s19.WAIC)
vif = rd("S19_vif.csv"); N["vif_main_max"] = float(vif.VIF_main.max()); N["vif_smk"] = float(vif.loc[vif["var"] == "current_smoking_rate", "VIF_main_plus_smoking"].iloc[0])
ur = rd("S20_urbanicity.csv"); N["urb"] = {r["cov"]: D(r) for _, r in ur.iterrows()}
ax = rd("S14_aux_outcomes_OR.csv"); N["aux"] = {f"{r.outcome}|{r['cov']}": D(r) for _, r in ax.iterrows()}
axs = rd("S14_aux_summary.csv").iloc[0]; N["auxs"] = {k: float(v) for k, v in axs.items()}
lk = rd("S21_mortality_linkage.csv").set_index("mortality"); N["link"] = {k: {c: (None if pd.isna(v) else float(v)) for c, v in r.items()} for k, r in lk.iterrows()}
lr = rd("S21_linkage_by_region.csv"); lr["fbd_region"] = lr.fbd_region.map(NFC); q = lambda s: s >= s.quantile(.75)
N["triple"] = lr[q(lr.OR) & q(lr.SIR_LIVD) & q(lr.SIR_SUIC)].fbd_region.tolist(); assert len(N["triple"]) == int(N["link"]["all_three_topQ"]["n_topQ_both"])
top = sp.sort_values("OR", ascending=False).head(5); N["top5"] = [(r.fbd_region, round(r.OR, 2)) for _, r in top.iterrows()]
json.dump(N, open(os.path.join(HERE, "numbers_hdrk.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("robust", ROB, "| hot", N["n_hot"], N["hot_sido"], "| triple", N["triple"])
