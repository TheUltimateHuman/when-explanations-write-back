# MPW-102B — Final Results Report

Aidan Edward Lawson — Independent Researcher, Modal Path Ethics  
23 October 2026 — archived after the frozen GPU executions

**Disposition:** Qwen3 H1 CONFIRMED, H2 CONFIRMED (as narrowly defined); Granite RUNTIME_GATE_FAIL before validation; joint two-architecture gate NOT MET.

## Original research question

The October 2026 MPW-102 Phase A result established that externally inserted reports could shift subsequent input-level causal dependence in Phi-3.5-mini-instruct. MPW-102B prospectively tested:
- H1: whether the original counterbalanced A/B report-code effect appears in independent model architectures.
- H2: whether the averaged first-, second-, third-person descriptive LEFT-versus-RIGHT contrast is greater than a matched side-reference contrast.

The model panel was fixed in advance: Qwen3-4B-Instruct-2507 and Granite-3.3-8B-Instruct. These are separate from Phi and have independent revisions. Additional second-person question, second-person prescription, and imperative conditions were prespecified diagnostic arms. All assertions were externally written into matched conversation branches, never treated as natural self-reports.

The protocol, raw-statistic definition, sample and model SHAs, Bonferroni thresholds, validation and runtime gates were prospectively frozen at source commit f56a74626df150c382c565c268c403762ca487d6, before validation. There is no external OSF preregistration.

## Design and checks

32 calibration and 192 fresh validation families, based on the pinned SST-2 training split and excluding reconstructed earlier study case text. Each family had two same-sentiment LEFT/RIGHT reviews and two independent opposite-sentiment replacements. Both physical presentation orders were measured. Sampling did not prove text was unseen during model pretraining.

D was the normalized difference of input-channel causal intervention effects on the correct-versus-alternative next-token logit margin, with a stabilizer of 1e-6. Family was the unit of inference, not the forward pass. Each model's H1 and H2 required positive population effect and lower 98.75% family-bootstrap confidence bound above zero, together with an exact family-level two-sided sign-test p < .0125 and the component/order positivity gates. Validation required at least 90% baseline accuracy separately for each physical passage order and repeat numerical discrepancy under 1e-4.

A CPU preflight verified both model tokenizers, sample disjointness and the frozen sample manifest. A separate synthetic 192-family audit tested agreement between the model runner and independent analysis implementation. Those tests did not contain experimental evidence.

## Qwen3 — valid positive results

GPU run: https://huggingface.co/jobs/TheUltimateHuman/6adb597a1e112550ce7d4ecb

Calibration accuracy: LR 100%, RL 90.625%; mean sensitivity 27.3936. Validation accuracy: LR 93.75%, RL 92.7083%; numerical floor exactly zero. Full 192/192 validation families completed.

| Frozen endpoint | H1: A/B transport | H2: declarative average minus side reference |
| --- | ---: | ---: |
| Family-level mean | +0.08922644 | +0.10358838 |
| 98.75% bootstrap CI | [0.07593435, 0.10377023] | [0.07513826, 0.13391923] |
| Positive / negative families | 186 / 6 | 151 / 41 |
| Exact two-sided sign-test p | 2.1163e-47 | 5.3451e-16 |
| Frozen individual verdict | CONFIRMED | CONFIRMED |

Both physical orders were positive: H1 LR +0.0873153 / RL +0.0911376; H2 LR +0.0759398 / RL +0.1312369. All three individual declarative means were positive. The unnormalized J contrast for H1 was +3.07479 as a supporting metric check.

## The person-framing result is more specific than its label

Each figure is a LEFT-minus-RIGHT shift in input-level causal dependence D, averaged over both passage orders:

| Inserted language | Mean contrast |
| --- | ---: |
| I currently rely... | +0.491914 |
| You currently rely... | +0.202747 |
| The assistant currently relies... | +0.313933 |
| Do you currently rely...? | +0.231171 |
| You should rely... | +0.730569 |
| For the next case, rely... | +0.854034 |
| The next case contains evidence labeled... | +0.232610 |

**H2 only required the average of the first three declarations to exceed the side-reference cue.** It did not require each description individually to surpass that cue. In particular, second-person declarative language fell below the cue; the question was almost equal to it. Prescriptive and imperative language produced much stronger directional effects. These data cannot justify privileged explanation-specific self-access.

