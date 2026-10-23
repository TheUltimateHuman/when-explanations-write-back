# /// script
# requires-python = ">=3.10"
# ///
"""Regression tests for the two known arbitrary runtime gate regressions."""
import importlib.util,urllib.request,tempfile
from pathlib import Path

URL='https://raw.githubusercontent.com/TheUltimateHuman/when-explanations-write-back/mpw-runtime-recovery-20261023/mpw-runtime-recovery/scripts/runtime_policy.py'
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'runtime_policy.py';p.write_bytes(urllib.request.urlopen(URL,timeout=45).read())
 spec=importlib.util.spec_from_file_location('runtime_policy',p)
 policy=importlib.util.module_from_spec(spec)
 import sys
 sys.modules[spec.name]=policy
 spec.loader.exec_module(policy)
 # Both ORIGINAL experiments had adequate 75m provider windows, even after 35% padding.
 for study,start,sec,n in [('MPW102B_Granite',189.507178887,14.7370174625,192),
                            ('MPW103_Qwen',191.766950853,22.700217106,128)]:
  v=policy.assess(startup_seconds=start,seconds_per_family=sec,n_families=n,
      provider_timeout_seconds=4500,hourly_usd=.8)
  assert v.outcome=='PROCEED_WITHIN_PROVIDER_WINDOW',(study,v)
  assert v.padded_seconds<4500
  print(study+': PASS - no arbitrary gate')
 # An actually impossible hardware window must request replanning, not simulate null evidence.
 v=policy.assess(startup_seconds=500,seconds_per_family=30,n_families=160,
       provider_timeout_seconds=4200,hourly_usd=.8)
 assert v.outcome=='PHYSICAL_RUNTIME_REPLAN'
 # Explicit user budget must be enforced separately from hypothesis validity.
 v=policy.assess(startup_seconds=200,seconds_per_family=15,n_families=160,
       provider_timeout_seconds=6000,hourly_usd=.8,approved_total_budget_usd=.50)
 assert v.outcome=='USER_BUDGET_APPROVAL_REQUIRED'
 # Padded-risk warning must NOT become an invented no-validation gate.
 v=policy.assess(startup_seconds=200,seconds_per_family=17,n_families=128,
       provider_timeout_seconds=3000,hourly_usd=.8)
 assert v.outcome=='PROCEED_WITH_OVERRUN_WARNING'
 print('ALL_FOUR_MPWRUNTIME_POLICY_TESTS_PASSED')
