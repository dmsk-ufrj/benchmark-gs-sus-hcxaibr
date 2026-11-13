#!/usr/bin/env python3
"""
compute_kappa_icc.py — Reproduces Table 4 (inter-rater reliability by rubric axis)
of the HCXAI-BR manuscript from the raw rater spreadsheets.

For four of the five axes (Safety, Accessible Language, Local Contextualization,
Transparency), this script reads the two raters' original scores directly from
ratings/rater1_rodrigo_raw.xlsx and ratings/rater2_giordano_raw.xlsx.

For Contestability specifically, the two raw rater files only contain the
PRE-refinement scores (kappa_quad=0.111, ICC(A,1)=0.112, p=.050 — also
reproducible from this axis alone, see the --pre-refinement flag). The published
Table 4 values for Contestability (kappa_quad=0.485, ICC(A,1)=0.487) come from a
second reconciliation pass: see ratings/contestability_reconciliation/, where the
two raters re-scored this one axis against a revised rubric anchor (documented in
that folder's own notes). This script merges the reconciliation files with the
original scores (falling back to the original score wherever the reconciliation
sheet left a cell blank — which happens for every response where the two raters
already agreed on the first pass and therefore needed no re-scoring) to
reconstruct the final Contestability column used in the published analysis.

Usage:
    python compute_kappa_icc.py                  # all five axes, published (final) values
    python compute_kappa_icc.py --pre-refinement  # Contestability using only the
                                                   # original (pre-refinement) scores,
                                                   # for comparison / transparency

Requires: openpyxl, pandas, scikit-learn, pingouin
"""
import argparse
import sys
from pathlib import Path

import openpyxl
import pandas as pd
from sklearn.metrics import cohen_kappa_score
import pingouin as pg

HERE = Path(__file__).resolve().parent
RATINGS = HERE.parent / "ratings"

AXES = ["Segurança", "Linguagem acessível", "Contexto local", "Contestabilidade", "Transparência"]
AXIS_EN = {
    "Segurança": "Safety",
    "Linguagem acessível": "Accessible Language",
    "Contexto local": "Local Contextualization",
    "Contestabilidade": "Contestability",
    "Transparência": "Transparency",
}
LANDIS_KOCH = [
    (0.00, "Slight"), (0.21, "Fair"), (0.41, "Moderate"),
    (0.61, "Substantial"), (0.81, "Almost perfect"),
]


def interpret(kappa):
    band = "Slight"
    for threshold, label in LANDIS_KOCH:
        if kappa >= threshold:
            band = label
    return band


def load_rater_sheet(path, sheet="Avaliação"):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet]
    header = [ws.cell(row=4, column=c).value for c in range(1, 17)]
    col = {name: idx + 1 for idx, name in enumerate(header) if name}
    rows = []
    r = 5
    while ws.cell(row=r, column=1).value is not None:
        rec = {"ID": ws.cell(row=r, column=col["ID"]).value,
               "Modelo": ws.cell(row=r, column=col["Modelo"]).value}
        for ax in AXES:
            rec[ax] = ws.cell(row=r, column=col[ax]).value
        rows.append(rec)
        r += 1
    return pd.DataFrame(rows)


def load_reconciliation(path, sheet):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb[sheet]
    rows = []
    r = 5
    while ws.cell(row=r, column=1).value is not None:
        rows.append({
            "ID": ws.cell(row=r, column=1).value,
            "nota_av1_old": ws.cell(row=r, column=7).value,
            "nota_av2_old": ws.cell(row=r, column=9).value,
            "nota_av1_new": ws.cell(row=r, column=12).value,
            "nota_av2_new": ws.cell(row=r, column=14).value,
        })
        r += 1
    return pd.DataFrame(rows)


