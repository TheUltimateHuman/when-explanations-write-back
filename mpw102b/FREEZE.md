# MPW-102B — Frozen prevalidation state

**Freeze date:** 2026-10-23 (pre-GPU; no new validation outcomes observed).

- Prospective protocol: mpw102b/PROTOCOL.md on branch mpw102b-20261023-prevalidation
- CPU-only sample/token preflight job: 6adb58bd046eb82b1ecd45be
- Source syntax/integrity audit job: 6adb59511e112550ce7d4eb7
- Exact executing runner source SHA-256: 13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8
- Script candidate Git commit: c6e9c0e045ebb5b0a717502661c7ea52203b14b1
- Frozen MPW-102B family manifest SHA-256: 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce
- Historical MPW-102 sample SHA-256: 90ac38a668c6fa03ebdd1a37f294dc7280b24533b5d5caacbd8ed034f54549c5
- Model 1: Qwen/Qwen3-4B-Instruct-2507, revision cdbee75f17c01a7cc42f958dc650907174af0554
- Model 2: ibm-granite/granite-3.3-8b-instruct, revision 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b
- Data: stanfordnlp/sst2, revision 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb
- 32 calibration families; 192 new validation families. Both models must separately satisfy their prespecified eligibility gate before confirmation testing.
- Bonferroni four model-level primary tests at two-sided alpha .0125 each, family bootstrap 98.75% CI and exact family-level sign-test.
- H1 is original MPW-102 AB-coded report-meaning contrast averaged across both mapping reversals and both evidence display orders.
- H2 is (average of first-, second-, third-person declarative LEFT–RIGHT contrasts) minus neutral LEFT–RIGHT cue contrast, averaged across both evidence display orders.
- Secondary person treatments: second-person interrogative and prescriptive, bare imperative.
- GPU: max 75 min per model on L4; internal 65 min runtime / calibration-only projection gate before any validation.
- Raw records are sharded and hash-anchored. Failures and ineligibility must be disclosed. No repeat merely to seek confirmation.

No cross-architecture or specific explanatory effect is claimed in advance. The prior Phi success and MPW-101 failure remain separate.
