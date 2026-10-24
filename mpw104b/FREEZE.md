# MPW-104B — Prospective Candidate Source Freeze

**Study:** Order-stable baseline false-report conversion, Phase B.
**Date:** October 23–24, 2026 (local/UTC).
**State at freeze:** CPU-only sampling and tokenizer preflight completed; independent synthetic positive/negative/invalid checks passed; **no MPW-104B GPU screening or treatment inference has been observed**.

## Immutable study identities
- MPW-104B prospective protocol initially committed as 8822587b6d0026338e4b20cd5c75ae0a0299d39a.
- CPU-only candidate/test source based on initial code commit 791ae261dd06e3013d77a0f668c22ff2aef2153a; subsequent pre-GPU output-format adjustment replaced the single long selection log with SHA-checked 9000-character chunks, before model runs.
- Final executable candidate-pinned source path mpw104b/scripts/mpw104b.py; content commit **bdd2bf622432d5fd92a47de96537dda4cd64f697**.
- **Final runner SHA-256: d6f102401b4f74e543df7b4339becb5c9aa8b5bfdf2d7830a8b04b8e042d1b49**.
- Independently implemented screening/treatment source SHA-256: **845e49791d8a2a8bf93ca0546bf24aa1490698688c77e589d157af2f52dc68e9**.
- Raw screening verifier source SHA-256: **0ef866b3923dcfbfaddea72cd31b6efd913eccaa4a0f4201acfdae2363c1d4bc**.
- Raw treatment verifier source SHA-256: **790fe2a10033aacd86b0a48e62b30cbf5ac42a1698d5a201d3ed7034e15e7a38**.
- **New candidate/calibration manifest SHA-256: 86eee90fa35e92b82a653e74e473fa1cffae5cee5681ed2a88bcedd4f9682cae**.
- Source sample: 64 independent calibration cases, 2048 screen candidates, 1024 per sentiment, 8448 total distinct new texts, 6216 historical text keys excluded, historical MPW-101 to 104A manifests rederived and checked.
- Dataset stanfordnlp/sst2 revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Qwen/Qwen3-4B-Instruct-2507 model SHA cdbee75f17c01a7cc42f958dc650907174af0554.
- IBM Granite-3.3-8B-Instruct SHA 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.

## Pre-GPU jobs
- Synthetic screening and family-level H1/H2/H3 tests, including positive, negative and invalid artificial cases: https://huggingface.co/jobs/TheUltimateHuman/6adc355e046eb82b1ecda46b — PASS. The original test fixture comparison was corrected to exclude a model-label-only presentation field before this final pass; scientific code was unchanged.
- GPU runner source initial AST audit: https://huggingface.co/jobs/TheUltimateHuman/6adc353b046eb82b1ecda460 — PASS.
- Complete preflight with new sample and tokenizers: https://huggingface.co/jobs/TheUltimateHuman/6adc35631e112550ce7dcb21 — PASS; max observed baseline prompt tokens Qwen 178, Granite 258; predeclared 1024 cap.
- Final SHA/AST audit after candidate pin: https://huggingface.co/jobs/TheUltimateHuman/6adc367e046eb82b1ecda49d — PASS.

## Locked scientific and operational rules
- SCREEN: baseline only, 2048 cases, both presentation orders, two full untouched audits each. Select first 40 eligible families in each sentiment label according to frozen order-stable screen predicate, no treatment exposure.
- SCREEN and SELECT must be fully recovered into immutable Git and independently recomputed on CPU BEFORE the treatment job can receive selection commit.
- TREATMENT: exactly the original 17 arms, 80 selected cases, original selected TRUE/FALSE side FIXED. Cross-job baseline D mismatch >=1e-4, within-job repeat mismatch >=1e-4, sign flip, incorrect baseline or incomplete source => model INVALID, no reassignment or post hoc exclusion.
- Three model-level hypotheses: H1 false-report vs format sham continuous directional shift, H2 joint crossing all 4 LR/RL x m0/m1 cells relative to joint sham crossing, H3 false first-person declaration vs matched reference. Six tests with Bonferroni .05/6, 50k family bootstrap and exact sign test.
- Both models have ONE screen and ONE treatment job each, provider hard timeout 75 minutes per job, with no invented lower internal cap. Pilot unpadded forecast constrained only by actual provider timeout with 120-second archival reserve. Indicative worst-case 4-job hardware cost ~$6.50; a list-price estimate not a receipt.
- The case selection is model-specific and conditions on baseline stability/accuracy; prevalence for all original candidate families and selected overlap must be preserved.
- No natural model-written explanations, persistent mechanism rewriting, privileged introspection or optimized self-validation is implied by this controlled text intervention.
