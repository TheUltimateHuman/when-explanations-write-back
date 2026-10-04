# Zenodo Archival Record

The current frozen release of **When Explanations Write Back: Mechanistic Provenance for Language Models** is archived on Zenodo as **version 1.1**.

- Zenodo record: https://zenodo.org/records/23145243
- DOI: https://doi.org/10.5281/zenodo.23145243
- Publication date: 2026-10-04
- Creator: Aidan Edward Lawson
- Version: 1.1

## Version history

### v1.1 — 2026-10-04

Version 1.1 incorporates the readability revision and the recovered PCA-006 through PCA-012 developmental execution archive: 13 retained Hugging Face Jobs executions with exact submitted scripts, retained raw logs, parsed family-level records, model/job provenance, and SHA-256 anchors.

The scientific claim boundary is unchanged. PR-002 remains the confirmatory benchmark record: Phi-3.5-mini-instruct satisfied the individual preregistered primary criterion, while the stronger preregistered cross-architecture gate was not met.

### v1.0 — 2026-09-12

The original archival release remains available at:

- Record: https://zenodo.org/records/22728293
- DOI: https://doi.org/10.5281/zenodo.22728293

The v1.0 snapshot predates the October 4 developmental-archive recovery.

## Stable PR-002 integrity anchors

```text
a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670  PR002_EXACT_EXECUTED_SCRIPT.py
6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe  PR002_PHI_FAMILY_LEVEL.csv
```

## Relationship to this repository

Zenodo v1.1 is the current frozen archival snapshot for citation. This GitHub repository is the inspectable code/data companion and may receive documentation improvements after publication without changing the archived v1.1 payload.

## Confirmatory boundary

PR-002 produced an individual preregistered success for Phi-3.5-mini-instruct. The stronger preregistered cross-architecture gate was not met because Qwen and Mistral failed the frozen calibration eligibility gate. Developmental recovery and post hoc robustness analyses do not enlarge that endpoint.
