# MPW-101 pre-validation freeze record

All fields below were fixed before any MPW-101 confirmatory validation audit.

- Preflight job: https://huggingface.co/jobs/TheUltimateHuman/6ad01fb4c66288145224914c
- Preflight status: COMPLETED (2026-10-15 UTC)
- Manifest SHA-256: `9559ac6421cb4c5498009b25831766bbdbd5a3fa563083ce9eecfaadde6dda3f`
- Runtime source SHA-256 (with manifest guard): `2f099745a19aea2241ec2821ac5e4632206ff6068ab93759e2a6ca40cac476d9`
- Source protocol: `protocol/MPW101_FROZEN.md`
- Original planning source preserved separately.
- 32 calibration families, 256 confirmatory validation families; class balanced.
- Exact model and dataset revisions encoded in source.
- Seed 2026101501; family bootstrap seed 520261015.
- Primary F = 1[report_sign x D > 0], natural selected report at original A/B mapping.
- Primary gates: tau>0, two-sided exact McNemar p<0.05, paired-family bootstrap CI lower>0; validation task accuracy >=0.9.
- Secondary predeclared thresholds: 0.02, 0.05, 0.10; no substitution for primary result.
- Budget authorized: $10; main job L4x1 with hard 8-hour timeout ($6.40 ceiling at listed rate), excluding cents spent on CPU preflight.
- Status at freeze: preflight successful; GPU validation NOT STARTED.
- Review status: 6/6 unit tests passing; no OSF registration has been submitted. This public Git history is the prospective timestamped protocol record.
