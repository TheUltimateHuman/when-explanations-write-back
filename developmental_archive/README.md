# Developmental PCA Archive — repository v1.1 supplement

Recovered on **2026-10-04** from the retained Hugging Face Jobs execution record for *When Explanations Write Back: Mechanistic Provenance for Language Models*.

This directory preserves **13 retained executions spanning PCA-006 through PCA-012**. Each execution directory contains:

- `exact_executed_script.py` — the script recovered from the exact submitted HF Job command;
- `raw_job_log.txt` — the retained execution log as returned by Hugging Face Jobs;
- `family_records.json` — parsed `PCAxxx_RECORD` / `PCA007M2_RECORD` rows, summary rows, model revision, job ID, hardware flavor, and execution timestamps.

`MANIFEST.json` records SHA-256 and Git blob SHA anchors for every archived artifact.

## Scientific status

These runs are **developmental / non-confirmatory**. Their recovery does not alter the paper's preregistered PR-002 boundary. PR-002 remains the confirmatory benchmark record and its stronger cross-architecture gate remains unmet.

No missing observations were synthesized or back-filled. Parsed family records are derived only from the retained execution logs. The raw logs are preserved alongside them so parsing can be independently checked.

## Archival relation

Zenodo v1.0 (DOI 10.5281/zenodo.22728293) is a frozen earlier snapshot and does **not** contain this 2026-10-04 developmental recovery supplement. This repository supplement should be deposited as a new archival version if a permanent Zenodo v1.1 snapshot is desired.
