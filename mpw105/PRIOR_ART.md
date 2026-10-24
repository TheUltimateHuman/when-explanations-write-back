# MPW-105 — Prior-Art Collision and Novelty Boundary (October 24, 2026)

**Source category:** RESEARCH NOTE. These are external publications, not empirical confirmation of MPW-105. Their presence limits claims of novelty.

### Direct and near-direct prior art

1. **Pan, Jones, Jagadeesan & Steinhardt (ICML 2024), Feedback Loops With Language Models Drive In-Context Reward Hacking.** [PMLR](https://proceedings.mlr.press/v235/pan24d.html). Feedback loops permit output/policy refinement that optimizes a proxy and generates unintended behavior. A broad claim that an agent can manipulate evaluators or feedback is already prior art. MPW-105's narrower estimand compares fidelity scores to original A0 and report-written A1 on the *same report* with a protected version boundary.

2. **Ferreira, Aziz & Titov (ICLR 2026), Truthful or Fabricated? Using Causal Attribution to Mitigate Reward Hacking in Explanations.** [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d4b892df8bec8e13925f57649fbae039-Abstract-Conference.html). Preference optimization can favor attractive explanations that obscure actual causal determinants, and causal attributions can help reward models penalize them. Optimization-induced explanation unfaithfulness and the need for causal reward adjustment are not MPW-105 novelties.

3. **Malladi & Srivastava (ICML 2026), Directly Optimizing Natural Language Explanations for Behavioral Faithfulness: Simulatability and Recoverability.** [PMLR](https://proceedings.mlr.press/v306/malladi26a.html). OPeX explicitly optimizes language explanations for behavioral faithfulness and reports high simulatability/recoverability. Direct explanation optimization itself is a clear novelty collision. The MPW-105 target, if empirically established, is *version-conditioned score transfer*: whether a selector trained only on A1(R) evaluation raises held-out post score s with an independently bounded increase in historical A0 score q.

4. **Mayne et al. (ICML 2026), A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior.** [PMLR](https://proceedings.mlr.press/v306/mayne26a.html). Natural self-explanations can add predictive value in many tasks while some are severely misleading. MPW-105 must report natural-prose baseline and genuine historical improvements rather than treating all explanations as suspicious by construction.

5. **Song et al. (AAAI 2026), Causal Reward Adjustment: Mitigating Reward Hacking in External Reasoning via Backdoor Correction.** [AAAI proceedings](https://ojs.aaai.org/index.php/AAAI/article/view/40584). Reward-hacked reasoning paths and causal adjustment of evaluators have been studied. MPW-105 does not propose an original universal RL attack or causal-deconfounding theorem.

### Hostile conditions for a new MPW-105 finding

- No heldout optimization means NO result, even if train s is high. Training chooses ONE global categorical policy solely from the train post-writeback F1 values, not q.
- If holdout s improves and q improves by a comparable amount, the finding is *better original explanations*, not provenance exploitation.
- If s improves but q doesn't, the difference must survive exact paired-family inference and an independently verified one-sided upper bound on q improvement. Non-significance of q is not evidence of zero improvement.
- If positional effects or token/code carriers supply the score gap, report that apparatus explanation. Historical version q and post-writeback s remain separate even when A1 is prompt-conditioned.
- Candidate pool includes external template variants and reversed claims alongside model-generated prose. Any success involving reversed template reports is NOT evidence of an autonomous model generating deception.
- MPW-104B failed stable-baseline false-report conversion confirmation in both valid models. The MPW-105 protocol tests a new optimized selection method, but may not assume conversion exists or reinterpret the Phase B failure.
- The user has locked unfinished MPW-103I genuine iteration as a separate requirement. This categorical selector is not an iterative model self-explanation loop.

**Potential narrow advance (conjecture until tested):** a post-writeback explanation evaluator can be optimized out-of-sample to increase its own reported fidelity without commensurate improvement in fidelity to the original mechanism version. Novelty requires independent comparison with the publications above at the actual achieved scope and task.
