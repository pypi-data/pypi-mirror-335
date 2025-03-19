# robyn/debug/modeling_rewrite/code/utils/hyper_utils.py
from typing import List, Optional, Any
import itertools
import pandas as pd
from robyn.debug.modeling_rewrite.code.constants import AdstockOptions, HYPS_NAMES, HYPS_OTHERS

def check_adstock(adstock: str) -> str:
    """Validate adstock type"""
    try:
        return AdstockOptions(adstock).value
    except ValueError:
        raise ValueError(f"Invalid adstock type: {adstock}. Must be one of {[e.value for e in AdstockOptions]}")

def get_hyper_names(adstock: str, all_media: List[str], all_vars: Optional[List[str]] = None) -> List[str]:
    """Generate hyperparameter names based on adstock type and media"""
    adstock = check_adstock(adstock)
    
    if adstock == AdstockOptions.GEOMETRIC.value:
        relevant_hyps = [h for h in HYPS_NAMES if h in ["thetas", "alphas", "gammas"]]
    else:  # weibull types
        relevant_hyps = [h for h in HYPS_NAMES if h in ["shapes", "scales", "alphas", "gammas"]]
    
    # Create combinations of media and hyperparameter types
    local_names = sorted([f"{media}_{hyp}" for media, hyp in itertools.product(all_media, relevant_hyps)])
    
    # Add penalty variables if all_vars provided
    if all_vars:
        penalty_names = [f"{var}_penalty" for var in all_vars]
        local_names = sorted(local_names + penalty_names)
        
    return local_names

def check_hyper_fixed(
    input_collect: Any,  # Replace with proper type
    dt_hyper_fixed: Optional[pd.DataFrame],
    add_penalty_factor: bool
) -> tuple[bool, List[str]]:
    """Check if hyperparameters are fixed and return hyperparameter names"""
    
    hyper_fixed = dt_hyper_fixed is not None
    
    # Get base hyperparameter names
    hyp_param_names = get_hyper_names(
        adstock=input_collect.adstock,
        all_media=input_collect.all_media
    )
    
    # Add standard hyperparameters
    hyp_param_names.extend(HYPS_OTHERS)
    
    # Add penalty factor names if needed
    if add_penalty_factor:
        cols = [col for col in input_collect.dt_mod.columns if col not in ['ds', 'dep_var']]
        penalty_names = [f"{col}_penalty" for col in cols]
        hyp_param_names.extend(penalty_names)

    # Validate dt_hyper_fixed if provided
    if hyper_fixed:
        if len(dt_hyper_fixed) != 1:
            raise ValueError("Provide only 1 model / 1 row from previous runs")
            
        missing_params = [p for p in hyp_param_names if p not in dt_hyper_fixed.columns]
        if missing_params:
            raise ValueError(f"Invalid dt_hyper_fixed. Missing values for: {missing_params}")
    
    return hyper_fixed, hyp_param_names