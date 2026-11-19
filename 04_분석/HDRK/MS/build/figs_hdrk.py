# Figures.
import os, shutil
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from PIL import Image
import content_hdrk as C
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(HERE), "out", "Figures"); os.makedirs(OUT, exist_ok=True)
AN = os.path.normpath(os.path.join(HERE, "..", "..")); N = C.N
im = Image.open(os.path.join(AN, "figs", "Fig_maps_HDRK.tiff")); im.save(os.path.join(OUT, "Figure1.tiff"), compression="tiff_lzw", dpi=(600, 600))
shutil.copy(os.path.join(AN, "figs", "Fig_maps_HDRK.png"), os.path.join(OUT, "Figure1.png"))
plt.rcParams.update({"font.family": "Arial", "font.size": 11})
def save(fig, k):
    for ext, dpi in (("png", 300), ("tiff", 600)): fig.savefig(os.path.join(OUT, f"Figure{k}.{ext}"), dpi=dpi, pil_kwargs={"compression": "tiff_lzw"} if ext == "tiff" else None, bbox_inches="tight")
VARS = [v for g, vs in C.GROUPS[:3] for v in vs]
SER = [("Main model", lambda v: N["main"][v], "#1f4e79", "o"), ("Knorr-Held type IV", lambda v: N["kh"][f"KH_IV|{v}"], "#2e8b57", "s"),
       ("Between districts", lambda v: N["bw"][f"{v}|between"], "#b8860b", "^"), ("Within districts", lambda v: N["bw"][f"{v}|within"], "#8b1a1a", "v"),
       ("Adding current smoking", lambda v: N["smk"][v], "#6a3d9a", "D"), ("Adding county status and density", lambda v: N["urb"][v], "#d95f02", "P")]
fig, ax = plt.subplots(figsize=(8.5, 9.5)); y0 = np.arange(len(VARS))[::-1]; off = np.linspace(-0.34, 0.34, len(SER))
for (lab, f, col, mk), dy in zip(SER, off):
    for v, y in zip(VARS, y0):
        d = f(v); ax.plot([d["lo"], d["hi"]], [y + dy, y + dy], color=col, lw=1.4)
        ax.plot(d["OR"], y + dy, marker=mk, color=col, mfc=col if d["cred"] else "white", ms=6.5, label=lab if v == VARS[0] else None)
ax.axvline(1, color="#555", lw=0.8, ls="--")
ax.set_yticks(y0); ax.set_yticklabels([C.LABEL[v] + (" †" if v in N["robust"] else "") for v in VARS]); ax.set_xscale("log")
ticks = [0.70, 0.80, 0.90, 1.0, 1.10, 1.20]; ax.set_xticks(ticks); ax.set_xticklabels([f"{t:.2f}" for t in ticks]); ax.minorticks_off()
lo = min(min(f(v)["lo"] for v in VARS) for _, f, _, _ in SER); hi = max(max(f(v)["hi"] for v in VARS) for _, f, _, _ in SER); assert 0.70 <= lo and hi <= 1.20, (lo, hi)
ax.set_xlim(0.69, 1.21); ax.set_xlabel("Odds ratio per standard deviation (log scale)"); ax.set_ylim(-0.7, len(VARS) - 0.3)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.legend(loc="lower center", bbox_to_anchor=(0.42, -0.24), ncol=2, frameon=False, fontsize=10)
plt.tight_layout(); save(fig, 2); plt.close(fig)
print("figs ok")
