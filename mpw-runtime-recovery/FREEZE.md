# MPW Timing-Gate Repair — Two-Run Post-Result Freeze

**Freeze date:** 2026-10-23. **Source category:** RESEARCH ARTIFACT / transparent post-result protocol amendment.

All changes were committed before the new GPU jobs were submitted. The *original* GPU calibration and runner outcomes, other model results, later independent-architecture findings and original publication claims are known to the investigator.

Amendment with prior knowledge disclosure: mpw-runtime-recovery/AMENDMENT_001.md, original Git commit ccb59e2ef35d73c2d1e56ac3c63d8022d78b72fb.

## MPW-102B Granite correction
- Original untouched runner Git ref: f56a74626df150c382c565c268c403762ca487d6.
- Original SHA-256: 13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8.
- Modified runner: mpw-runtime-recovery/scripts/mpw102b_granite_runtime_only.py.
- Modified SHA-256: f2d7f6d4a34ae3ebdebb44e6b6fe01856e814e00dfee089b807f20ec04cb4dfe.
- Byte identity except unique replacement MAX_SECONDS=65*60 -> MAX_SECONDS=95*60, verified independently on CPU Job 6adbd6fc046eb82b1ecd782e.
- Original validation case SHA-256: 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce (32 calibration +192 validation).
- Original model SHA Granite 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b, dataset SHA 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Original frozen H1/H2 model primary gates and bootstrap seeds unchanged; original 102B Granite had NO validation due to prior timing gate.
- New provider hard timeout 100m; hardware flavor remains L4x1.

## MPW-103 Qwen correction
- Original untouched runner Git ref: 80a1015c044d352264b43f9b188ec6be52001e6b.
- Original SHA-256: 78d24e2990fb1d24e9caddd2ce5b161c9554adfebf74ec9b9ab3f83894621bba.
- Modified runner: mpw-runtime-recovery/scripts/mpw103_qwen_runtime_only.py.
- Modified SHA-256: 153336fc9d93edafe1fad4d40d37d9f9cab101aa2aeda9c3c5d766e35dfd3cd4.
- Byte identity except unique replacement TIME_LIMITS['qwen3']=65*60 ->95*60 (Granite cap remains 90*60), independently verified in CPU Job 6adbd6fc046eb82b1ecd782e.
- Original case SHA-256: 370a225c22762ba97f4bac87692a9ff6cab032713d467f6a040ebcfd96d4f08b (32 calibration +128 validation).
- Qwen revision cdbee75f17c01a7cc42f958dc650907174af0554, dataset revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
- Original frozen H1/H2/H3/H4 family-level gates and seeds unchanged. Original Qwen had NO validation due to prior timing gate. Granite MPW-103 findings were known when this amendment was planned.
- New provider hard timeout 100m; hardware flavor remains L4x1.

## Mandatory recordkeeping and analysis
- Label every new run as POST-RESULT TIME-GATE AMENDMENT; the model validation cohorts were previously untested in the stopped model, but the broader research program results are known.
- Independently verify same calibration+validation manifest before execution and compare original revised code hash.
- Recover full raw observations, SHA-anchor compressed 48/32-case chunks, recompute with *original* independent analysis scripts frozen prior to the amendment, and publish a compound ledger without suppressing earlier stopped results.
- Original result is not retroactively changed, no second chance to select significance or cases. If a newly executed study fails hypotheses, that stays visible.
- Never claim the repaired run is equivalent to a pristine prospective independent replication.
