# MPW-106 — Execution amendment, reader case-hash lookup bug

**Classification:** source-only instrumentation repair after a frozen reader GPU attempt failed **before any memory-treatment observation was emitted**. Original hypotheses, case selection, model/dataset pins, frozen memory states, causal metrics, statistical tests and provider timeout are unchanged.

## Failure

The first fresh-reader GPU job [6aea5d3e](https://huggingface.co/jobs/TheUltimateHuman/6aea5d3ec78863f9c63208a9) was launched using the prospectively frozen `mpw106/scripts/mpw106_reader.py` at source commit `1f11fa6a8fc4ff889241899ea49998826846da63`. It completed historical case reconstruction, verified all selected original source hashes and all four memory snapshots, loaded the frozen model and proceeded through original baseline remeasurement without a validity-failure result. On the *first memory retrieval pilot* (NEUTRAL on the first selected case), it crashed with `KeyError: 'case_sha256'` in `retrieve(f, arm)`. **There are zero reader-treatment observations and zero H1/H2/H3 test statistics from this failed GPU job.** The original job stays ERROR / INSTRUMENT_FAILURE; it cannot count as a negative hypothesis result.

## Minimal correction

`f` is the reconstructed original source-case object from `screen.make_cases` containing `idx`, `label`, and four evidence passages. Its `case_sha256` is stored separately in the immutable selection; the original reader already verified `sha(canonical(f)) == selection.case_sha256` for every selected case before attempting memory retrieval. The frozen code nevertheless used `f["case_sha256"]` in four `contract.lookup` calls. Change **exactly those four lookup arguments** to `sha(canonical(f))`; this recomputes the same immutable per-case SHA from original source bytes. No other source changes.

This new reader is an **amended execution**, not the original pristine frozen source. It must pass an independent byte-diff/AST check before GPU, and its actual source SHA and provider job must be recorded. It uses the same source and Git refs and the original 90-minute hard cap. Do not alter any family, direction, effect test, control wrapper, missing/deleted semantics or significance gate. A failed amended validity gate remains final for this study; no score-chasing reruns.

Original eligible model: Qwen3 only. Granite's writer was already `INVALID_BASELINE_DRIFT`, and no Granite reader is permitted. The pre-reader Qwen H2/H3 minimum-16 original-false capability gate is already ineligible (15 cases), independent of this repair.
