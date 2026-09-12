# When Explanations Write Back — Public Reproducibility Repository

This public repository accompanies Aidan Edward Lawson's manuscript **When Explanations Write Back: Mechanistic Provenance for Language Models**.

## Permanent archive

The frozen manuscript and complete reproducibility package are permanently archived on Zenodo:

- **Zenodo record:** https://zenodo.org/records/22728293
- **DOI:** https://doi.org/10.5281/zenodo.22728293

The Zenodo record is the archival snapshot. This GitHub repository is the inspectable code/data companion and may receive documentation or verification improvements without changing the archived v1.0 payload.

## Confirmatory boundary

PR-002 produced an **individual preregistered success for Phi-3.5-mini-instruct**. The stronger preregistered **cross-architecture gate was not met** because Qwen and Mistral failed the frozen calibration eligibility gate and therefore did not proceed as validation-eligible architectures.

The paper's methodological claim is versioned: when a report or explanation can alter the system before validation, fidelity measured against the post-writeback mechanism need not identify fidelity to the pre-writeback mechanism. The proposed Baseline Write Barrier preserves the target before explanation uptake.

## Direct PR-002 artifacts

The two artifacts that had previously been recoverable only from the retained Hugging Face Jobs record are now directly public here:

- `results/PR002_EXACT_EXECUTED_SCRIPT.py` — exact Python script executed by the Qwen, Mistral, and Phi PR-002 jobs.
- `results/PR002_PHI_FAMILY_LEVEL.csv.gz` — gzip-compressed exact 96-family Phi validation table recovered from the retained execution log.

To recover the original CSV byte-for-byte:

```bash
gzip -dc results/PR002_PHI_FAMILY_LEVEL.csv.gz > results/PR002_PHI_FAMILY_LEVEL.csv
```

Integrity anchors:

```text
a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670  results/PR002_EXACT_EXECUTED_SCRIPT.py
6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe  results/PR002_PHI_FAMILY_LEVEL.csv
```

Original Phi execution-log SHA-256:

`d3f9ab17d3a928344772257fd11d88fded0472839453f1772fbba9d2134f84f3`

## Repository contents

- `results/PR002_EXACT_EXECUTED_SCRIPT.py` — exact executed PR-002 script
- `results/PR002_PHI_FAMILY_LEVEL.csv.gz` — complete 96-family Phi record, losslessly compressed
- `results/PR002_REPORTED_RESULTS.json` — frozen reported aggregate results
- `results/PR002_HF_JOB_PROVENANCE.json` — original job IDs, revisions, eligibility outcomes, and log hashes
- `results/PR002_ATTACK_ROBUSTNESS.json` — post hoc metric-stress and fidelity-transition analyses
- `results/PR002_RECOVERY_STATUS.md` — recovery status and historical limitations
- `protocol/PR002_PROTOCOL.md` — frozen PR-002 design and success rule
- `code/pr002_robustness_audit.py` — family-level robustness reanalysis
- `analysis/verify_reported_statistics.py` — independent aggregate-statistics checks
- `PUBLIC_RELEASE.md` — archival notes and hash-verification instructions
- `CITATION.cff` — citation metadata
- `LICENSE_STATUS.md` — explicit license-status notice

## Interpretation discipline

The post hoc robustness analyses test whether the Phi result is explained by pathologies in the normalized dominance statistic, negative intervention effects, or saturation. They do **not** replace or enlarge the preregistered endpoint.

The direct natural-report fidelity-transition analysis is exploratory because its binary fidelity criterion was defined after recovery of the family-level record.

Earlier developmental PCA experiments do not all have equivalent family-level execution artifacts. No missing observations were synthesized or back-filled.

## Archival relationship

For a stable citation or frozen release, use the Zenodo DOI above. For direct inspection of the exact PR-002 script, family-level table, and analysis utilities, use this repository.
