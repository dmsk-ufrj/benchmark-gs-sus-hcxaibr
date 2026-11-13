#!/usr/bin/env python3
"""
axis_correlations.py — Reproduces the Pearson correlation matrix between the
five rubric axes reported in Section 6.2 (RQ2) of the HCXAI-BR manuscript,
in response to Reviewer 2's point R2-13 (axis overlap / independence).

IMPORTANT CAVEAT (stated explicitly in the manuscript, Section 6.2): this
correlation matrix uses Rater 1's (Rodrigo's) scores only, not the pooled
average of both raters — the same single-rater caveat that applies to the
R1-7/R1-8/R2-13 illustrative analyses elsewhere in the manuscript. It is NOT
run on the post-refinement Contestability scores, since the correlation
analysis in the manuscript was computed before the Contestability
reconciliation pass existed. Re-running it on the refined scores or on the
pooled (two-rater) scores will give different (not wrong, just different and
not what is quoted in the paper) numbers — if you want that comparison, pass
--refined and/or --pooled.

Usage:
    python axis_correlations.py                 # exactly what Section 6.2 reports
    python axis_correlations.py --refined        # Rater 1 only, but with refined Contestability
    python axis_correlations.py --pooled          # pooled (both raters), pre-refinement Contestability
    python axis_correlations.py --refined --pooled  # pooled, with refined Contestability

Requires: openpyxl, pandas
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compute_kappa_icc import AXES, AXIS_EN, RATINGS, load_rater_sheet, final_contestability  # noqa: E402

SHORT = {
    "Segurança": "Safety",
    "Linguagem acessível": "AccLang",
    "Contexto local": "LocalCtx",
    "Contestabilidade": "Contest",
    "Transparência": "Transp",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refined", action="store_true",
                         help="Use post-refinement Contestability scores instead of pre-refinement")
    parser.add_argument("--pooled", action="store_true",
                         help="Use the pooled (average of both raters) score per axis instead of Rater 1 only")
    args = parser.parse_args()

    r1 = load_rater_sheet(RATINGS / "rater1_rodrigo_raw.xlsx")
    r2 = load_rater_sheet(RATINGS / "rater2_giordano_raw.xlsx")
    merged = r1.merge(r2, on="ID", suffixes=("_R1", "_R2"))
    assert len(merged) == 90

    df = pd.DataFrame(index=merged["ID"])
    for ax in AXES:
        if ax == "Contestabilidade" and args.refined:
            refined = final_contestability()
            joined = merged.set_index("ID").join(refined)
            if args.pooled:
                df[SHORT[ax]] = (joined["final_av1"].astype(float) + joined["final_av2"].astype(float)) / 2
            else:
                df[SHORT[ax]] = joined["final_av1"].astype(float)
        else:
            a = merged.set_index("ID")[f"{ax}_R1"].astype(float)
            if args.pooled:
                b = merged.set_index("ID")[f"{ax}_R2"].astype(float)
                df[SHORT[ax]] = (a + b) / 2
            else:
                df[SHORT[ax]] = a

    corr = df.corr(method="pearson")

    mode_bits = []
    mode_bits.append("pooled (both raters)" if args.pooled else "Rater 1 (Rodrigo) only — matches Section 6.2")
    mode_bits.append("post-refinement Contestability" if args.refined else "pre-refinement Contestability — matches Section 6.2")
    print(f"Axis correlation matrix — {', '.join(mode_bits)}\n")
    print(corr.round(2).to_string())

    pairs = []
    for i, a in enumerate(corr.columns):
        for b in corr.columns[i + 1:]:
            pairs.append((a, b, corr.loc[a, b]))
    pairs.sort(key=lambda t: -abs(t[2]))
    print("\nPairs ranked by |r|:")
    for a, b, r in pairs:
        print(f"  {a:<10s} x {b:<10s}  r = {r:+.2f}")

    if not args.refined and not args.pooled:
        print("\nExpected (Section 6.2): highest pair is LocalCtx x Contest (r≈0.75); "
              "the Safety/Transparency/Contestability trio the reviewer asked about "
              "correlates only moderately (r≈0.20-0.47); no pair exceeds r=0.8.")


if __name__ == "__main__":
    sys.exit(main())
