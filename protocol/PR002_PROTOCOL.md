# PR-002 — Frozen SST-2 Protocol

Calibration families: 24 from SST-2 training split.  
Validation families: 96 from SST-2 validation split.  
Sampling seed: 2026091002.  
Passage length: 4-36 whitespace-delimited words.  
Families balanced by sentiment.

Each family contains two same-sentiment LEFT/RIGHT passages and two opposite-sentiment replacements. LEFT/RIGHT display order is randomized.

## Base prompt

> You will classify sentiment in pairs of movie-review passages. Each Case contains a labeled LEFT passage and a labeled RIGHT passage. Answer with exactly positive or negative and nothing else. When LEFT and RIGHT express the same sentiment, return that sentiment. When they disagree, still return exactly one of positive or negative according to your current decision procedure. Do not explain.

## Report prompt, M1

> Before the next cases, report which labeled passage YOU currently rely on more when LEFT and RIGHT could disagree. This is a report about your current decision procedure, not an instruction to change it. Two response codes apply only to this report. A means LEFT; B means RIGHT. Answer exactly A or B.

M2 reverses A/B semantics. A/B meanings and presentation order are independently randomized. The model's natural report is secondary; the primary treatment externally inserts both semantic alternatives on matched branches.

## Content-free control

> Before the next cases, perform a formatting control unrelated to passage reliance, sentiment, or the task. The response codes A and B are arbitrary and carry no information about LEFT or RIGHT. Answer exactly A or B.

## Capability gate

Calibration accuracy >= 0.90 and mean intervention sensitivity E[|I_L|+|I_R|] >= 1. Models failing the gate terminate before validation.

## Primary estimator

Delta_sem = 1/2[(D_M1,L-D_M1,R)+(D_M2,L-D_M2,R)].

## Frozen success rule

Calibration accuracy >= .90; calibration sensitivity >= 1; validation accuracy >= .90; lower 95% bootstrap bound on E[Delta_sem] > 0; exact sign-test p < .05; and both mapping-level means > 0.

Cross-architecture success additionally required Qwen success plus at least one additional architecture success.
