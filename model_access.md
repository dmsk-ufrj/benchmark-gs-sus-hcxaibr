# Model access protocol and identity key

This file documents (a) exactly how each of the six models was accessed during
data collection, verbatim from the manuscript (Section 4.1), and (b) the key
mapping the anonymized model letter codes (`A`-`F`) used throughout
`ratings/rater1_rodrigo_raw.xlsx` and `ratings/rater2_giordano_raw.xlsx` to the
real model names.

## Why the raw rating files use letter codes

Both raters scored the 90 responses with model identity masked (shown only as
"Modelo A", "Modelo B", etc., in randomized row order) to avoid the raters'
own expectations about a given provider biasing their scores. The key linking
each code to a real model name was held separately by the study team and was
not itself exported as a data file during collection.

**The mapping below was reconstructed independently**, not read from that
original key, by cross-matching each letter code's pooled per-axis mean score
(Safety, Accessible Language, Local Contextualization, Transparency — the four
axes that are directly reproducible from the raw rater files without any
further processing) against the exact values published in the manuscript's
Table 5. All six letters matched on all four axes to two decimal places (see
`scripts/compute_totals_ci.py`, which reproduces every published Total score
exactly using this mapping), so it should be reliable — but cross-check it
against your own records before treating it as authoritative for anything
beyond reproducing the published tables.

| Code | Model | Provider |
|---|---|---|
| A | Amazônia IA | WideLabs |
| B | Sabiá-4 BR-SP | Maritaca AI |
| C | Gemma-3-Gaia-PT-BR-4b-it | CEIA-UFG, ABRIA, Nama, Amadeus AI, Google DeepMind (adapted from `google/gemma-3-4b-pt`) |
| D | GPT-5.6 Luna | OpenAI |
| E | TucanoBR/Tucano-2b4-Instruct | trained from scratch on the GigaVerbo corpus |
| F | Gemini 3.5 Flash-Lite | Google |

## Access protocol (verbatim from the manuscript, Section 4.1)

> The four proprietary and commercial models, GPT-5.6 Luna (OpenAI), Gemini
> 3.5 Flash-Lite (Google), Sabiá-4 BR-SP (Maritaca AI), and Amazônia IA
> (WideLabs) ... were queried through each provider's public chat interface
> rather than a programmatic API, using a newly created account with no prior
> usage history or personalization, accessed from a Google Chrome
> private-browsing (incognito) window, with every prompt submitted as a new
> chat carrying no prior conversation history, to avoid cross-prompt context
> contamination within a model; decoding parameters such as temperature,
> top-p, and maximum output length were left at each interface's default and
> were not explicitly configured or recorded.
>
> The two open-weight models, Gemma-3-Gaia-PT-BR-4b-it ... and
> TucanoBR/Tucano-2b4-Instruct ..., were queried through Hugging Face's
> hosted Inference API, using each model's publicly deployed checkpoint at
> the time of collection. Both open-weight models were served on Hugging
> Face's own hosted infrastructure (Inference API) running on T4 GPU
> instances rather than on a self-managed server, so their exact runtime
> configuration beyond what the API reported could not be independently
> verified.
>
> All responses were collected between 5 and 18 September 2026. ... For the
> two Hugging Face-hosted models, no decoding parameters (temperature, top-p,
> maximum tokens) were explicitly passed in the API call either, so
> generation used the Inference API's own defaults ... Likewise, no custom
> system instructions were supplied for any of the six models beyond each
> provider's or endpoint's own default behavior; for the four consumer
> interfaces in particular, any system-level instructions or safety layer the
> provider applies internally are not disclosed and could not be inspected or
> held constant across models.

## Known limitations of this protocol (also stated in the manuscript, Section 7.2)

- **No per-response or per-model timestamps.** Only the aggregate collection
  window (5–18 September 2026) was ever recorded in the tracking spreadsheet
  used during collection (`responses/responses_collection_log.xlsx`); the
  "Data/hora da coleta" column in that file is empty for all 90 rows. Finer
  temporal analysis (e.g., did later-collected responses differ systematically
  from earlier ones) is not possible from the released data.
- **Backend checkpoints for the four consumer-interface models are not
  independently verifiable** beyond what each provider's interface reported
  at the time of collection — provider-side routing, A/B tests, and silent
  model updates are a known source of drift for public chat products.
- **Decoding parameters were not fixed or recorded** for any of the six
  models (all six used each interface's or endpoint's own defaults).
- **Exact per-model access dates within the 5–18 September window** are not
  captured in any file in this repository — only the aggregate window is
  available.
