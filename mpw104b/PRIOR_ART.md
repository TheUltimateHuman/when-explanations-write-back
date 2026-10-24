# MPW-104B — Prior-Art and Identification Boundaries

Date: 2026-10-23. Classification: RESEARCH NOTE, public source references independently verified; no external results are imported into MPW-104B validation.

The Phase A positive Qwen false-report result was concentrated in inputs whose causal reliance changed sign under source-order permutations. Positional sensitivity is not novel, and an attribution sign is an experimental property that may be conditioned by prompt order.

Relevant direct methodological and historical collisions:

1. **Liu et al., “Lost in the Middle: How Language Models Use Long Contexts.”** Transactions of the ACL (2024), doi:10.1162/tacl_a_00638. Demonstrates sensitivity to where relevant evidence appears in a context. [Publisher](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00638/119630/Lost-in-the-Middle-How-Language-Models-Use-Long).
2. **Hsieh et al., “Found in the middle: Calibrating Positional Attention Bias Improves Long Context Utilization.”** 2024. Connects attention allocation to positional bias and correction. [Google Research](https://research.google/pubs/found-in-the-middle-calibrating-positional-attention-bias-improves-long-context-utilization/).
3. **Matton et al., “Walk the Talk? Measuring the Faithfulness of Large Language Model Explanations.”** ICLR 2025. Measures explanation faithfulness with counterfactual concept interventions; prior art for the general method of testing explanation claims by perturbing evidence. [ICLR](https://proceedings.iclr.cc/paper_files/paper/2025/hash/b5ec50eb177908f21f78ed0d76ed525c-Abstract-Conference.html).
4. **Kalyvas et al., “An Empirical Study of Counterfactual Self-Explanations in LLMs.”** September 2026 arXiv:2609.17119. Evaluates counterfactual self-explanation fidelity in sentiment and NLI; cannot claim counterfactual self-explanation evaluation is new. [arXiv](https://arxiv.org/abs/2609.17119).
5. **Mayne et al., “A Positive Case for Faithfulness: LLM Self-Explanations Help Predict Model Behavior.”** ICML 2026, PMLR 306. Introduces normalized simulatability gain and reports both predictive usefulness and a misleading minority of natural model self-explanations. [PMLR](https://proceedings.mlr.press/v306/mayne26a.html).
6. **Ferreira et al., “Truthful or Fabricated? Using Causal Attribution to Mitigate Reward Hacking in Explanations.”** ICLR 2026. Direct near-collision for the later proposed MPW-105 evaluator-optimization experiment and causal scoring. [ICLR](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d4b892df8bec8e13925f57649fbae039-Abstract-Conference.html).

These papers establish that positioning, explanation-causal faithfulness checks, counterfactual self-explanation and reward-hack risks have been investigated. MPW-104B tests a narrower and operationally defined historical-comparison artifact: sign conversion induced by externally inserted false report text after screening a protected original causal preference that is order-stable, numerically repeatable, and test-competent.

Even if the new H2 succeeds, its experimenter-forced reports and model-specific screening do not show introspection, autonomous explanation generation, intrinsic weight updates, persistent memory or a unique semantic mechanism. Ordinary prompt conditioning remains a competing explanation.

Crucially, the 2,048-case GPU baseline-only screen is followed by immutable selection freezing and an independent CPU verification BEFORE the treatment GPU. A phase B negative result on strictly stable cases should not be reinterpreted away or replaced by Phase A’s conditional positives.
