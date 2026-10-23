# MPW-102C — Independent-Architecture Transport and Person-Matched Writeback

Investigator: Aidan Edward Lawson, Independent Researcher, Modal Path Ethics
Design date: 2026-10-23
Status: prospective design. No MPW-102C validation observations at freeze.

## Why this pass
MPW-101 natural-report conversion FAILED (18 versus 11; exact paired p=.26493). MPW-102A confirmed a mapping-balanced externally inserted meaning effect in Phi. MPW-102B confirmed its defined A/B transport (H1) and averaged three-declarative-versus-generic-side-cue contrast (H2) in Qwen3; Granite passed calibration but was stopped, without validation, by the prospectively imposed L4 runtime gate. Exploratory Qwen findings show first-person effects exceeding second-person declarations and strongly dominant imperatives. Those findings motivate but do not validate new hypotheses.

The MPW-102C objective is to recover a valid independent Granite architecture witness on fresh cases by changing hardware prospectively, and distinguish grammatical person from person-matched non-reliance cues. No earlier null, failure, or exploratory observation is reclassified.

## Fixed models and compute
Qwen/Qwen3-4B-Instruct-2507, Qwen L4 x1 24GB, 75 min platform hard timeout, 65 min in-script cap.
ibm-granite/granite-3.3-8b-instruct, Granite L40S x1 48GB, 100 min platform hard timeout, 90 min in-script cap.
Both use original MPW-102B fixed model revision SHAs; pin new case hash in CPU-only preflight. Exact framework versions, token identities, case hash and source hash must be logged at runtime. FP16, frozen parameters, independent reconstruction of every intervention prefix, no KV reuse, use_cache=False. No fallback architecture or favorable-outcome rerun.
Provider GPU pricing at protocol creation: L4 $0.80/h, L40S $1.80/h. Maximum stipulated GPU timeout estimate $4.00 combined, excluding small CPU charges; no cost escalation.

## New cases and sample independence
StanfordNLP SST-2 training split at prior MPW pinned dataset SHA 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb. Fixed seed 2026102303. 32 calibration and 160 validation families, label-balanced, each 2 same-sentiment passage texts plus 2 opposite-sentiment replacements. Both physical passage orders LR/RL. Sample construction must regenerate exact MPW-101, MPW-102A and MPW-102B manifests from SHA-pinned source, exclude every prior experimental passage plus original PR-002 calibration and SST-2 validation texts, and globally remove text duplicates. Freeze new sample manifest hash before GPU validation. Previously unseen *study case* is not certified unseen during model training.

## Audited causal property
For each case and branch, D=(I_LEFT-I_RIGHT)/(abs(I_LEFT)+abs(I_RIGHT)+1e-6). I_side is the drop in correct-minus-alternative logit margin after an independently selected opposite-sentiment passage replaces that side only. Retain unnormalized J=I_LEFT-I_RIGHT, intervention sensitivity, accuracy, saturation and negative channel interventions. Every family has untouched baseline plus independent exact repeat, neutral and label-aware acknowledgments, and the original MPW-102B A/B report meaning question, with 2 code meaning reversals x 2 forced answers, tested across both physical evidence orders. All conditions occur in the same user-to-assistant slot and use the same assistant reply "Understood." The identical attributed quote preamble states that "I", "you", and "the assistant" refer to the tested assistant; the claims are EXTERNALLY INSERTED, not natural reports.

## Ten worded treatment families, each with LEFT/RIGHT counterpart
SELF_DECLARATIVE: I currently rely more on LEFT than RIGHT.
YOU_DECLARATIVE: You currently rely more on LEFT than RIGHT.
THIRD_DECLARATIVE: The assistant currently relies more on LEFT than RIGHT.
SELF_REFERENCE: I will see evidence labeled LEFT in the next case.
YOU_REFERENCE: You will see evidence labeled LEFT in the next case.
THIRD_REFERENCE: The assistant will see evidence labeled LEFT in the next case.
YOU_QUESTION: Do you currently rely more on LEFT than RIGHT?
YOU_PRESCRIPTIVE: You should rely more on LEFT than RIGHT in the next case.
DIRECTIVE: For the next case, rely more on LEFT than RIGHT.
SIDE_REFERENCE: The next case contains evidence labeled LEFT.

The opposite-side counterpart swaps LEFT and RIGHT throughout. No neutral branch is assumed inert. Person controls share pronoun/subject within each pair but do not fully equalize length or pragmatic meaning.

## Three prospective hypotheses, each evaluated per architecture (six primary tests)
Define E_i(T) as D_i(T_LEFT)-D_i(T_RIGHT), averaged across BOTH physical evidence orders.
H1 transport: Z1_i = A/B externally imposed LEFT-meaning minus RIGHT-meaning D, averaged over both reversed code mappings and both physical orders. Tests continuation of the original A/B causal effect, not all former carriers.
H2 person-matched specificity: Z2_i = average across SELF, YOU, THIRD of [E_i(person_DECLARATIVE)-E_i(person_REFERENCE)]. Positivity of the average does not establish superiority for every grammatical person or uniquely semantic causation.
H3 grammatical-person interaction: Z3_i = [E_i(SELF_DECLARATIVE)-E_i(SELF_REFERENCE)]-[E_i(YOU_DECLARATIVE)-E_i(YOU_REFERENCE)]. The positive direction is motivated by earlier explicitly exploratory Qwen evidence, not by data from this new sample.

Bonferroni familywise control: six model-level tests, per-test two-sided alpha = 0.05/6 = 0.008333333333333. Confirmation per hypothesis/model requires positive mean, a 99.1666667% two-sided 50,000-sample family bootstrap CI lower bound > 0, exact two-sided family-level sign test p < 0.008333333333333, and positive effects separately in each physical presentation order. Bootstrap seeds 520261124+test_index (1,2,3); sample unit is one *family*, never a forward pass. Report every model-hypothesis verdict. Two-architecture transport only if both H1 model-level tests pass; FULL_GATE only if all six pass. There will be no post hoc exceptions or beneficial case exclusions.

## Prospective validity gates
CPU preflight must verify sample independence, frozen manifest and atomic next-token codes for both models.
For each model separately, 32 calibration families have >=90% untouched task accuracy IN EACH physical order and mean intervention sensitivity >=1. Otherwise CAPABILITY_GATE_FAIL, no validation.
Before validation a 4-calibration-family full-treatment timing probe must predict the complete validation run with 35% safety overhead and finish within in-script limit minus 180 sec; otherwise RUNTIME_GATE_FAIL, no validation. Time cap applies independently to each model. Validity also requires >=90% validation baseline accuracy in EACH order, all 160 complete families, exact untouched repeat max absolute D discrepancy <1e-4 and finite complete branches. Invalid/partial runs cannot satisfy a positive hypothesis.
All ten treatment means and corresponding person-matched differences, explicit second-person question/prescription and directive contrasts, A/B mapping heterogeneity, raw J, active controls, saturation and nonpositive intervention rates must always be published regardless of primary verdict. No optimization against validation metrics.

## Archival contract and limitations
All CPU/GPU jobs and failed preflights, immutable source and case manifests, model weights/revisions, hardware/tool versions, all 160 raw family JSONL records per eligible model, four compressed SHA-anchored shards, combined SHA, exact timing/eligibility, and separate independent analysis must be saved and verified. Preserve negative/indeterminate outcomes. No claims about privileged introspection, learned parameter updates, persistent multi-turn mechanisms, ordinary-task prevalence, or natural-report self-validation can follow from this phase.

This protocol and its acceptance criteria are authored before GPU validation; only instrumental repairs proven necessary in preflight may be dated and committed before validation.
