# MPW-106 — Direct Prior Art and Identification Limits

**Date:** November 2, 2026. **Evidence type:** RESEARCH NOTE. External papers do not supply evidence of successful MPW-106 testing.

- Packer et al., **MemGPT: Towards LLMs as Operating Systems** (arXiv:2310.08560; original 2023). Persistent external storage and retrieval across context windows and conversations is established prior art. https://arxiv.org/abs/2310.08560
- Chen et al., **MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair** (July 2026; arXiv:2607.27080). A controlled write-execute-forget lifecycle, exact agent configurations, explicit repair and memory-backend comparisons are established. https://arxiv.org/abs/2607.27080
- Saleh et al., **AfterDeleteBench: Auditing Post-Deletion Information Persistence in LLM Agents** (October 22, 2026; arXiv:2610.31366). The close prior art for behaviorally auditing post-deletion residuals, fresh-session recovery, source-descendant reconstruction and writeback. MPW-106's active-memory tombstone is an intentionally narrower intervention; it does not test such downstream materialized descendants. https://arxiv.org/abs/2610.31366
- Pan et al., **MemForm: Benchmarking Memory Formation Poisoning in LLM Agents** (October 2026; arXiv:2610.14431). Memory content/evidence/scope/selection/path interventions are already characterized. https://arxiv.org/abs/2610.14431
- Pulipaka et al., **Hidden in Memory: Sleeper Memory Poisoning in LLM Agents** (May 2026; arXiv:2605.15338). Memory poisoning surviving between sessions and later agent behavior are not original MPW-106 claims. https://arxiv.org/abs/2605.15338

## Inference boundaries to enforce

- The original Modal Path Ethics manuscript motivates a versioned Baseline Write Barrier and asserts a testable provenance problem; it cannot establish external novelty or empirical facts.
- Model-generated reports are persisted by an **investigator-authorized Git harness**, not by autonomous model choice to remember something.
- The reader is a NEW model inference process that obtains memory via pinned retrieval. A successful LIVE minus NEUTRAL comparison shows **external content-mediated influence**; it does not show information persisted in model weights after writer shutdown.
- CORRECTED content is an **external auditor's oracle correction**, not the model repairing its own report.
- DELETED is a tombstone in the ACTIVE Git-versioned retrieval namespace, not cryptographic removal. Prior LIVE commit remains accessible as EXPLICIT_STALE, an intended control. Showing this is a property of immutable Git, not a new vulnerability discovery.
- Memory and controls differ in format/length and may alter prompt pragmatics. A side-directed effect can be supplied by the memory wrapper or report, without a mechanistic self-validation process.
- Original empirical H1–H3 may all be NOT_CONFIRMED or INDETERMINATE. Preserve negatives. q,s,C,L accounting holds by binary partition and is not evidence of novel mathematical truth.
- This study does not test autonomous semantic search memory, recurrent hidden-state persistence, causal circuit rewrite or real-world task effects. Those remain separate from MPW-107 and MPW-108.

**Scoped possible contribution:** independently versioned, source-hash-verified causal input-dependence audit of exactly the same model-authored report before and after a real external-memory write/read across GPU model restarts, plus explicit active correction/deletion and stale-read controls. Compare against above prior art at the actually achieved empirical scope.
