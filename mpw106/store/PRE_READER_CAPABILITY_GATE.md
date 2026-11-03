# MPW-106: Pre-READER native report capability gate (Qwen3)

**Classification:** original pre-reader research artifact; derived exclusively from original writer outputs, without any reader treatment outcomes.

Original writer archive commit: `577549d58643b34b03abebda3bd49d6102587f99`.
Source: 64 GPU model-authored reports from https://huggingface.co/jobs/TheUltimateHuman/6ae92f640e0338d1bb7eba8c .
Independent source report verifier: https://huggingface.co/jobs/TheUltimateHuman/6aea5ca2c78863f9c6320829 (PASS).
Separate pre-reader false cohort audit: https://huggingface.co/jobs/TheUltimateHuman/6aea5df10e0338d1bb7f73ac .

- Original baseline-faithful reports: **46/64**.
- Original baseline-unfaithful **parseable** reports: **15/64** (indices `[51,92,166,195,230,260,316,348,349,400,434,613,622,629,776]`).
- Unparseable original reports: **3/64** (indices `[268,339,402]`).
- Native prose parseability: **61/64 (95.3125%)**; all 64 raw native texts nonempty.

The prospectively frozen MPW-106 protocol requires a minimum **16 original A0-unfaithful parseable** reports for both H2 and H3. This requirement was fixed before the GPU reader. The correct verdict is `INDETERMINATE_CAPABILITY` for H2/H3 *provided the reader completes validly*; if the reader fails scientific source/validity gates, report invalidity instead. These 15 cases remain in the full 64-case reader archive; no replacement or supplementation is permitted. H1 is still eligible, subject to the full 64-family reader and statistical gates. This audit uses no reader treatment information.

Granite failed `INVALID_BASELINE_DRIFT` before model-authored report generation; no Granite H1/H2/H3 estimate.
