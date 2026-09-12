# Zenodo Archival Record

The frozen public-release manuscript and complete reproducibility package for **When Explanations Write Back: Mechanistic Provenance for Language Models** are archived on Zenodo as version 1.0.

- Zenodo record: https://zenodo.org/records/22728293
- DOI: https://doi.org/10.5281/zenodo.22728293
- Publication date: 2026-09-12
- Creator: Aidan Edward Lawson

## Archived payload integrity

The archival upload was prepared from the frozen public-release artifacts with these SHA-256 anchors:

```text
119234368123101e95040f17dc7ac36ef9439380f073818d97817c0836ae6434  When_Explanations_Write_Back_Public_Release_Manuscript.pdf
f004e4151eb3f8f1555af4c18d976786067df8dd4cbf5c8b76c7e768ea4bcf88  When_Explanations_Write_Back_Public_Reproducibility_Package.zip
```

The PR-002 artifacts embedded in the reproducibility package and mirrored in this repository have these stable anchors:

```text
a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670  PR002_EXACT_EXECUTED_SCRIPT.py
6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe  PR002_PHI_FAMILY_LEVEL.csv
```

## Relationship to this repository

Zenodo is the permanent frozen archival snapshot for citation. This GitHub repository is the inspectable code/data companion and may receive documentation or verification improvements without changing the archived v1.0 payload.

## Confirmatory boundary

PR-002 produced an individual preregistered success for Phi-3.5-mini-instruct. The stronger preregistered cross-architecture gate was not met because Qwen and Mistral failed the frozen calibration eligibility gate. Post hoc robustness analyses do not enlarge the preregistered endpoint.
