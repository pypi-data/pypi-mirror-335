from typing import Dict, Any, Optional, Union, List
import pandas as pd
from robyn.debug.modeling_r.core.robyn_train.checks import check_init_msg

def robyn_train(
    input_collect: Dict[str, Any],
    hyper_collect: Dict[str, Any],
    cores: int = 1,
    iterations: int = 2000,
    trials: int = 5,
    intercept_sign: Optional[str] = None,
    intercept: bool = True,
    nevergrad_algo: str = "TwoPointsDE",
    dt_hyper_fixed: Optional[pd.DataFrame] = None,
    ts_validation: bool = True,
    add_penalty_factor: bool = False,
    rssd_zero_penalty: bool = True,
    objective_weights: Optional[Dict[str, float]] = None,
    refresh: bool = False,
    seed: int = 123,
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Train Robyn Models.
    
    Consumes output from robyn_input() and runs the robyn_mmm() on each trial.
    
    Args:
        input_collect: Dictionary containing input data and parameters
        hyper_collect: Dictionary containing hyperparameter bounds
        cores: Number of CPU cores to use
        iterations: Number of iterations for optimization
        trials: Number of trials
        intercept_sign: Sign constraint for intercept
        intercept: Whether to include intercept term
        nevergrad_algo: Optimization algorithm to use
        dt_hyper_fixed: Fixed hyperparameters dataframe
        ts_validation: Whether to use time series validation
        add_penalty_factor: Whether to add penalty factor
        rssd_zero_penalty: Whether to apply zero penalty to RSSD
        objective_weights: Weights for different objectives
        refresh: Whether to refresh results
        seed: Random seed
        quiet: Whether to suppress output
    
    Returns:
        Dictionary containing trained models for each trial
    """
    hyper_fixed = hyper_collect.get('all_fixed', False)
    output_models = {}

    if hyper_fixed:
        # Single trial with fixed hyperparameters
        model_output = robyn_mmm(
            input_collect=input_collect,
            hyper_collect=hyper_collect,
            iterations=iterations,
            cores=cores,
            nevergrad_algo=nevergrad_algo,
            intercept=intercept,
            intercept_sign=intercept_sign,
            dt_hyper_fixed=dt_hyper_fixed,
            ts_validation=ts_validation,
            add_penalty_factor=add_penalty_factor,
            rssd_zero_penalty=rssd_zero_penalty,
            objective_weights=objective_weights,
            seed=seed,
            quiet=quiet
        )
        model_output['trial'] = 1
        
        # Set original solID if provided
        if dt_hyper_fixed is not None and 'solID' in dt_hyper_fixed:
            for tab in ['resultHypParam', 'xDecompVec', 'xDecompAgg']:
                if tab in model_output['resultCollect']:
                    model_output['resultCollect'][tab]['solID'] = dt_hyper_fixed['solID']
        
        output_models['trial1'] = model_output
    
    else:
        # Multiple trials with varying hyperparameters
        check_init_msg(input_collect, cores)  # We'll need to implement this utility function
        
        if not quiet:
            calibration_msg = "using" if input_collect.get('calibration_input') is None else "with calibration using"
            print(f">>> Starting {trials} trials with {iterations} iterations each {calibration_msg} {nevergrad_algo} nevergrad algorithm...")

        for trial_num in range(1, trials + 1):
            if not quiet:
                print(f"  Running trial {trial_num} of {trials}")
                
            model_output = robyn_mmm(
                input_collect=input_collect,
                hyper_collect=hyper_collect,
                iterations=iterations,
                cores=cores,
                nevergrad_algo=nevergrad_algo,
                intercept=intercept,
                intercept_sign=intercept_sign,
                ts_validation=ts_validation,
                add_penalty_factor=add_penalty_factor,
                rssd_zero_penalty=rssd_zero_penalty,
                objective_weights=objective_weights,
                refresh=refresh,
                trial=trial_num,
                seed=seed + trial_num,
                quiet=quiet
            )

            # Check for zero coefficients
            if any(model_output['resultCollect']['resultHypParam'].get('decomp.rssd', []) == float('inf')):
                num_coef0_mod = len([x for x in model_output['resultCollect']['resultHypParam'].get('decomp.rssd', [])
                                   if x == float('inf')])
                num_coef0_mod = min(num_coef0_mod, iterations)
                
                if not quiet:
                    print(f"""This trial contains {num_coef0_mod} iterations with all media coefficient = 0.
                    Please reconsider your media variable choice if the pareto choices are unreasonable.
                    
                    Recommendations:
                    1. Increase hyperparameter ranges for 0-coef channels to give Robyn more freedom
                    2. Split media into sub-channels, and/or aggregate similar channels, and/or introduce other media
                    3. Increase trials to get more samples""")

            model_output['trial'] = trial_num
            output_models[f'trial{trial_num}'] = model_output

    return output_models