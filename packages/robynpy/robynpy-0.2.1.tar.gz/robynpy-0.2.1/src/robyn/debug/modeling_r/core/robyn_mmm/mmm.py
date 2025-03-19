from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from ...utils.lambda_calc import lambda_seq
from ...transformations.run_transformations import run_transformations
from ...core.model_decomp import model_decomp
from ...core.model_refit import model_refit
from ...core.lift_calibration import lift_calibration
from .spend_share import calculate_spend_share
from .lambda_setup import setup_lambda
from .nevergrad_setup import setup_nevergrad, NevergradSetup
from .iterations import run_iteration
from .decomp_rssd import calculate_decomp_rssd

@dataclass
class ParallelResult:
    """Container for parallel processing results"""
    nrmse: float
    decomp_rssd: float
    mape: Optional[float] = None
    full_result: Dict[str, Any] = None

def robyn_mmm(
    input_collect: Dict[str, Any],
    hyper_collect: Dict[str, Any],
    iterations: int = 2000,
    cores: int = 1,
    nevergrad_algo: str = "TwoPointsDE",
    intercept: bool = True,
    intercept_sign: Optional[str] = None,
    ts_validation: bool = True,
    add_penalty_factor: bool = False,
    objective_weights: Optional[Dict[str, float]] = None,
    dt_hyper_fixed: Optional[pd.DataFrame] = None,
    rssd_zero_penalty: bool = True,
    refresh: bool = False,
    trial: int = 1,
    seed: int = 123,
    quiet: bool = False
) -> Dict[str, Any]:
    """
    Core MMM Function that activates Nevergrad to generate samples of hyperparameters,
    conducts media transformation within each loop, fits the Ridge regression,
    optionally calibrates the model, decomposes responses and collects the result.
    """
    # Start timing
    t0 = time.time()

    # Check if nevergrad is available when needed
    if iterations > 1:
        try:
            import nevergrad as ng
            if isinstance(seed, int):
                np.random.seed(seed)
        except ImportError:
            raise ImportError(
                "You must have nevergrad python library installed.\n"
                "Please install it using: pip install nevergrad"
            )

    # Setup environment and collect parameters
    if input_collect.get('dt_mod') is None:
        raise ValueError("Run robyn_engineering() first to get the dt_mod")

    # Calculate spend share
    dt_spend_share = calculate_spend_share(
        input_collect=input_collect,
        rolling_window_start_which=input_collect['rollingWindowStartWhich'],
        rolling_window_end_which=input_collect['rollingWindowEndWhich'],
        paid_media_spends=input_collect['paid_media_spends'],
        paid_media_selected=input_collect['paid_media_selected'],
        exposure_vars=input_collect.get('exposure_vars', []),
        organic_vars=input_collect.get('organic_vars', []),
        refresh_added_start=input_collect['refreshAddedStart'],
        dt_mod_roll_wind=input_collect['dt_modRollWind'],
        rolling_window_length=input_collect['rollingWindowLength']
    )

    # Setup lambda parameters
    lambda_max, lambda_min, lambdas = setup_lambda(
        dt_mod=input_collect['dt_mod'],
        lambda_min_ratio=0.0001  # default value from glmnet
    )

    # Setup Nevergrad optimization
    ng_setup = setup_nevergrad(
        hyper_fixed=hyper_collect['all_fixed'],
        iterations=iterations,
        cores=cores,
        optimizer_name=nevergrad_algo,
        hyper_count=len(hyper_collect['hyper_bound_list_updated']),
        calibration_input=input_collect.get('calibration_input'),
        objective_weights=tuple(objective_weights.values()) if objective_weights else None,
        quiet=quiet
    )

    def run_parallel_batch(batch_num: int) -> List[ParallelResult]:
        """Run a batch of iterations in parallel"""
        batch_results = []
        
        for _ in range(ng_setup.iter_par):
            try:
                # Get hyperparameter sample from nevergrad
                if not hyper_collect['all_fixed']:
                    hyp_param_sam = ng_setup.optimizer.ask()
                    hyp_param_values = hyp_param_sam.value
                    
                    # Scale sample to given bounds using uniform distribution
                    hyp_param_dict = {}
                    for name in hyper_collect['hyper_bound_list_updated'].keys():
                        bounds = hyper_collect['hyper_bound_list_updated'][name]
                        idx = list(hyper_collect['hyper_bound_list_updated'].keys()).index(name)
                        value = float(hyp_param_values[idx])
                        
                        if isinstance(bounds, (list, tuple)):
                            value = np.quantile([bounds[0], bounds[1]], value)
                        hyp_param_dict[name] = value
                        
                    # Add fixed hyperparameters
                    if hyper_collect['hyper_bound_list_fixed']:
                        hyp_param_dict.update(hyper_collect['dt_hyper_fixed_mod'])
                else:
                    hyp_param_dict = hyper_collect['dt_hyper_fixed_mod']
                
                hyp_param_sam = pd.Series(hyp_param_dict)
                
                # Run iteration
                result = run_iteration(
                    i=batch_num,
                    hyp_param_sam=hyp_param_sam,
                    input_collect=input_collect,
                    rolling_window_start_which=input_collect['rollingWindowStartWhich'],
                    rolling_window_end_which=input_collect['rollingWindowEndWhich'],
                    dt_mod=input_collect['dt_mod'],
                    adstock=input_collect['adstock'],
                    lambda_max=lambda_max,
                    lambda_min_ratio=lambda_min_ratio,
                    intercept=intercept,
                    ts_validation=ts_validation,
                    trial=trial,
                    rssd_zero_penalty=rssd_zero_penalty,
                    refresh=refresh,
                    x_decomp_agg_prev=input_collect.get('xDecompAggPrev')
                )
                
                # Collect results
                parallel_result = ParallelResult(
                    nrmse=result['common']['nrmse'],
                    decomp_rssd=result['common']['decomp_rssd'],
                    mape=result['common'].get('mape'),
                    full_result=result
                )
                
                batch_results.append(parallel_result)
                
                # Update nevergrad with results
                if not hyper_collect['all_fixed']:
                    if input_collect.get('calibration_input') is None:
                        ng_setup.optimizer.tell(
                            hyp_param_sam,
                            (parallel_result.nrmse, parallel_result.decomp_rssd)
                        )
                    else:
                        ng_setup.optimizer.tell(
                            hyp_param_sam,
                            (parallel_result.nrmse, parallel_result.decomp_rssd, parallel_result.mape)
                        )
                
                # Update progress bar
                if not quiet and not hyper_collect['all_fixed']:
                    ng_setup.pbar.update(1)
                    
            except Exception as e:
                print(f"Error in iteration {batch_num}: {str(e)}")
                continue
                
        return batch_results

    # Run optimization loop with error handling
    try:
        result_collect_ng = []
        
        if cores > 1 and not hyper_collect['all_fixed']:
            with ProcessPoolExecutor(max_workers=cores) as executor:
                for batch_results in executor.map(run_parallel_batch, range(ng_setup.iter_ng)):
                    result_collect_ng.extend(batch_results)
        else:
            for i in range(ng_setup.iter_ng):
                batch_results = run_parallel_batch(i)
                result_collect_ng.extend(batch_results)
                
    except Exception as e:
        if len(result_collect_ng) > 1:
            print(f"Error while running robyn_mmm(); providing PARTIAL results\n{str(e)}")
        else:
            raise e

    # Close progress bar
    if not quiet and not hyper_collect['all_fixed']:
        ng_setup.pbar.close()

    # Process final results
    result_collect = {
        'resultHypParam': pd.DataFrame([r.full_result['hyper_params'] for r in result_collect_ng]),
        'xDecompAgg': pd.concat([r.full_result['decomp_result']['x_decomp_agg'] for r in result_collect_ng]),
        'iter': len(result_collect_ng),
        'elapsed.min': (time.time() - t0) / 60
    }

    # Add calibration results if available
    if input_collect.get('calibration_input') is not None:
        result_collect['liftCalibration'] = pd.concat([
            r.full_result['lift_result'] for r in result_collect_ng if r.full_result['lift_result'] is not None
        ])

    # Adjust accumulated time
    result_collect['resultHypParam']['ElapsedAccum'] = (
        result_collect['resultHypParam']['ElapsedAccum'] - 
        result_collect['resultHypParam']['ElapsedAccum'].min() +
        result_collect['resultHypParam']['Elapsed'].iloc[
            result_collect['resultHypParam']['ElapsedAccum'].idxmin()
        ]
    )

    return {
        'resultCollect': result_collect,
        'hyperBoundNG': hyper_collect['hyper_bound_list_updated'],
        'hyperBoundFixed': hyper_collect['hyper_bound_list_fixed']
    } 