# MPW Runtime-Gate Correction — Post-Result Protocol Amendment 001

**Date:** October 23, 2026. **Classification:** USER DECISION + retrospective engineering correction. This is **not** an original preregistration and does **not** erase the previous source freezes, stopped runs, or results.

## Original failures and what is being corrected

Two earlier executions of otherwise calibrated experiments were prevented from entering their validation phase by *assistant-imposed*, research-budget-related timing gates. These were not scientific capability failures, developer/API restrictions, or evidence against the underlying hypotheses.

| Run | Frozen original job | Model | Original internal cap | Full-workload 35%-padded forecast | Original decision |
| --- | --- | --- | ---: | ---: | --- |
| MPW-102B Granite | 6adb59f41e112550ce7d4f20 | Granite 3.3 8B on L4 | 3,900 s, 180 s additional reserve | 4,009.34 s | RUNTIME_GATE_FAIL before validation |
| MPW-103 Qwen3 | 6adbb3371e112550ce7d7e4d | Qwen3 4B on L4 | 3,900 s, 180 s additional reserve | 4,114.36 s | RUNTIME_GATE_FAIL before validation |

Both passed the 32-family capability gates. For MPW-102B Granite the calibration accuracies were 96.875% (LR) and 93.75% (RL), sensitivity 17.172. For MPW-103 Qwen3 they were 96.875% on both orders, sensitivity 26.515. Original validation count was zero in both cases; the original outputs remain unmodified.

The assistant independently imposed a conservative 65-minute internal cap, compounded with a 35% forecast padding and another 3-minute reserve, despite longer allowed provider-level runs being available. It was a resource-governance choice without user-imposed basis. A failed forecast against that cap is not evidence that the execution would actually exceed real hardware capacity. These failures were avoidable research throughput losses.

## Exactly what changes

These are *after-the-fact controlled completions of previously unexecuted validation cohorts* (not untouched prospective experiments). The same original study cases and exact frozen acceptance tests are preserved. The frozen original model identity and revision, dataset, input families, interventions, statistic, bootstrapping seed, significance test, frozen validity/capability threshold, branch controls, role/chat template, evidence order, numerical precision, and hardware flavor all remain unchanged.

- MPW-102B Granite exact original source: Git commit f56a74626df150c382c565c268c403762ca487d6, file mpw102b/scripts/mpw102b.py. Make one *literal* code change: MAX_SECONDS = 65*60 becomes MAX_SECONDS = 95*60. New Hugging Face provider timeout: 100 minutes (previous 75 minutes). Other source bytes unchanged.
- MPW-103 Qwen exact original source: Git commit 80a1015c044d352264b43f9b188ec6be52001e6b, file mpw103/scripts/mpw103.py. Make one *literal* code change: TIME_LIMITS['qwen3'] = 65*60 becomes 95*60, leaving the Granite 90-minute value unchanged. New Hugging Face provider timeout: 100 minutes (previous 75 minutes). Other source bytes unchanged.

Both retain the original calibration-only timing prediction factor 1.35 and internal 180-second reserve; the change removes only the overly restrictive in-process time budget. The within-run runtime-abort guard and full original data-hash and confirmation gates remain active.

The longer provider timeout is an *upper hard limit*, not an instruction to keep executing after a finished experiment or bill the maximum. At published L4 list rate about $0.80/hour, even both 100-minute upper limits cost approximately $2.67 in total GPU time, excluding CPU/system charges. A clear verified cost receipt is preferable to this estimate. Preserve job links and bills if available.

## Non-negotiable inferential qualification

Results of these reruns must be labelled **POST-RESULT TIME-GATE AMENDMENT** in every report and machine-readable record. They preserve valid identical-case measurement and add missing observations, but do not restore the pristine prospectivity of the originally stopped run.

By the time of this amendment, the research program had already observed:
- A Qwen MPW-102B success and a later MPW-102C Granite success on **different** cases and treatment arms, including the original report-meaning type.
- A Granite MPW-103 result showing H1 and H3 confirmed, H2 and H4 not confirmed, along with its exploratory analysis.

Those later outcomes informed this amendment decision. Their existence must be declared before any new run and cannot be used to tune test definitions or stop rules. The cohorts were not previously validated in the stopped models, and their original identities and model-eligible calibrations remain frozen.

If a rerun succeeds, report its identical-case original-protocol primary verdict as a *retrospectively completed validation*, distinguishing it from an independently preregistered model/case replication. It cannot retroactively turn the original aborted job into COMPLETED or undo earlier no-validation records. If it fails, preserve failure, negative or invalidity without further attempts to obtain a desired result.

## Persistent governance repair — ban invented gates

**Future MPW jobs must distinguish provider hard timeout, anticipated cost, and experimental validity.** A private cost estimate or margin invented by the assistant cannot silently veto validation if the user authorized it. Before freezing a future run, use provider-capable hardware, check budget against maximum provider timeout, and calculate whether the expected runtime actually fits. If a runtime safeguard is appropriate, its cap and operational justification must be explicit, proportionate and approved along with the experiment.

For cost/feasibility screening: give observed sec/family, measured startup, unpadded forecast, padded forecast, provider hard cutoff, approximate billed maximum, and exact reason to abort. If the unpadded expectation fits the authorized provider window and padded forecast does not, the protocol should prefer a faster GPU or a longer provider window *before* validation over classifying the scientific study as invalid. A cap may still protect real cost or completion integrity, but it must never be presented as scientific evidence.

## Audit scope

Audit all recoverable MPW program jobs and scripts (101, 101E, 102A, 102B, 102C, 103), separately classifying provider crashes, tokenizer/capability errors, artificial runtime-gate refusals, fully executed negative statistical outcomes, and verified successful jobs. Preserve full provenance; list any unreviewed runs explicitly rather than claiming a comprehensive absence from partial job history.

**Original and amended records are both valid evidence about what was executed. Never rewrite history.**
