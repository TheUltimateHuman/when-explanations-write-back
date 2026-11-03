# MPW-106 Stage W original GPU outcome

Source frozen before inference: `1f11fa6a8fc4ff889241899ea49998826846da63`; protected screen: `63b8e7fd4385408e724ad81e7e8fcd51b6fc043a`.

- Qwen3 original GPU job [6ae92f640e0338d1bb7eba8c](https://huggingface.co/jobs/TheUltimateHuman/6ae92f640e0338d1bb7eba8c): **WRITER_COMPLETED**, 64/64 original reports, 61/64 parseable, four 16-family raw shards; combined original raw SHA-256 `a0ae9a72fb188bf3b96f3e7e4e27895452b24c0c5c158efd467458b7a6dd84de`. Raw records require independent CPU verification before memory can be committed.
- Granite original GPU job [6ae92f700e0338d1bb7eba97](https://huggingface.co/jobs/TheUltimateHuman/6ae92f700e0338d1bb7eba97): **INVALID_BASELINE_DRIFT**, 125 failed order-specific baseline-version checks against the locked 1e-4 gate. Calibration had passed, but the writer stopped before any model-generated report, archive, or memory. Granite H1–H3 are invalid/not estimated; do not rerun or drop failed cases.

The archive contains ONLY original writer data from the eligible Qwen3 job. Writer data have not yet been written to the external memory carrier; the GPU writer itself never writes to Git.
