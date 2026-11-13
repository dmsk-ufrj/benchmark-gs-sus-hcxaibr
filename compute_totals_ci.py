#!/usr/bin/env python3
"""
compute_totals_ci.py — Reproduces Table 5 (pooled mean score by model and rubric
axis, with per-axis Total) and the approximate 95% confidence intervals plotted
in Figure 5 of the HCXAI-BR manuscript.

Pooled score = simple average of the two raters' final score for each response.
For Contestability, the "final" score is the post-refinement value reconstructed
by compute_kappa_icc.py's final_contestability() (imported here) — see that
script's docstring and ratings/contestability_reconciliation/ for why a second
pass was needed for this one axis.

Model letter codes (A-F) are deliberately anonymized in the raw rater files
(the raters scored model identity masked). The mapping to real model names
below was reconstructed independently by cross-matching each code's per-axis
score pattern against the published Table 5 — it was not read from a identity
key file — so double-check it against your own records before relying on it
for anything beyond reproducing this table.

Usage:
    python compute_totals_ci.py

Requires: openpyxl, pandas, scipy
"""
import sys
from pathlib import Path

import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute_kappa_icc import AXES, AXIS_EN, RATINGS, load_rater_sheet, final_contestability  # noqa: E402

# Reconstructed by matching each letter code's Safety / Accessible Language /
# Local Contextualization / Transparency pooled means exactly against the
# published Table 5 (see model_access/model_access.md for the match detail).
# CONFIRM against your own records before publishing/relying on this mapping.
MODEL_MAP = {
    "A": "Amazônia IA",
    "B": "Sabiá-4 BR-SP",
    "C": "Gemma-3-Gaia-PT-BR-4b-it",
    "D": "GPT",
    "E": "TucanoBR/Tucano-2b4-Instruct",
    "F": "Gemini",
}

PUBLISHED_TABLE5 = {
    # model: (Safety, Acc.lang, Local ctx, Contest., Transp., Total)
    "GPT": (1.60, 1.73, 1.17, 1.00, 1.83, 7.33),
    "Sabiá-4 BR-SP": (1.63, 1.00, 1.57, 1.03, 1.80, 7.03),
    "Gemini": (1.30, 1.70, 1.23, 0.97, 1.63, 6.83),
    "Amazônia IA": (1.07, 1.93, 0.50, 0.87, 0.87, 5.23),
    "Gemma-3-Gaia-PT-BR-4b-it": (1.30, 0.80, 0.80, 0.97, 1.13, 5.00),
    "TucanoBR/Tucano-2b4-Instruct": (0.73, 0.87, 0.10, 0.73, 0.80, 3.23),
}


def main():
    r1 = load_rater_sheet(RATINGS / "rater1_rodrigo_raw.xlsx")
    r2 = load_rater_sheet(RATINGS / "rater2_giordano_raw.xlsx")
    merged = r1.merge(r2, on="ID", suffixes=("_R1", "_R2"))
    assert len(merged) == 90

    refined = final_contestability()
    merged = merged.set_index("ID").join(refined)

    for ax in AXES:
        if ax == "Contestabilidade":
            merged[f"{ax}_pooled"] = (merged["final_av1"].astype(float) + merged["final_av2"].astype(float)) / 2
        else:
            merged[f"{ax}_pooled"] = (merged[f"{ax}_R1"].astype(float) + merged[f"{ax}_R2"].astype(float)) / 2

    merged["Modelo"] = merged["Modelo_R1"]
    merged["Modelo_name"] = merged["Modelo"].map(MODEL_MAP)

    pooled_cols = [f"{ax}_pooled" for ax in AXES]
    means = merged.groupby("Modelo_name")[pooled_cols].mean()
    sds = merged.groupby("Modelo_name")[pooled_cols].std()
    means["Total"] = means.sum(axis=1)
    means = means.sort_values("Total", ascending=False)

    print("Table 5 reproduction (pooled mean (SD across 15 prompts), 0-2 scale; Total 0-10)\n")
    header = f"{'Model':<32s}" + "".join(f"{AXIS_EN[ax]:>14s}" for ax in AXES) + f"{'Total':>8s}"
    print(header)
    for model in means.index:
        row = f"{model:<32s}"
        for ax in AXES:
            m = means.loc[model, f"{ax}_pooled"]
            s = sds.loc[model, f"{ax}_pooled"]
            row += f"{m:6.2f}({s:.2f})".rjust(14)
        row += f"{means.loc[model, 'Total']:8.2f}"
        print(row)

    print("\nComparison against published Table 5 Total (0-10):")
    for model in means.index:
        pub_total = PUBLISHED_TABLE5.get(model, (None,) * 6)[-1]
        mine = means.loc[model, "Total"]
        flag = "OK" if pub_total is not None and abs(mine - pub_total) < 0.02 else "CHECK"
        print(f"  {model:<32s} mine={mine:.2f}  published={pub_total}  [{flag}]")

    # Approximate 95% CI across the 15 prompts per model (Figure 5), on the Total scale
    print("\nApproximate 95% CI for the Total score, by model (Figure 5):")
    n_prompts = 15
    for model in means.index:
        sub = merged[merged["Modelo_name"] == model]
        totals_per_prompt = sub[pooled_cols].sum(axis=1)  # Total per response (6 models x 15 responses -> here 15 rows per model)
        mean_total = totals_per_prompt.mean()
        sd_total = totals_per_prompt.std()
        se = sd_total / (n_prompts ** 0.5)
        tcrit = stats.t.ppf(0.975, df=n_prompts - 1)
        ci_lo, ci_hi = mean_total - tcrit * se, mean_total + tcrit * se
        print(f"  {model:<32s} mean={mean_total:.2f}  95% CI=[{ci_lo:.2f}, {ci_hi:.2f}]")


if __name__ == "__main__":
    sys.exit(main())
