# PR-002 Recovery Status

The retained Hugging Face Jobs record contains the exact executed PR-002 script and the complete 96-family Phi validation output. These artifacts were recovered on 2026-09-11 during the hostile submission audit and are now embedded in this public repository.

Direct files:

- `results/PR002_EXACT_EXECUTED_SCRIPT.py`
- `results/PR002_PHI_FAMILY_LEVEL.csv.gz` (gzip-compressed exact CSV; decompress to recover the original byte-for-byte family table)

Key hashes:

- exact executed PR-002 script: `a931bcf62608aa4178f84f02d7b1519c5193d11579cf4c2b065e71f03d2bf670`
- decompressed Phi family CSV: `6aa41468ef83c9d6c93205a3479866fac684fac13a3c04cdc57bc5874291f5fe`
- Phi original execution log: `d3f9ab17d3a928344772257fd11d88fded0472839453f1772fbba9d2134f84f3`

No values were synthesized. The family record enabled post hoc metric-stress tests and an exploratory direct instantiation of the paper's fidelity-transition identity. Those analyses remain separate from the preregistered confirmatory endpoint.
