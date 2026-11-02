# MPW-106 — Pre-Inference Source-Construction Refactor Note

**Classification:** PREVALIDATION IMPLEMENTATION CHANGE, made **before any MPW-106 GPU inference, screening, report write or memory-retrieval results**.

The first MPW-106 CPU-only preflight used an inherited sampling method that recursively regenerated prior MPW-101 through MPW-105/103I case banks multiple times. This was slow because reconstructing MPW-103I separately replays the same ancestral corpus again.

Original preflight: https://huggingface.co/jobs/TheUltimateHuman/6ae821bfc78863f9c6301405, executing source commit 1c4c90ce38ebeb327df10370566914d3eb6a3a78, initial source SHA 8697694882edab5f6f7c78295f55f6f49d6b5afb092b56e561ed334baa1a23b7.

A prospective implementation change at Git commit **8bbdc1fe581e5a0d0d6bfb4e7b6455466e733b31** reconstructs all earlier case banks once and then applies the exact same legacy eligibility/exclusion/sampling procedure to reproduce MPW-103I by seed 2026102501 from the recovered historical exclusion set. It demands the immutable MPW-103I case-bank SHA **00cf578b03d0aeabc08b0226c5d84702695e9aa3f5b3264392b31d914526c20a** before accepting any fresh MPW-106 sample. It then adds those original MPW-103I source texts to the exclusion set and draws the MPW-106 sample with the original frozen seed 2026110106 and original 32+2048 cardinality. If the previously published machine source cohort cannot be reconstructed byte-identically, the optimized preflight **FAILS CLOSED**.

Optimization validation job: https://huggingface.co/jobs/TheUltimateHuman/6ae82688c78863f9c6301642. Results of this and the original preflight remain pending at time this note was authored. Independently authored 2048-case synthetic selection regression PASSED for the refactored source at https://huggingface.co/jobs/TheUltimateHuman/6ae826e6c78863f9c63016c2 .

**No scientific hypothesis, hard threshold, sample seed, model revision, raw-GPU treatment, bootstrap, positivity gate or outcome-based selection is altered.** The only methodological change is avoiding redundant recomputation of already byte-anchored historical source generations. Both source versions and CPU jobs remain in Git/HF history. Do not claim the refactor reproduced the legacy cohort until the respective CPU job reports the exact original SHA.
