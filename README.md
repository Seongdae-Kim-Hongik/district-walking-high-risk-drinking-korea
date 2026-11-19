# District walking, drinking venues, and high-risk drinking among drinkers in South Korea, 2011-2024

Analysis code for the manuscript

> Kim S. *Do districts where more adults walk have fewer high-risk drinkers? Fourteen years of small-area survey data from South Korea.* Manuscript under review.

Archived version: Zenodo, https://doi.org/10.5281/zenodo.24359134 (v1.0.0), MIT license.

## Contents

Code only. The processed district-year data (master table, analytic panel, survey outcomes, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/HDRK/` | Covariates with expected directions, controls, negative controls and model settings (`sets_HDRK_std3.json`) and the model chain (`run_fh_chain.sh`) |
| `04_분석/HDRK/MS/build/` | `numbers_hdrk.py` (reads the result tables and computes every reported number), `figs_hdrk.py` (figures), `build_refs_hdrk.py` and `refs_hdrk.json` (reference metadata from PubMed and Crossref), and document helpers. The manuscript text generator is not included. |

Folder names are in Korean because the source tables are Korean; each script has a short header describing what it does.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- Outcome: Korea Community Health Survey (Korea Disease Control and Prevention Agency), district prevalence of high-risk drinking among adults who drank in the previous year (at least seven standard drinks for men or five for women on one occasion at least twice a week), age-sex-standardized to the 2005 projected population, with standard errors and numbers of respondents, 2011-2024 (KOSIS table DT_H_DR_HIGH). Auxiliary outcomes: high-risk drinking among all adults (DT_117075_H_DR_HIGH_WH) and monthly drinking (DT_H_DR_MONTH).
- Covariates: Community Health Survey (walking, moderate-or-vigorous physical activity, perceived stress, current smoking as a sensitivity covariate); public sports facility register and community exercise facility statistics; Ministry of the Interior and Safety local licensing data (general restaurants, entertainment bars and singing bars open at year end); basic livelihood security statistics (invalid 2021-2023 values set to missing and interpolated); population and housing census (tertiary education); and KOSIS local indicators (controls and negative controls).
- Mortality comparison: Statistics Korea cause-of-death statistics (liver disease and suicide), standardized mortality ratios 2011-2024.

## Pipeline

Set `ST_DATA_ROOT` to local copies of the public source files and `ST_GRAPH` to the district contact graph.

| Step | Script | Output |
|---|---|---|
| 1 | `99c_extra_canonical_pool_hdrk.py` | Benefit receipt, tertiary education, general restaurants and entertainment and singing bars, by district code |
| 2 | `99HD_hdrk_fh_prep.py` | Survey outcome and auxiliary outcomes on the logit scale with delta-method sampling variances and effective sample sizes |
| 3 | `99HD2_hdrk_linkage_prep.py` | Standardized mortality ratios for liver disease and suicide |
| 4 | `80_build_disease_panel_v.py HDRK` (`ST_VER=std3`) | Transformed and standardized covariates, filling and variance inflation factors |
| 5 | `81fh_hdrk.R HDRK` | Spatiotemporal Fay-Herriot models (R-INLA): screening indices, set comparison, main model, negative controls, windows, subset models, Knorr-Held II-IV, between/within decomposition, lags, leave-one-province-out, alternative likelihoods, graph and prior, auxiliary outcomes, restricted spatial regression, regional slopes, influential observations, smoking collinearity, urbanization adjustment, mortality overlap, follow-up of associations opposite to the expected direction |
| 6 | `99HD4_hdrk_maps.py` | District maps |
| 7 | `04_분석/HDRK/MS/build/numbers_hdrk.py`, `figs_hdrk.py` | Reported numbers and figures |

`run_fh_chain.sh` runs step 5 in parallel parts. Software: R 4.6.0 with R-INLA; Python 3.9 with pandas, numpy, geopandas and matplotlib.

## License

MIT (see `LICENSE`).
