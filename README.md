# HCXAI-BR — raw data and reproduction scripts

Supporting data and analysis scripts for **HCXAI-BR**, a reproducible
benchmark of human-centered explainability and contestability for health
information guidance in Brazil, evaluating six large language models
(four commercial, two open-weight) across five rubric axes: Safety,
Accessible Language, Local Contextualization, Contestability, and
Transparency.

> Manuscript under Major Revisions at *MDPI Algorithms* (special issue
> "Explainable AI: Advances in Interpretability Algorithms and
> Applications"). Citation details will be added here once the camera-ready
> version is accepted.

## What's in this repository

| Folder | Contents |
|---|---|
| `prompts/` | The 15-prompt instrument (10 standard-register + 5 colloquial/regional-register, across 5 health themes). |
| `literature_review/` | The 127-paper corpus and thematic coding (7 clusters) behind the 20-paper Health & Well-Being cluster this study builds on (Section 2). |
| `responses/` | The collection log for all 90 model responses (6 models × 15 prompts), including the full raw response text, access metadata, and the "new chat" flag per response. |
| `ratings/` | Both human raters' scores on all five axes for all 90 responses, plus the Contestability reconciliation files (see below), plus the 25-item/14-rater lay-reader pilot used for external validation (Section 4.5/5.4). |
| `model_access/` | The verbatim access protocol from the manuscript and the model-letter-code identity key. |
| `scripts/` | Python scripts that reproduce Tables 4 and 5 and the Section 6.2 axis-correlation analysis directly from the files above. |

## Quick start

```bash
cd scripts
pip install -r requirements.txt
python compute_kappa_icc.py        # reproduces Table 4 (inter-rater reliability)
python compute_totals_ci.py        # reproduces Table 5 and the Figure 5 confidence intervals
python axis_correlations.py        # reproduces the Section 6.2 axis-correlation matrix
```

Each script's own docstring explains exactly which manuscript table/figure it
reproduces and any flags that change its behavior.

## Data dictionary (short version)

- **Model letter codes (`A`–`F`)**: both raters scored responses with model
  identity masked. See `model_access/model_access.md` for the real-name
  mapping and how it was reconstructed.
- **Prompt IDs (`P01`–`P15`)**: see `prompts/prompts_15items.xlsx` for the
  prompt text, health theme, and register (standard vs. colloquial).
  `response ID` = `{model letter}_{prompt ID}` (e.g., `A_P03`).
- **Rubric axes**: scored 0, 1, or 2 by each rater, per the rubric descriptors
  in the manuscript's Table 2/Table 3 (not reproduced as a separate file
  here, since they are already in the manuscript itself).
- **Rater files**: `ratings/rater1_rodrigo_raw.xlsx` and
  `ratings/rater2_giordano_raw.xlsx`, one row per response, one column per
  axis (score) plus a free-text justification column, for all 90 responses.

## Known limitations — read before reusing this data

This section exists so that anyone reusing this data does not have to
rediscover these limitations the hard way. All of them are also disclosed in
the manuscript itself (Section 7.2, Limitations).

### 1. Contestability needed a second scoring pass — and that is why this axis has its own subfolder

The two raters' *first-pass* scores for Contestability (in
`ratings/rater1_rodrigo_raw.xlsx` / `rater2_giordano_raw.xlsx`) agreed only
weakly (κ=0.111, quadratic-weighted; 44.4% exact agreement on a 0–2 scale) —
far below the other four axes (κ 0.38–0.83). Inspecting the disagreements
showed they were not random: they concentrated on specific prompts (notably
the "warning signs" theme) and were systematically one-directional (Rater 1
scored higher than Rater 2 in 47 of the 50 disagreeing responses).

The two raters then revised the Contestability rubric anchor to separate
"recognizing the response's own reading may be incomplete" from "recommending
the user seek care" (the latter already being credited under Safety), and
re-scored:

- the **20 responses with the largest first-pass disagreement** against the
  revised anchor (`ratings/contestability_reconciliation/reconciliation_20_largest_disagreements.xlsx`,
  which also documents the full rationale for the anchor revision in its own
  "Leia-me" sheet), then
- the **remaining 70 responses** against the same revised anchor
  (`ratings/contestability_reconciliation/reconciliation_remaining_70.xlsx`).

In both reconciliation files, a response that both raters had already agreed
on in the first pass was left blank in the "new score" columns (no need to
re-score something with no disagreement) — the published Table 4 uses the
revised score where one was recorded, and the original (already-agreed)
score otherwise. `scripts/compute_kappa_icc.py` implements exactly this
fallback and reproduces the published post-refinement numbers exactly
(κ=0.485, ICC(A,1)=0.487, 72.2% exact agreement). Pass `--pre-refinement` to
see the original, weaker numbers instead.

**This refinement is diagnostic, not independent validation**: the anchor was
revised by inspecting the very disagreements it was then applied to fix, on
the same 90 responses. The manuscript (Section 5.1) is explicit that
independent replication on an unexposed response set would be needed before
treating κ=0.485 as evidence the rubric itself is reliable, rather than
evidence that this specific anchor wording, applied by these two raters to
these 90 responses, now agrees better than it did before.

### 2. No per-response or per-model collection timestamp

`responses/responses_collection_log.xlsx`'s "Data/hora da coleta" column is
empty for all 90 rows. Only the aggregate collection window — 5 to 18
September 2026 — was ever recorded; it is not possible to recover when, within
that window, any individual response was collected, or whether collection
dates differed systematically by model. See `model_access/model_access.md`
for the full access protocol and its other disclosed limitations (decoding
parameters never fixed or recorded; backend checkpoints for the four
consumer-interface models not independently verifiable).

### 3. The "new chat" flag was corrected after a data-entry error, not a protocol deviation

`responses/responses_collection_log.xlsx`'s "Conversa nova?" ("new
conversation?") column originally showed "Não" for all 15 Amazônia IA
responses and all 15 Sabiá-4 BR-SP responses, apparently contradicting the
manuscript's statement that every prompt was submitted as a new chat with no
prior conversation history. This was confirmed with the study team to be a
data-entry error during logging, not an actual protocol deviation — every
prompt genuinely was submitted as a new chat for every model — and the column
has been corrected to "Sim" for all 90 rows in the file in this repository.

### 4. Single-rater caveats

A few manuscript analyses (the R1-7/R1-8 illustrative response excerpts, and
the Section 6.2 axis-correlation matrix reproduced by
`scripts/axis_correlations.py`) use Rater 1's (Rodrigo's) scores alone, not
the two-rater pooled average that Tables 4/5/6 use elsewhere. This is called
out in the manuscript at each such point, and `axis_correlations.py`'s
docstring repeats it.

### 5. Rater 2's justification column is blank

`ratings/rater2_giordano_raw.xlsx` has valid scores (0/1/2) for all 90
responses × 5 axes, but the free-text justification column is empty
throughout — Rater 2 recorded scores only, not the reasoning behind them.
This does not affect any of the statistics above (which use only the numeric
scores), but means the qualitative illustrative excerpts in the manuscript
draw on Rater 1's justifications only.

## License

- **Data** (everything under `prompts/`, `literature_review/`,
  `responses/`, `ratings/`, `model_access/`): released under
  [CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/) — reuse and
  redistribution are permitted with attribution.
- **Code** (everything under `scripts/`): released under the
  [MIT License](https://opensource.org/license/mit/).

*(These were chosen as reasonable defaults for an open academic benchmark and
have not yet been confirmed with all co-authors — update
`LICENSE-DATA`/`LICENSE-CODE` if a different choice is preferred before
pushing.)*
