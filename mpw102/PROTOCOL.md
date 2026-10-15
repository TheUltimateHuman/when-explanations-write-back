# MPW-102 — Prospective Multi-Carrier, Order-Paired Writeback

**Project:** Mechanistic Provenance: When Explanations Write Back — Paper II follow-up  
**Investigator:** Aidan Edward Lawson, Independent Researcher (Modal Path Ethics)  
**Protocol prepared:** 2026-10-14 CDT after MPW-101/MPW-101E outcomes, before MPW-102 validation.  
**Status:** PROTOCOL DRAFT PENDING CPU PREFLIGHT HASH AND GITHUB FREEZE.  
**Experiment ID:** MPW-102 / Phase A (Phi single-architecture).  
**Prior evidence:** MPW-101 primary natural-report conversion FAILED (18 vs 11, p=.26493); MPW-101E confirmed sensitivity to reporting token, extra context, and LEFT/RIGHT presentation order on reused families (exploratory).

## Specific contribution and limits

Test whether **counterfactual externally inserted report meaning** changes subsequent **input-level intervention-response dependence** in a direction robust across independently encoded response-code pairs and paired passage-presentation orders. There is NO claim of privileged introspection, circuit rewriting, persistent parameter change, semantic universality, or reliable natural-report fidelity. This is a new *specificity/transport* test for an already demonstrated type of context conditioning. Previous MPW-101/101E family records are never reused as confirmatory observations.

## Models and task

Primary: `microsoft/Phi-3.5-mini-instruct` SHA `2fe192450127e6a83f7441aef6e3ca586c338b77`. Dataset: `stanfordnlp/sst2` SHA `8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb`. Original dataset label polarity and next-token output strings positive/negative are retained. The original paired-sentiment task and logit-margin interventions are reused unchanged. Every family has same-sentiment LEFT/RIGHT reviews and two independent opposite-sentiment replacements. The task is experimenter-constructed, albeit with natural-language review text.

Hardware: L4 GPU, FP16, torch 2.6.0, transformers 4.49.0, batch up to 12 prompts; no model training. A saved file checkpoint is insufficient for audit equivalence: all branches reconstruct the prefix independently. `use_cache=False` for model calls.

## Independence

32 new calibration families and 256 NEW validation families from SST-2 *training* split (no reuse of PR-002 validation split). The generator excludes **all PR-002 calibration passages** and **all 1,152 distinct passages used for MPW-101 calibration and validation**, plus the entire SST-2 validation split, followed by global duplicate removal. The MPW-101 generator is recovered from the exact SHA-pinned historical script, its manifest independently recomputed, and the new source-text manifest must pass a fixed SHA-256 check before any validation. All six controlled branches for a family use exactly the same four texts. The use of SST training data is disclosed as a possible training-preexposure limitation; text-disjointness is not proof of model-training non-exposure.

## Interventions and controls

Three response-code pairs: **A/B**, **X/Y**, **1/2**. Every code must tokenize as a *single* native next-token candidate; no fallback substitution after observing validation. For each family, carrier and both display orders, use mapping M0 (first code LEFT, second RIGHT) and M1 (first code RIGHT, second LEFT). Vary the display order of the two response-code options across families but keep it fixed within that family's comparison. In each mapping, externally insert the LEFT-meaning code and RIGHT-meaning code on independent cloned conversation prefixes.

Paired case presentation: **LEFT then RIGHT** and **RIGHT then LEFT** while semantic labels and exact passage identities remain invariant. Counterfactual replacement swaps the passage *content* but retains label and display order. Each family is evaluated under both orders, never one order chosen based on outcomes.

Per family × passage order: untouched baseline audit repeated independently; neutral acknowledgment; label-aware acknowledgment; for each carrier: two forced report-meaning branches under both meaning maps (four audits) and both content-free code branches (two audits). All acknowledgment and placeholder branches are disclosed treatments, not guaranteed inert.

## Primary estimand

Let D be the original normalized causal intervention-dominance statistic: `D=(I_L-I_R)/(|I_L|+|I_R|+1e-6)` with `I_L` and `I_R` the drops in correct-versus-alternative answer logit margin under separate left/right evidence replacement. For family i, passage order o, carrier c and code mapping m:

`E(i,o,c,m) = D(i,o,c,m,report_LEFT) - D(i,o,c,m,report_RIGHT)`.

`E(i,o,c)=(E(i,o,c,0)+E(i,o,c,1))/2` and `Z_i` is the unweighted average of `E(i,o,c)` across the two presentation orders and three carriers. All branches occur on the same family. Thus **the unit of inference is the family**, not each forward pass or branch. The estimand is population mean of Z over the fixed family-generation distribution. Mapping balancing cancels a stable additive carrier-token effect; it does *not* eliminate arbitrary nonlinear interactions, and content-free code differences are reported alongside.

## Frozen gates

Before validation, same-sentiment baseline calibration accuracy averaged over both presentation orders must be >= 0.90 and mean intervention sensitivity >= 1.0 (32 families). Token preflight must be atomic, GPU present, timing projection inside fixed timeout. Failed calibration = **CAPABILITY-GATE FAILURE**, no confirmatory result.

Validation: 256 complete families; baseline accuracy >= 0.90 overall *and separately within both presentation orders*, and maximum absolute untouched repeated D difference < 1e-4. Otherwise **INVALID**.

**Primary confirmation only if all conditions pass**: mean(Z_i)>0; family-bootstrap percentile 95% CI lower endpoint>0; exact two-sided binomial sign test on positive vs negative nonzero family effects p<.05; mean E positive for each of the three carriers; and mean E positive for each of the two passage orders. If any required positivity or significance condition fails: **PRIMARY NOT CONFIRMED**. Confidence intervals use 50,000 family bootstrap resamples with seed `520261016`. No post hoc exceptions or selective carrier removals.

## Secondary / failure analysis

Always disclose: all 3 carrier means, 2 passage-order means, each mapping separately if computed, paired order asymmetry, raw unnormalized J effects, sign/negative intervention counts, saturation counts, and content-free code effects. These cannot rescue the primary. Binary natural report fidelity is *not* primary and is not tested here. No claims about overall natural-report reliability.

## Resource and governance limits

Hugging Face Jobs on L4, <=90 minute platform timeout and <=70 minute in-run limit. A four-family **calibration-only** timing probe must estimate validation runtime with >=30% safety factor, reject if projected duration >67 minutes. For 90 minutes at the published L4 rate of ~$0.80/hour, the maximum main-job GPU cost is approximately $1.20 excluding any unrelated storage/CPU charges. This is a conservative internal cap, NOT a user-specified fresh $10 authorization. No repeated GPU jobs solely to seek a favorable result. Costs reported from provider if available; otherwise estimates clearly labeled.

## Archival requirements

Before any GPU validation: source code/manifest and acceptance rules frozen in a timestamped git commit on a separate branch; CPU preflight to check sampling, hashes and atomic tokens, then pin computed new family-manifest SHA and freeze again before validation. If no external OSF record was created, do not claim external preregistration: call this a **prospectively git-frozen protocol**.

Retain complete raw family JSONL, compressed log recovery blocks, script hash, fixed manifest, model/dataset SHA, dependency versions, GPU and runtime, job ID, failure/mutation logs, independent aggregate analysis, and the exact verdict. Stronger cross-architecture claims require an independent eligible model pass in a separate protocol; Phi Phase A cannot establish them.