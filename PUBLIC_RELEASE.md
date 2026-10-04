# Public Release Notes

The frozen v1.0 manuscript and complete reproducibility package are archived on Zenodo:

- Record: https://zenodo.org/records/22728293
- DOI: https://doi.org/10.5281/zenodo.22728293

The Zenodo record is the permanent archival snapshot. This GitHub repository remains the inspectable code/data companion.

This archive is self-contained for the PR-002 confirmatory record described in the manuscript. Reviewers do not need access to the author's Hugging Face account to inspect the exact executed script or the 96-family Phi output table.

## Integrity checks

The two primary recovered PR-002 artifacts can be checked directly after decompressing the family table:

```bash
sha256sum results/PR002_EXACT_EXECUTED_SCRIPT.py

gzip -dc results/PR002_PHI_FAMILY_LEVEL.csv.gz > results/PR002_PHI_FAMILY_LEVEL.csv
sha256sum results/PR002_PHI_FAMILY_LEVEL.csv
```

Expected values:

```text
a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670  results/PR002_EXACT_EXECUTED_SCRIPT.py
6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe  results/PR002_PHI_FAMILY_LEVEL.csv
```

The original Phi execution-log hash remains `d3f9ab17d3a928344772257fd11d88fded0472839453f1772fbba9d2134f84f3`. Original Qwen, Mistral, and Phi job IDs and model/dataset provenance are recorded in `results/PR002_HF_JOB_PROVENANCE.json`.

## Claim boundary

Phi-3.5-mini-instruct met its individual preregistered PR-002 primary endpoint. The stronger preregistered cross-architecture gate was not met because Qwen and Mistral failed the preregistered calibration gate. Public release of the recovered family table does not promote any post hoc analysis into the confirmatory endpoint.

The retained developmental PCA-006 through PCA-012 execution artifacts were subsequently recovered on 2026-10-04 and are preserved under `developmental_archive/` in the GitHub repository. This repository supplement does not alter the preregistered PR-002 endpoint and is not part of the frozen Zenodo v1.0 payload.

## Repository v1.1 developmental recovery

The later repository supplement preserves 13 retained Hugging Face Jobs executions spanning PCA-006 through PCA-012. Each archived execution includes the exact submitted script, retained raw log, parsed family-level records, model revision/job provenance, and SHA-256 anchors. These materials are historical developmental evidence only and do not retroactively become confirmatory results.

See `developmental_archive/README.md` and `developmental_archive/MANIFEST.json`.

## Citation

Lawson, Aidan Edward. *When Explanations Write Back: Mechanistic Provenance for Language Models*. Version 1.0, 2026. DOI: 10.5281/zenodo.22728293.
