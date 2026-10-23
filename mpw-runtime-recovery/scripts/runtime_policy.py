#!/usr/bin/env python3
"""MPW research runtime planning: forecast execution without invented vetoes.

Pure stdlib, no network. Provider timeout is operational; family sensitivity,
sample integrity and inferential gates must be evaluated elsewhere. Warn when
an *uncertain padded* runtime overruns a provider window; only block when
the unpadded run doesn't fit or known user-approved budget is exceeded.

Examples:
 python runtime_policy.py --startup-sec 189.5072 --sec-per-family 14.73701746 --families 192 --provider-minutes 75 --hourly-usd 0.80
 python runtime_policy.py --startup-sec 191.76695 --sec-per-family 22.7002171 --families 128 --provider-minutes 75 --hourly-usd 0.80
"""
import argparse,json,math
from dataclasses import dataclass,asdict

@dataclass(frozen=True)
class RuntimeAssessment:
    outcome:str
    unpadded_seconds:float
    padded_seconds:float
    provider_timeout_seconds:float
    writeout_reserve_seconds:float
    provider_rate_usd_per_hour:float
    estimated_bill_if_unpadded_usd:float
    worst_case_provider_bill_usd:float
    approved_total_budget_usd:float|None
    warnings:tuple[str,...]

def assess(*,startup_seconds:float,seconds_per_family:float,n_families:int,
           provider_timeout_seconds:float,hourly_usd:float,
           writeout_reserve_seconds:float=120,padding_factor:float=1.35,
           approved_total_budget_usd:float|None=None)->RuntimeAssessment:
    numeric=(startup_seconds,seconds_per_family,provider_timeout_seconds,
             hourly_usd,writeout_reserve_seconds,padding_factor)
    if any(not math.isfinite(x) for x in numeric):
        raise ValueError("NONFINITE_RUNTIME_ARGUMENT")
    if min(startup_seconds,seconds_per_family,hourly_usd,writeout_reserve_seconds)<0:
        raise ValueError("NEGATIVE_RUNTIME_ARGUMENT")
    if n_families<1 or provider_timeout_seconds<=writeout_reserve_seconds:
        raise ValueError("INVALID_PROVIDER_WINDOW")
    if padding_factor<1:
        raise ValueError("PADDING_IS_A_SURCHARGE_FACTOR_GE_1")
    if approved_total_budget_usd is not None and (not math.isfinite(approved_total_budget_usd)
                                                   or approved_total_budget_usd<0):
        raise ValueError("INVALID_APPROVED_BUDGET")
    unpadded=startup_seconds+seconds_per_family*n_families
    padded=startup_seconds+padding_factor*seconds_per_family*n_families
    worst=hourly_usd*provider_timeout_seconds/3600
    expected=hourly_usd*unpadded/3600
    usable=provider_timeout_seconds-writeout_reserve_seconds
    warnings=[]
    # Provider maximum spend must be checked against approval; not silently invented.
    if approved_total_budget_usd is not None and worst>approved_total_budget_usd:
        status="USER_BUDGET_APPROVAL_REQUIRED"
        warnings.append("Provider maximum cost exceeds explicitly approved budget. "
                        "Seek approval or choose a cheaper configuration before validation.")
    elif unpadded>usable:
        status="PHYSICAL_RUNTIME_REPLAN"
        warnings.append("Unpadded empirical expectation does not fit provider timeout "
                        "after actual reserved archival window. Choose faster hardware "
                        "or increase provider window prior to validation.")
    elif padded>usable:
        status="PROCEED_WITH_OVERRUN_WARNING"
        warnings.append("Conservative padded forecast exceeds provider window but "
                        "unpadded forecast fits. Warn and offer larger provider window "
                        "or faster hardware; NEVER impose an extra assistant-created "
                        "scientific validity gate.")
    else:
        status="PROCEED_WITHIN_PROVIDER_WINDOW"
    return RuntimeAssessment(status,unpadded,padded,provider_timeout_seconds,
             writeout_reserve_seconds,hourly_usd,expected,worst,
             approved_total_budget_usd,tuple(warnings))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--startup-sec",required=True,type=float)
    p.add_argument("--sec-per-family",required=True,type=float)
    p.add_argument("--families",required=True,type=int)
    p.add_argument("--provider-minutes",required=True,type=float)
    p.add_argument("--hourly-usd",required=True,type=float)
    p.add_argument("--writeout-reserve-sec",default=120,type=float)
    p.add_argument("--padding-factor",default=1.35,type=float)
    p.add_argument("--approved-total-budget-usd",default=None,type=float)
    args=p.parse_args()
    out=assess(startup_seconds=args.startup_sec,seconds_per_family=args.sec_per_family,
       n_families=args.families,provider_timeout_seconds=args.provider_minutes*60,
       hourly_usd=args.hourly_usd,
       writeout_reserve_seconds=args.writeout_reserve_sec,
       padding_factor=args.padding_factor,
       approved_total_budget_usd=args.approved_total_budget_usd)
    print(json.dumps(asdict(out),indent=2,sort_keys=True))
if __name__=="__main__":main()
