# MPW-103 — Prospective Prevalidation Freeze

**Aidan Edward Lawson — Modal Path Ethics**  
**Date:** October 23, 2026.  
**Status at this freeze:** CPU-only preflight COMPLETE and syntax/synthetic tests PASS. No MPW-103 GPU calibration or validation output has been observed.

## Immutable anchors

- Prospective design: mpw103/PROTOCOL.md; initial Git commit 5df95041bbb5d344b083f358710f8306c76952a3, with 1,024-token hard input cap explicitly committed before preflight in c23668e258e6104b30c15d4e2ebd68568b623817.
- Final runner source Git commit before this freeze: 5284881ca425efe06df0e96813c01c4eea666e47.
- **Final runner byte SHA-256:** 78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba.
- Independent analysis SHA-256: 5f715b181679c6f23768319d6056cbcd6160d07987878d86c8c50c9b27220e9a.
- Raw archival verifier SHA-256: cd325534c9412db11fc314c7fd62f29869219b6ad548cdf1ec9f08e8958dfc0b.
- **Fresh case manifest SHA-256:** 370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b.
- 32 calibration families + 128 new validation families, 640 distinct evidence passages. Reconstructed 101, 102A, 102B, 102C historical manifests matched; 4,936 historical text keys excluded.
- Pinned SST-2 revision: 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Pinned Qwen3-4B-Instruct-2507 revision: cdbee75f17c01a7cc42f958dc650907174af0554.
- Pinned IBM Granite-3.3-8B-Instruct revision: 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b.
- Tokenizer preflight: Qwen A [32], B [33], positive [30487], negative [42224]; Granite A [51], B [52], positive [18502], negative [15272]. All atomic.
- Maximum preflight input length (calibration + validation candidate histories, all 3 audit variants, both physical orders, both mappings, both final meanings): Qwen3 **499**, Granite **572** tokens. Both below prospectively frozen 1,024 limit.

## Evidence of no prevalidation leakage

1. Syntax/byte audit of initially unfrozen runner: Hugging Face CPU job 6adbb1b7046eb82b1ecd68e3, PASS.
2. CPU-only fresh-family sampling and maximum token context: Hugging Face CPU job 6adbb209046eb82b1ecd691b, PASS. Its sample SHA was pinned in Git only afterward; zero model forward passes were performed.
3. Frozen source, independent analysis and verifier AST+SHA checks: CPU job 6adbb3041e112550ce7d7e45, PASS.
4. Synthetic positive and negative 128-family analysis agreement: CPU job 6adbb281046eb82b1ecd692f, PASS. Synthetic results have **no** scientific interpretation and cannot establish any study outcome.

## Fixed statistical gates and research limits

H1 (seven earlier reports with final fixed), H2 (dose E8 minus E2), H3 (report versus arbitrary-code past), H4 (order at equal counts), each in both Qwen and Granite. Eight family-level tests at Bonferroni alpha 0.00625 each; positive mean, positive both evidence orders, lower 99.375% family-bootstrap 50k resample CI > 0, and exact family sign-test p < 0.00625. 128 COMPLETE new families and untouched accuracy >=90% per order with exact numerical-repeat floor <1e-4 are mandatory. Each model calibration gate requires 32 families at >=90% per order and mean sensitivity >=1, followed by a 4-family complete-branch runtime projection with 35% safety reserve before validation.

Models: Qwen L4 x1 max 75 min provider timeout/65 min runner; Granite L40S x1 max 100 min provider/90 min runner. The worst-case GPU cost at list rates is approximately $4 across both jobs, not a provider billing receipt. Do not run additional GPUs to chase favorable outcomes.

**Scientific restraint:** externally inserted report history can probe dependence on prior context, but cannot prove that a model autonomously wrote or validated its own explanations, or that persistence remains after report history deletion. Existing fabricated-history and conversation-history prior art limits novelty claims.
