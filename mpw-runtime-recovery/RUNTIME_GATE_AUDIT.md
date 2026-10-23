# MPW-101 through MPW-103 — Hostile Runtime-Gate Audit

**Audit date:** 2026-10-23. **Scope:** all 100 Hugging Face jobs returned by authenticated job history, including all nine known substantive GPU experiments from MPW-101 through MPW-103, the MPW-102A token preflight failure, and source-code runtime gates. Original archived source/report text and final tags were compared. This audit does not claim coverage of jobs outside this HF account, unretrieved private workstation runs, or unpublished programs under other research names.

**Conclusion: TWO confirmed unjustified timing-gate refusals**, both at fixed 3900-second assistant-generated internal caps:
1. MPW-102B Granite original job 6adb59f41e112550ce7d4f20 — eligible, forecast 4009.34 sec padded, RUNTIME_GATE_FAIL/NO_VALIDATION.
2. MPW-103 Qwen original job 6adbb3371e112550ce7d7e4d — eligible, forecast 4114.36 sec padded, RUNTIME_GATE_FAIL/NO_VALIDATION.

Both were falsely prevented by comparing a conservative 35%-padded forecast to MAX_SECONDS-180 = 3720 sec. The provider's original 75-minute limit was 4500 sec. Even both padded estimates were BELOW 4500 sec. Hence provider capacity was *not* the stopping cause. Their unpadded estimates, including measured startup, were 3019.01 sec (102B Granite) and 3097.39 sec (103 Qwen), approximately 50.3 and 51.6 minutes.

## Complete recoverable experimental ledger

| Pass | Model / job | Original status by actual runner logs | Gate distinction |
| --- | --- | --- | --- |
| MPW-101 | Phi, 6ad0205b5ccb47ba0f7a2a2f | 256/256 complete; PRIMARY NOT CONFIRMED | Authentic negative primary. Timing pilot 389.69 sec forecast vs 28800 hard allowed; not truncated. |
| MPW-101E | Phi, 6ad02a4d5ccb47ba0f7a2dfa | 256/256 exploratory diagnostic complete | Runtime forecast 347.89 sec vs 840-sec limit; no timing stop. |
| MPW-102A | Phi, 6ad0329e5ccb47ba0f7a3139 | 256/256 complete; PRIMARY CONFIRMED | 2092.01-sec padded forecast, accepted; no timing stop. |
| MPW-102B | Qwen3, 6adb597a1e112550ce7d4ecb | 192/192 complete; original H1+H2 CONFIRMED | 1672.46-sec forecast; no timing stop. |
| MPW-102B | Granite L4, 6adb59f41e112550ce7d4f20 | Calibration PASSED, 0 validation; RUNTIME_GATE_FAIL | **Assistant-added cap blocked attainable trial. Corrected separately post-result.** |
| MPW-102C | Qwen3, 6adb939b046eb82b1ecd5a01 | 160/160 complete; H1/H2/H3 CONFIRMED | 1731.98-sec forecast; no timing stop. |
| MPW-102C | Granite L40S, 6adb93921e112550ce7d6a2e | 160/160 complete; H1/H3 CONFIRMED, H2 NOT CONFIRMED | 1182.73-sec forecast; no timing stop. Genuine scientific negative H2. |
| MPW-103 | Qwen3 L4, 6adbb3371e112550ce7d7e4d | Calibration PASSED, 0 validation; RUNTIME_GATE_FAIL | **Assistant-added cap blocked attainable trial. Corrected separately post-result.** |
| MPW-103 | Granite L40S, 6adbb3381e112550ce7d7e50 | 128/128 complete; H1/H3 CONFIRMED, H2/H4 NOT CONFIRMED | 2495.17-sec forecast; no timing stop. Genuine negative H2/H4. |

### Additional prevalidation failures not caused by runtime

- MPW-102A original CPU preflight job 6ad030965ccb47ba0f7a3089: response codes '1'/'2' expanded to two tokens under pinned Phi tokenizer; required atomic next-token code criterion failed. The failure was documented as AMENDMENT-001 before GPU validation and code pair replaced with K/M. This was a legitimate instrumentation check and was not a runtime throttling error.
- Any Qwen/Granite calibration failures from older exploratory PCA/PR-002 studies require separate archival retrieval; the current claim of exactly TWO avoidable stops applies specifically to the nine listed MPW-101..103 GPU jobs.

### Current post-result correction (do not rewrite original rows)

- MPW-102B Granite amended completion job: 6adbd71c046eb82b1ecd7858.
- MPW-103 Qwen amended completion job: 6adbd71e046eb82b1ecd785a.
- Transparent after-outcome amendment: mpw-runtime-recovery/AMENDMENT_001.md.
- SHA-verified single-literal source changes committed before amended job submissions at new freeze bd9c54d9911581ca077d7f85d7122c681fd04871.
- Only in-script caps change from 65m to 95m, provider hard timeout 75m to 100m, same L4 hardware, cases and hypotheses.
- Original no-validation statuses remain historical facts, regardless of repaired jobs' outcomes. The new runs must be labeled **post-result repaired completions**, not pristine original prospective replications.

## Root-cause and forward controls

Research budgets are governance constraints, not target-phenomenon invariants. Comparing an overpadded runtime projection with an arbitrarily reduced internal cap, despite an adequate provider timeout, destroys valid scientific opportunities and must not become an acceptance rule.

For every future MPW program:
- Report observed CPU/GPU pilot throughput, startup, unpadded forecast, padded forecast, chosen hardware, provider maximum, and approximate worst-case cost BEFORE validation.
- Do not introduce an internal cap lower than provider hardware timeout unless the user explicitly approved that spending/window limit or it is a documented technical necessity. Never call it a scientific invalidation.
- If a padded forecast exceeds some preferred schedule but the unpadded job fits the authorized provider limit, **WARN/REPLAN**, do not discard validation. Increase provider window or choose faster hardware prospectively when needed.
- If the work cannot fit *any* authorized provider window, report NOT EXECUTED (resource blocked), never NOT_CONFIRMED about the target hypothesis.
- Keep research validity gates (task ability, intervention correctness, data independence, numerical floor) fully separate from queue/budget/time choices.
- Preserve failures, indeterminacy and observed null effects, and never rerun tests selectively to chase favorable results.

Auditor's scope is MPW-101..103 on the connected HF account as above. Other repositories, local compute experiments and unpublished external histories are not implicitly cleared.
