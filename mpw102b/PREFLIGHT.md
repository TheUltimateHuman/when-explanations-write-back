# MPW-102B CPU-only prevalidation record (2026-10-23)

No new model was loaded for inference and no validation outcomes were inspected in this stage.

Hugging Face CPU job: https://huggingface.co/jobs/TheUltimateHuman/6adb58bd046eb82b1ecd45be
Source candidate at CPU preflight: 3ed4661575ff015aac46aca5c34c75ecd39109fd
Data source: stanfordnlp/sst2 at 8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb

Parent MPW-102 32+256 sample and MPW-101 sample regenerated from frozen sources and checked against their published SHA-256; 3,272 historical text keys excluded, leaving 896 distinct fresh case passages.

Prevalidation case manifest: 5604b42d0264c5ddf228a649e3847ab392b57116d89aaf3c0b625407583928ce

Model revisions (retrieved before validation):
- Qwen3-4B-Instruct-2507: cdbee75f17c01a7cc42f958dc650907174af0554
- Granite-3.3-8B-Instruct: 51dd4bc2ade4059a6bd87649d68aa11e4fb2529b

Both model tokenizers passed the requirement that positive, negative, A and B be single native tokens.

- Qwen3: A 32, B 33, negative 42224, positive 30487.
- Granite: A 51, B 52, negative 15272, positive 18502.

No model inclusion/exclusion decisions were made using validation outcomes. A model must pass the separately frozen calibration accuracy and sensitivity gate after GPU loading or it is INELIGIBLE and MUST NOT undergo validation.

This file documents the sample/tokenizer test as a research artifact, not as a confirmatory experiment.
