# MPW-106 — Native report-side asymmetry (pre-reader audit)

**Classification:** source-only descriptive research audit, conducted without access to or selection based on reader treatment outcomes. This finding cannot alter any prespecified endpoint, source cohort, or hypothesis.

Original raw native Qwen writer data: [writer archive 577549d](https://github.com/TheUltimateHuman/when-explanations-write-back/commit/577549d58643b34b03abebda3bd49d6102587f99), exact 64 source cases. Independent CPU original-text cross-tab: [job 6aea5f8b](https://huggingface.co/jobs/TheUltimateHuman/6aea5f8b0e0338d1bb7f74a4).

| Protected original true side / Native report parsed side | LEFT | RIGHT | Unparseable | Total |
|---|---:|---:|---:|---:|
| LEFT | 34 | 3 | 1 | 38 |
| RIGHT | 12 | 12 | 2 | 26 |
| Total | 46 | 15 | 3 | 64 |

Thus 46 original A0-faithful and 15 A0-unfaithful parseable reports, plus 3 unparseable. The original reported side has a strong LEFT tendency (46/61 parseable), an interpretive limitation for any report-specific steering; signed H1 uses both sides and the original frozen neutral comparison, but is not a clean test of causal mechanism independent of prompt salience or message length. Preserve directional subsets as descriptive diagnostics only. The frozen H2/H3 minimum-16 capability gate is not met. No reader outcome has been observed in this audit.