def final_contestability():
    """Reconstruct the post-refinement Contestability column (90 responses)."""
    recon_dir = RATINGS / "contestability_reconciliation"
    df20 = load_reconciliation(recon_dir / "reconciliation_20_largest_disagreements.xlsx",
                                "Reavaliação (20 casos)")
    df70 = load_reconciliation(recon_dir / "reconciliation_remaining_70.xlsx",
                                "Reavaliação (70 casos)")
    full = pd.concat([df20, df70], ignore_index=True)
    assert full["ID"].nunique() == 90, f"expected 90 unique responses, got {full['ID'].nunique()}"
    full["final_av1"] = full["nota_av1_new"].where(full["nota_av1_new"].notna(), full["nota_av1_old"])
    full["final_av2"] = full["nota_av2_new"].where(full["nota_av2_new"].notna(), full["nota_av2_old"])
    return full.set_index("ID")[["final_av1", "final_av2"]]


def compute_axis_stats(a, b):
    kq = cohen_kappa_score(a, b, weights="quadratic")
    kl = cohen_kappa_score(a, b, weights="linear")
    exact = (a == b).mean()
    long = pd.DataFrame({
        "item": list(range(len(a))) * 2,
        "rater": ["R1"] * len(a) + ["R2"] * len(b),
        "score": list(a) + list(b),
    })
    icc = pg.intraclass_corr(data=long, targets="item", raters="rater", ratings="score")
    icc_row = icc[icc["Type"] == "ICC(A,1)"].iloc[0]
    return {
        "kappa_quadratic": kq,
        "kappa_linear": kl,
        "exact_agreement_pct": exact * 100,
        "icc_a1": icc_row["ICC"],
        "icc_ci95": tuple(icc_row["CI95"]),
        "icc_pval": icc_row["pval"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pre-refinement", action="store_true",
                         help="Use only the original (pre-refinement) Contestability scores")
    args = parser.parse_args()

    r1 = load_rater_sheet(RATINGS / "rater1_rodrigo_raw.xlsx")
    r2 = load_rater_sheet(RATINGS / "rater2_giordano_raw.xlsx")
    merged = r1.merge(r2, on="ID", suffixes=("_R1", "_R2"))
    assert len(merged) == 90, f"expected 90 merged responses, got {len(merged)}"

    results = {}
    for ax in AXES:
        if ax == "Contestabilidade" and not args.pre_refinement:
            refined = final_contestability()
            joined = merged.set_index("ID").join(refined)
            a = joined["final_av1"].astype(float)
            b = joined["final_av2"].astype(float)
        else:
            a = merged[f"{ax}_R1"].astype(float)
            b = merged[f"{ax}_R2"].astype(float)
        results[ax] = compute_axis_stats(a, b)

    label = "PRE-refinement" if args.pre_refinement else "FINAL (post-refinement for Contestability)"
    print(f"Table 4 reproduction — {label}\n")
    print(f"{'Axis':<28s} {'k_quad':>7s} {'k_lin':>7s} {'exact%':>7s} {'ICC(A,1)':>9s} {'95% CI':>18s} {'interp.':>13s}")
    for ax in AXES:
        s = results[ax]
        ci = f"[{s['icc_ci95'][0]:.2f}, {s['icc_ci95'][1]:.2f}]"
        print(f"{AXIS_EN[ax]:<28s} {s['kappa_quadratic']:7.3f} {s['kappa_linear']:7.3f} "
              f"{s['exact_agreement_pct']:6.1f}% {s['icc_a1']:9.3f} {ci:>18s} "
              f"{interpret(s['kappa_quadratic']):>13s}")

    print("\nPublished Table 4 (for comparison):")
    print("Safety                       0.514   0.520   71.1%     0.517      [0.35, 0.65]      Moderate")
    print("Accessible Language          0.573   0.527   71.1%     0.576      [0.40, 0.71]      Moderate")
    print("Local Contextualization      0.828   0.749   77.8%     0.829      [0.75, 0.88] Almost perfect")
    print("Contestability (final)       0.485   0.401   72.2%     0.487      [0.26, 0.65]      Moderate")
    print("Contestability (pre-refine.) 0.111     —       —       0.112      [-0.06,0.29]        Slight")
    print("Transparency                 0.383   0.314   57.8%     0.386      [0.19, 0.55]          Fair")


if __name__ == "__main__":
    sys.exit(main())
