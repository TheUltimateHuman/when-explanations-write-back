# When Explanations Write Back - Public Reproducibility Package

This repository accompanies **When Explanations Write Back: Mechanistic Provenance for Language Models**. It is assembled for public archival release and does not require private Hugging Face Jobs access to inspect the confirmatory PR-002 execution artifacts.

## Confirmatory claim

The paper's central methodological claim is versioned: when an explanation/report can alter the system before validation, fidelity measured against the post-writeback mechanism need not identify fidelity to the pre-writeback mechanism. The Baseline Write Barrier preserves the target before explanation uptake.

PR-002 produced an individual preregistered success for Phi-3.5-mini-instruct. The stronger preregistered cross-architecture gate was not met.

## Direct public-release artifacts

The two files that were previously recoverable only from the retained Hugging Face Jobs record are embedded directly here:

- `results/PR002_EXACT_EXECUTED_SCRIPT.py` - exact script executed by the Qwen, Mistral, and Phi PR-002 jobs.
- `results/PR002_PHI_FAMILY_LEVEL.csv` - complete 96-family Phi validation record reconstructed from the retained execution log.

Integrity anchors:

- exact executed script SHA-256: `a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670`
- recovered Phi family CSV SHA-256: `6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe`
- original Phi execution-log SHA-256: `d3f9ab17d3a928344772257fd11d88fded0472839453f1772fbba9d2134f84f3`

`code/recover_pr002_from_hf_jobs.py` is retained as an independent provenance check for an authorized account. It is no longer required for ordinary inspection or reanalysis of the included PR-002 family data.

## Repository map

- `submission/` - public-release manuscript artifacts
- `protocol/` - frozen PR-001/PR-002 protocols and formal notes
- `results/PR002_EXACT_EXECUTED_SCRIPT.py` - exact PR-002 execution script
- `results/PR002_PHI_FAMILY_LEVEL.csv` - complete 96-family Phi record
- `results/PR002_REPORTED_RESULTS.json` - confirmatory aggregate record
- `results/PR002_HF_JOB_PROVENANCE.json` - retained Hugging Face job provenance and hashes
- `results/PR002_ATTACK_ROBUSTNESS.json` - post hoc metric-stress and fidelity-transition analyses
- `results/PR002_RECOVERY_STATUS.md` - recovery status and limitations
- `code/recover_pr002_from_hf_jobs.py` - independent historical recovery verifier
- `code/pr002_robustness_audit.py` - recompute post hoc attacks from the included family CSV
- `analysis/verify_package_integrity.py` - verify the release manifest and payload checksums
- `analysis/verify_reported_statistics.py` - independent checks of reported aggregate statistics
- `PUBLIC_RELEASE.md` - archival/release notes and hash-verification instructions
- `SHA256SUMS.txt` - payload checksums for third-party integrity verification
- `MANIFEST.json` - machine-readable package inventory, byte counts, and SHA-256 hashes

## Interpretation discipline

Post hoc robustness checks strengthen confidence that the Phi result is not an artifact of the normalized dominance statistic, negative intervention effects, or saturation. They do **not** replace or enlarge the preregistered endpoint. The direct fidelity-transition table is exploratory because its binary criterion was defined after recovery.

Earlier developmental PCA experiments do not all have equivalent family-level execution artifacts. No missing observations were synthesized or back-filled.