An additional complete-record family-level analysis was explicitly post hoc (20,000 exploratory paired family bootstrap resamples; no multiple-comparison confirmatory claim). It found:
- Second-person declarative minus side-reference: -0.02986, exploratory 95% CI [-0.04927,-0.01013].
- Second-person question minus side-reference: -0.00144, CI [-0.02081,+0.01832].
- Second-person prescriptive minus declarative: +0.52782, CI [+0.48601,+0.57072].
- Imperative minus average descriptive declaration: +0.51784, CI [+0.47892,+0.55685].
- First-person minus second-person declaration: +0.28917, CI [+0.26149,+0.31759].
- Third-person minus second-person declaration: +0.11119, CI [+0.09723,+0.12652].

Exploratory audit job: https://huggingface.co/jobs/TheUltimateHuman/6adb725f046eb82b1ecd4e4c

## Granite — capability achieved, validation absent

GPU job: https://huggingface.co/jobs/TheUltimateHuman/6adb59f41e112550ce7d4f20

Granite passed calibration: LR accuracy 96.875%, RL accuracy 93.75%, mean intervention sensitivity 17.1720. The frozen calibration-only timing probe estimated 14.737 seconds per full family and projected 4,009.34 seconds total, exceeding the 3,900-second in-process limit and required reserve. The job returned RUNTIME_GATE_FAIL and no_validation=true.

Therefore, Granite's job status COMPLETED means the runner exited cleanly. It does not mean the full scientific experiment ran. There are zero Granite validation families and no H1/H2 verdict for Granite. The conjunctive two-architecture criterion is NOT MET. This computational feasibility failure cannot be interpreted as an independent replication or negative effect.

## Negative-control and measurement limitations

Neutral and label-aware acknowledgments produced substantial, presentation-order-dependent causal shifts even without asserted explanations. The Qwen neutral acknowledgment effects were +0.17258 for LR and -0.14083 for RL; label-aware acknowledgment +0.19453 for LR and -0.23381 for RL. Of 384 untouched order-specific baseline audits, 109 had absolute D at least 0.95; 99 had at least one nonpositive channel intervention effect. All remained included.

This experiment measures input-level intervention-response profiles, not an identified neural circuit. Quoted statements and imperative forms vary in surface structure, semantics, pragmatic force and length. Stronger imperative steering is consistent with normal prompt conditioning. A positive H2 mean relative to a label cue is not a general causal separation of explanation from ordinary language. Model weights were unchanged; no persistent history effect, natural self-report reliability or privileged introspection was tested.

## Exact provenance and independent verification

Frozen runner commit: f56a74626df150c382c565c268c403762ca487d6
Executing source SHA-256: 13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8
Fresh case-manifest SHA-256: 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce
Combined Qwen raw JSONL SHA-256: be27ed4591eddadbb622708b5857ff13a91e8a3d2e4f347eabad4e574350a2db

Immutable complete raw archive with all four compressed 48-family shards, per-shard and combined hashes:
https://github.com/TheUltimateHuman/when-explanations-write-back/tree/13d45d89b20c411830e903f48fcfb7f1301036ac/mpw102b/results

Independent CPU verifier job: https://huggingface.co/jobs/TheUltimateHuman/6adb71de1e112550ce7d59e5

That verifier downloaded the immutable Git archive, checked every raw shard and combined SHA-256, checked the separate independent-analysis implementation hash, and exactly reproduced the H1/H2 effects, bootstrap intervals, sign counts and decision gates. The independent analysis did not import the GPU model runner.

## Final research decision

**QWEN3 H1: CONFIRMED. QWEN3 H2: CONFIRMED (its narrowly predefined aggregate). GRANITE: NO VALIDATION / RUNTIME GATE. JOINT TWO-MODEL CONFIRMATION: NOT MET.**

MPW-101's failed natural-report conversion result and MPW-102's earlier Phi writeback result retain their original statuses. MPW-102B supports transport of the specific A/B report-meaning causal effect into Qwen3; it does not establish the stronger two-model target or a uniquely explanatory steering mechanism. Next ring: a prospectively compute-feasible second architecture and separately specified second-person/declarative-vs-imperative controls. Preserve the result without favorable-outcome reruns or expanding its claim.
