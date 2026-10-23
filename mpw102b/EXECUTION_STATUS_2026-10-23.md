# MPW-102B execution status — 2026-10-23

**Research phase:** Prospectively frozen; CPU preflight and synthetic analysis checks passed; two independent model jobs accepted but queued for L4 availability at last inspection. **No MPW-102B validation outcomes were observed** at this status snapshot.

## Frozen source and protocol
- Protocol: [MPW-102B protocol](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f56a74626df150c382c565c268c403762ca487d6/mpw102b/PROTOCOL.md)
- Freeze: [FREEZE.md](https://github.com/TheUltimateHuman/when-explanations-write-back/blob/f56a74626df150c382c565c268c403762ca487d6/mpw102b/FREEZE.md)
- Executed runner commit: f56a74626df150c382c565c268c403762ca487d6
- Executed source SHA-256: 13ee183820c3e870a7566c3727593386ab375eff1790687186bd47439ad02eb8
- Frozen case manifest: 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce
- 32 calibration + 192 new validation families; fresh text set excludes reconstructed PR-002, MPW-101, and MPW-102 texts.
- Two prespecified model candidates: Qwen3-4B-Instruct-2507 and Granite-3.3-8B-Instruct.
- Seven treatment families include first-person, second-person declarative, third-person, second-person question, second-person prescriptive, imperative and side-reference control.
- Both primary gates (AB transport and explanation-vs-neutral specificity) were defined separately before validation; Bonferroni familywise threshold .0125 per model-level test.

## CPU preflight and synthetic analysis
- [Sample/token preflight](https://huggingface.co/jobs/TheUltimateHuman/6adb58bd046eb82b1ecd45be): completed, both model tokenizers A/B and positive/negative atomic.
- [AST and byte-hash audit](https://huggingface.co/jobs/TheUltimateHuman/6adb59511e112550ce7d4eb7): completed. Syntax PASS; runner SHA matched freeze.
- [Synthetic comparison of model runner and independent analysis](https://huggingface.co/jobs/TheUltimateHuman/6adb5a4a1e112550ce7d4f30): PASS, 192 synthetic families, matching effect means, confidence intervals and verdicts; these are unit tests, NOT scientific results.

## GPU jobs accepted by Hugging Face Jobs
- Qwen3 job: [6adb597a1e112550ce7d4ecb](https://huggingface.co/jobs/TheUltimateHuman/6adb597a1e112550ce7d4ecb).
- Granite job: [6adb59f41e112550ce7d4f20](https://huggingface.co/jobs/TheUltimateHuman/6adb59f41e112550ce7d4f20).
- Both used exact frozen runner SHA as URL source, different --model arguments, L4 x1, hard 75 minute provider timeout and a 65 minute in-process cap.
- **State at last check: SCHEDULING / Waiting for requested hardware.** Acceptance is not evidence that inference has begun or succeeded. Only calibration eligibility allows a validation phase; both may fail or time out.
- The resulting logs, if generated, must be recovered with their exact shard digests. The frozen verdict must stand even if null or negative.

## Next recovery instructions
Inspect each job status and collect exact logs. A valid completion requires MPW102B_VALIDATION_START, 192 families, 4 complete SHA-anchored shards, and MPW102B_END with matching hashes and model revision. Preserve ALL outcomes and errors. If a job fails calibration, record INELIGIBLE without testing its validation. An independent CPU analysis must reproduce the primary before publication. Do not launch retries to seek a favorable result. No full cross-architecture or explanatory-specificity success claim may be made from job scheduling alone.
