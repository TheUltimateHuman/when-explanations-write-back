# MPW-103I — Execution Compliance Note

**Recorded before receiving any MPW-103I iterative treatment outcomes.**  
**Category:** RESEARCH ARTIFACT / transparent pre-result source-versus-protocol audit.

The October 25 prospective protocol and freeze describe a four-family complete-iteration throughput pilot, but the exact frozen native-iteration runner at commit f0a12228e223a0a41948935dc3b1ef75f73574c4 uses **two** calibration families in its runtime pilot:

`for f in cal[:2]: run_family(...)`

and projects elapsed time with that two-case throughput. This is an *operational feasibility-method discrepancy*, not a modification of 64 study families, report generation or prompts, local controls, H1/H2/H3 estimands, bootstrap seeds, model source, case sample or validation integrity gates.

The runner was already frozen and the first Qwen GPU job was submitted before this discrepancy was noticed. **Do not represent it as a four-case pilot.** Preserve the actual measured two-case projection, the provider cap and whether the entire 64-family dataset completed. If a resource refusal occurs, it is a resource limitation and does not constitute a hypothesis negative.

Original exact source and job are unchanged; this note neither authorizes a new GPU attempt after seeing science results nor retroactively edits a frozen protocol. The note must be included in final report and provenance manifest. If the two-case estimate proves unreliable, document and prospectively amend future runs, not results of this job.
