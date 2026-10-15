# MPW-101 | Prospective Fidelity-Transition Replication

Investigator: Aidan Edward Lawson (independent, Modal Path Ethics)

## Purpose

Confirm or fail to confirm the **exploratory** natural-report fidelity conversion
observation from *When Explanations Write Back* (2026, v1.1). The preregistered
report-meaning result in the prior paper is a **different** estimand.

The original exploratory 11 conversions vs 3 losses gave a *two-sided* exact
McNemar p-value of 0.057373. This was not a prospective confirmatory result.

## Protocol before validation

- Phi-3.5-mini-instruct; exact old model revision `2fe192450127e6a83f7441aef6e3ca586c338b77`.
- SST-2 revision `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`.
- Distinct 32 calibration and 256 validation families from **training split**.
- Exclude all SST-2 validation passages, the predecessor PR-002 train calibration
  passages, and all duplication within the new sample. This differs from the
  original PR-002 validation-split sampling. Sampling is frozen by seed `2026101501`
  and exact `sampled_families` source; manifest hash printed before model load.
- Ineligible if calibration baseline accuracy <.90 or mean intervention sensitivity <1.
- Validation primary inference invalid if ordinary-task accuracy <.90.
- Strict zero-threshold report agreement is **primary**: `F=1[report_sign * D > 0]`.
- Paired exact 2-sided McNemar p < .05 AND bootstrap lower 95% CI >0 AND tau>0.
- Bootstrap family resampling 100,000 replicates with seed `520261015`.
- Prespecified secondary thresholds: 0.02, 0.05, 0.10. A passing sign-only result
  with failed modest thresholds is explicitly declared FRAGILE.
- Original question and report **together** are the treatment against untouched
  baseline; no pure answer-token-only causal claim is permitted from the primary.
- Report all failures, carrier effects, baseline numerical noise, calibration failures,
  capability failures, and full paired transition table.
- Pilot speed runs only on **calibration** cases, before validation, as a resource gate.
- One GPU execution, L4 x1 timeout <=8 hours, at published $0.80/hour up to $6.40
  plus CPU preflight; user authorized up to **$10** in Hugging Face credits.
- If the HF integration or GPU job fails, **no new confirmatory claim** is made.

## Raw records

`mpw101.py` prints the entire source-text manifest and result records to HF Jobs
logs, with SHA-256 integrity markers and gzip+base64 recovery chunks, so the
records remain recoverable even if the ephemeral runtime disappears. Running
`analyze_results_independent.py` on recovered `validation_records.jsonl` checks
fidelity transitions independently of the original runner.

## Research positioning

This is a single-model prospective replication test. It is not a replication
across architectures, not a test of private introspective access, and not a
claim about neural circuit rewriting or iterative optimization.

## Execution status

**UNEXECUTED** when this text was authored. Do not change to success in advance.
