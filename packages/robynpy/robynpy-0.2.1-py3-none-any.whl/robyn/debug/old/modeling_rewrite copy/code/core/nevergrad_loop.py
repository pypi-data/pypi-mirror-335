# robyn/debug/modeling_rewrite/core/nevergrad_loop.py

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import tqdm
import concurrent.futures
from dataclasses import dataclass
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime

@dataclass
class NevergradIteration:
    """Stores results of a single Nevergrad iteration"""
    nrmse: float
    decomp_rssd: float 
    mape: Optional[float]
    hyper_params: Dict[str, Any]
    results: Dict[str, Any]

def robyn_iterations(
    i: int,
    hyper_param_sam_ng: pd.DataFrame,
    input_collect: Dict[str, Any],
    adstock: Dict[str, Any],
    calibration_input: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """Run a single model iteration with given hyperparameters"""
    t1 = datetime.now()
    
    # Get hyperparameter sample for this iteration
    hyper_param_sam = hyper_param_sam_ng.iloc[i]
    
    # Transform media for model fitting
    temp = run_transformations(
        all_media=input_collect['all_media'],
        window_start_loc=input_collect['rolling_window_start'],
        window_end_loc=input_collect['rolling_window_end'],
        dt_mod=input_collect['dt_mod'],
        adstock=adstock,
        dt_hyppar=hyper_param_sam
    )
    
    # Prepare data for modeling
    dt_window = temp['dt_mod_saturated']
    
    # Split features and target
    y_window = dt_window['dep_var'].values
    x_window = prepare_model_matrix(dt_window.drop('dep_var', axis=1))
    
    # Split train/val/test sets
    train_size = hyper_param_sam['train_size']
    val_size = test_size = (1 - train_size) / 2
    
    if train_size < 1:
        n_samples = len(dt_window)
        train_idx = int(n_samples * train_size)
        val_idx = train_idx + int(n_samples * val_size)
        
        x_train = x_window[:train_idx]
        x_val = x_window[train_idx:val_idx]
        x_test = x_window[val_idx:]
        
        y_train = y_window[:train_idx]
        y_val = y_window[train_idx:val_idx]
        y_test = y_window[val_idx:]
    else:
        x_train = x_window
        y_train = y_window
        x_val = y_val = x_test = y_test = None

    # Set up sign controls and bounds
    lower_limits, upper_limits = setup_parameter_bounds(
        dt_window,
        prophet_signs=kwargs['prophet_signs'],
        context_signs=kwargs['context_signs'],
        paid_media_signs=kwargs['paid_media_signs'],
        organic_signs=kwargs['organic_signs']
    )

    # Fit model
    mod_out = model_refit(
        x_train=x_train,
        y_train=y_train,
        x_val=x_val,
        y_val=y_val,
        x_test=x_test,
        y_test=y_test,
        lambda_=hyper_param_sam['lambda'],
        lower_limits=lower_limits,
        upper_limits=upper_limits,
        **kwargs
    )

    # Calculate decomposition
    decomp_collect = model_decomp(
        coefs=mod_out['coefs'],
        y_pred=mod_out['y_pred'],
        dt_mod_saturated=temp['dt_mod_saturated'],
        dt_saturated_immediate=temp['dt_saturated_immediate'],
        dt_saturated_carryover=temp['dt_saturated_carryover']
    )

    # Calculate errors
    nrmse = mod_out['nrmse_val'] if kwargs.get('ts_validation') else mod_out['nrmse_train']
    mape = calculate_mape(calibration_input, decomp_collect) if calibration_input else 0
    decomp_rssd = calculate_decomp_rssd(decomp_collect, kwargs['paid_media_spends'])

    # Collect results
    result = {
        'hyper_params': hyper_param_sam.to_dict(),
        'model_metrics': {
            'rsq_train': mod_out['rsq_train'],
            'rsq_val': mod_out['rsq_val'],
            'rsq_test': mod_out['rsq_test'],
            'nrmse': nrmse,
            'mape': mape,
            'decomp_rssd': decomp_rssd
        },
        'decomposition': decomp_collect,
        'elapsed_time': (datetime.now() - t1).total_seconds()
    }
    
    return result

class NevergradLoop:
    def __init__(self, quiet: bool = False):
        self.quiet = quiet
        self.result_collect = {}
        self.count = 0
        
    def run_iteration_loop(
        self,
        optimizer,
        iter_total: int,
        iter_par: int,
        iter_ng: int,
        hyper_fixed: bool,
        cores: int,
        hyper_collect: Any,
        **kwargs
    ) -> Dict[str, Any]:
        """Run the main Nevergrad optimization loop"""
        
        start_time = datetime.now()
        
        if not hyper_fixed and not self.quiet:
            pbar = tqdm.tqdm(total=iter_total)
            
        try:
            for lng in range(1, iter_ng + 1):
                results = self._run_single_iteration(
                    optimizer=optimizer,
                    iter_par=iter_par,
                    hyper_fixed=hyper_fixed,
                    hyper_collect=hyper_collect,
                    cores=cores,
                    **kwargs
                )
                
                self.result_collect[lng] = results
                
                if not self.quiet and not hyper_fixed:
                    pbar.update(iter_par)
                    
        except Exception as e:
            if len(self.result_collect) > 1:
                logger.warning(f"Error while running MMM; providing PARTIAL results\n{str(e)}")
            else:
                raise e
        finally:
            # Cleanup and status reporting
            if not hyper_fixed:
                if not self.quiet:
                    pbar.close()
                elapsed_mins = (datetime.now() - start_time).total_seconds() / 60
                print(f"\n  Finished in {elapsed_mins:.2f} mins")
                
            # Final result collection
            result_collect = {}
            
            # Collect hyperparameter results
            result_hyp_param = []
            for ng_results in self.result_collect.values():
                for result in ng_results:
                    result_hyp_param.append(result['hyper_params'])
            result_collect["resultHypParam"] = pd.DataFrame(result_hyp_param)
            
            # Collect decomposition aggregates
            decomp_agg = []
            for ng_results in self.result_collect.values():
                for result in ng_results:
                    decomp_agg.append(result['decomposition']['xDecompAgg'])
            result_collect["xDecompAgg"] = pd.concat(decomp_agg, ignore_index=True)
            
            # Collect lift calibration if available
            if kwargs.get('calibration_input') is not None:
                lift_calibration = []
                for ng_results in self.result_collect.values():
                    for result in ng_results:
                        lift_calibration.append(result['decomposition']['liftCalibration'])
                result_collect["liftCalibration"] = pd.concat(
                    lift_calibration, 
                    ignore_index=True
                ).sort_values(['mape', 'liftMedia', 'liftStart'])
            
            # Add iteration count and elapsed time
            result_collect['iter'] = len(result_collect.get('mape', []))
            result_collect['elapsed_min'] = (datetime.now() - start_time).total_seconds() / 60
            
            # Adjust accumulated time in resultHypParam
            if 'resultHypParam' in result_collect:
                df = result_collect['resultHypParam']
                min_elapsed_accum = df['ElapsedAccum'].min()
                min_elapsed_idx = df['ElapsedAccum'].idxmin()
                df['ElapsedAccum'] = (df['ElapsedAccum'] - min_elapsed_accum + 
                                     df.loc[min_elapsed_idx, 'Elapsed'])
                result_collect['resultHypParam'] = df
            
            return {
                'resultCollect': result_collect,
                'hyperBoundNG': hyper_collect.hyper_bound_list_updated,
                'hyperBoundFixed': hyper_collect.hyper_bound_list_fixed
            }

    def _run_single_iteration(
        self, 
        optimizer, 
        iter_par: int, 
        hyper_fixed: bool,
        hyper_collect: Any,
        cores: int,
        **kwargs
    ) -> Dict[str, Any]:
        """Run a single iteration of the optimization"""
        
        # Initialize collection lists
        nevergrad_hp = []
        nevergrad_hp_val = []
        hyper_param_sam_list = []
        
        if not hyper_fixed:
            # Get samples for each core
            for co in range(iter_par):
                # Get hyperparameter sample from nevergrad
                ng_result = optimizer.ask()
                nevergrad_hp.append(ng_result)
                nevergrad_hp_val.append(ng_result.value)
                
                # Scale samples to given bounds
                hyper_param_sam = {}
                for hyp_name in hyper_collect.hyper_bound_list_updated:
                    index = list(hyper_collect.hyper_bound_list_updated.keys()).index(hyp_name)
                    channel_bound = hyper_collect.hyper_bound_list_updated[hyp_name]
                    hyppar_value = float(format(nevergrad_hp_val[-1][index], '.10g'))
                    
                    if isinstance(channel_bound, (list, np.ndarray)) and len(channel_bound) > 1:
                        # Scale using uniform distribution
                        hyper_param_sam[hyp_name] = (
                            min(channel_bound) + 
                            hyppar_value * (max(channel_bound) - min(channel_bound))
                        )
                    else:
                        hyper_param_sam[hyp_name] = hyppar_value
                
                # Store as DataFrame
                hyper_param_sam_list.append(pd.DataFrame([hyper_param_sam]))
            
            # Combine all samples
            hyper_param_sam_ng = pd.concat(hyper_param_sam_list, ignore_index=True)
            
            # Add fixed hyperparameters if any
            if len(hyper_collect.hyper_bound_list_fixed) > 0:
                fixed_params = pd.DataFrame([hyper_collect.hyper_bound_list_fixed])
                hyper_param_sam_ng = pd.concat(
                    [hyper_param_sam_ng, fixed_params], 
                    axis=1
                )
        else:
            # Use fixed hyperparameters
            hyper_param_sam_ng = pd.DataFrame([hyper_collect.hyper_bound_list_fixed])

        # Run model iterations in parallel
        with ProcessPoolExecutor(max_workers=cores) as executor:
            futures = [
                executor.submit(
                    robyn_iterations,
                    i,
                    hyper_param_sam_ng,
                    **kwargs
                )
                for i in range(iter_par)
            ]
            results = [f.result() for f in futures]

        # Update optimizer with results if not using fixed hyperparameters
        if not hyper_fixed:
            for i, (result, ng_hp) in enumerate(zip(results, nevergrad_hp)):
                optimizer.tell(
                    ng_hp,
                    (
                        result['model_metrics']['nrmse'],
                        result['model_metrics']['decomp_rssd'],
                        result['model_metrics']['mape']
                    )
                )

        return results