# robyn/debug/modeling_rewrite/core/mmm.py

import nevergrad as ng
import numpy as np
from typing import Optional, Dict, List, Any
import logging
from dataclasses import dataclass
import pandas as pd
import numpy as np
from robyn.debug.modeling_rewrite.data.inputs.mmmdata import MMMData
from robyn.debug.modeling_rewrite.code.hyperparameters.hyper_collector import HyperCollectorOutput

logger = logging.getLogger(__name__)

@dataclass
class MMMEnvironment:
    """Holds all the environment variables needed for MMM"""
    dt_mod: pd.DataFrame
    x_decomp_agg_prev: Optional[pd.DataFrame]
    rolling_window_start_which: int
    rolling_window_end_which: int
    refresh_added_start: str
    dt_mod_roll_wind: pd.DataFrame
    refresh_steps: int
    rolling_window_length: int
    paid_media_spends: List[str]
    paid_media_selected: List[str]
    exposure_vars: List[str]
    organic_vars: List[str]
    context_vars: List[str]
    prophet_vars: List[str]
    adstock: str
    context_signs: List[str]
    paid_media_signs: List[str]
    prophet_signs: List[str]
    organic_signs: List[str]
    calibration_input: Optional[Any]

class RobynMMM:
    def __init__(self):
        """Initialize RobynMMM"""
        pass

    def run(
        self,
        input_collect: MMMData,
        hyper_collect: HyperCollectorOutput,
        iterations: int,
        cores: int,
        nevergrad_algo: str,
        intercept: bool = True,
        intercept_sign: str = "non_negative",
        ts_validation: bool = True,
        add_penalty_factor: bool = False,
        objective_weights: Optional[List[float]] = None,
        dt_hyper_fixed: Optional[Dict] = None,
        rssd_zero_penalty: bool = True,
        refresh: bool = False,
        trial: int = 1,
        seed: int = 123,
        quiet: bool = False,
        **kwargs
    ):
        """Main MMM training function"""
        
        # Initialize nevergrad if needed
        if iterations > 1:
            np.random.seed(seed)
            # Note: We don't need reticulate check since we're already in Python
            
        # Collect hyperparameters
        hyp_param_sam_name = list(hyper_collect.hyper_list_all.keys())
        
        # Get optimization and fixed hyperparameters
        hyper_bound_list_updated = hyper_collect.hyper_bound_list_updated
        hyper_bound_list_updated_name = list(hyper_bound_list_updated.keys())
        hyper_count = len(hyper_bound_list_updated_name)
        
        hyper_bound_list_fixed = hyper_collect.hyper_bound_list_fixed
        hyper_bound_list_fixed_name = list(hyper_bound_list_fixed.keys())
        hyper_count_fixed = len(hyper_bound_list_fixed_name)
        
        dt_hyper_fixed_mod = hyper_collect.dt_hyper_fixed_mod
        hyper_fixed = hyper_collect.all_fixed
        
        # Setup environment
        if input_collect.featurized_mmm_data is None or input_collect.featurized_mmm_data.dt_mod is None:
            raise ValueError("Run featurization first to get dt_mod")
            
        # Initialize environment variables
        env = self._setup_environment(input_collect, nevergrad_algo)

        # Calculate spend shares
        dt_spend_share = self._calculate_spend_shares(
            env=env,
            dt_input=input_collect.data
        )
        # Calculate lambda sequence
        lambda_min_ratio = 0.0001  # default value from glmnet
        x = env.dt_mod.drop(columns=['ds', 'dep_var'])
        y = env.dt_mod['dep_var']
        
        lambdas = lambda_seq(
            x=x.values,  # Convert to numpy array
            y=y.values,
            seq_len=100,
            lambda_min_ratio=lambda_min_ratio
        )
        
        lambda_max = np.max(lambdas) * 0.1
        lambda_min = lambda_max * lambda_min_ratio
        
        # Setup Nevergrad iterations
        start_time = datetime.datetime.now()
        
        if not hyper_fixed:
            iter_total = iterations
            iter_par = cores
            iter_ng = np.ceil(iterations / cores).astype(int)  # Sometimes progress bar may not get to 100%
        else:
            iter_total = iter_par = iter_ng = 1

        # Initialize Nevergrad optimizer
        if not hyper_fixed:
            # Create instrumentation for optimization
            instrumentation = ng.p.Array(
                shape=(hyper_count,),  # Use hyper_count from earlier
                lower=0, 
                upper=1
            )
            
            # Initialize optimizer
            optimizer = ng.optimizers.registry[nevergrad_algo](
                parametrization=instrumentation,
                budget=iter_total,
                num_workers=cores
            )
            
            # Setup multi-objective optimization
            if env.calibration_input is None:
                # Without calibration: 2 objectives (NRMSE, DECOMP.RSSD)
                optimizer.tell(ng.p.MultiobjectiveReference(), (1, 1))
                weights = (
                    objective_weights[:2] if objective_weights 
                    else (1.0, 1.0)
                )
            else:
                # With calibration: 3 objectives (NRMSE, DECOMP.RSSD, MAPE)
                optimizer.tell(ng.p.MultiobjectiveReference(), (1, 1, 1))
                weights = (
                    objective_weights[:3] if objective_weights 
                    else (1.0, 1.0, 1.0)
                )
                
            # Set objective weights
            optimizer.set_objective_weights(weights)
            # Initialize the Nevergrad loop
            nevergrad_loop = NevergradLoop(quiet=quiet)
            results = nevergrad_loop.run_iteration_loop(
                optimizer=optimizer,
                iter_total=iter_total,
                iter_par=iter_par,
                iter_ng=iter_ng,
                hyper_fixed=hyper_fixed,
                cores=cores,
                hyper_collect=hyper_collect,
                dt_spend_share=dt_spend_share,
                lambda_min=lambda_min,
                lambda_max=lambda_max,
                **kwargs
            )
        # More implementation to follow...
        
    def _setup_environment(self, input_collect: MMMData, nevergrad_algo: str) -> MMMEnvironment:
        """Setup the environment variables needed for MMM"""
        return MMMEnvironment(
            dt_mod=input_collect.featurized_mmm_data.dt_mod,
            x_decomp_agg_prev=getattr(input_collect, 'x_decomp_agg_prev', None),
            rolling_window_start_which=input_collect.mmmdata_spec.rolling_window_start_which,
            rolling_window_end_which=input_collect.mmmdata_spec.rolling_window_end_which,
            refresh_added_start=getattr(input_collect.mmmdata_spec, 'refresh_added_start', None),
            dt_mod_roll_wind=input_collect.featurized_mmm_data.dt_modRollWind,
            refresh_steps=getattr(input_collect.mmmdata_spec, 'refresh_steps', None),
            rolling_window_length=input_collect.mmmdata_spec.rolling_window_length,
            paid_media_spends=input_collect.mmmdata_spec.paid_media_spends,
            paid_media_selected=input_collect.mmmdata_spec.paid_media_vars,
            exposure_vars=getattr(input_collect.mmmdata_spec, 'exposure_vars', []),
            organic_vars=input_collect.mmmdata_spec.organic_vars or [],
            context_vars=input_collect.mmmdata_spec.context_vars or [],
            prophet_vars=input_collect.holidays_data.prophet_vars,
            adstock=input_collect.adstock,
            context_signs=input_collect.context_signs,
            paid_media_signs=input_collect.paid_media_signs,
            prophet_signs=input_collect.holidays_data.prophet_signs,
            organic_signs=input_collect.organic_signs,
            calibration_input=input_collect.calibration_input
        )
    

    def _calculate_spend_shares(
        self, 
        env: MMMEnvironment,
        dt_input: pd.DataFrame
    ) -> pd.DataFrame:
        """Calculate spend shares for media variables"""
        
        # Get training data slice
        dt_input_train = dt_input.iloc[
            env.rolling_window_start_which:env.rolling_window_end_which
        ]

        # Calculate initial spend shares
        temp = dt_input_train[env.paid_media_spends]
        dt_spend_share = pd.DataFrame({
            'rn': env.paid_media_selected,
            'total_spend': temp.sum(),
            'mean_spend': temp.mean()
        })
        dt_spend_share['spend_share'] = dt_spend_share['total_spend'] / dt_spend_share['total_spend'].sum()

        # Handle exposure and organic variables
        all_vars = env.exposure_vars + env.organic_vars
        if len(all_vars) > 0:
            temp = dt_input_train[all_vars].mean()
            temp_df = pd.DataFrame({
                'rn': all_vars,
                'mean_exposure': temp
            })
            dt_spend_share = dt_spend_share.merge(temp_df, on='rn', how='outer')
        else:
            dt_spend_share['mean_exposure'] = np.nan

        # Calculate refresh spend shares
        refresh_added_start_which = env.dt_mod_roll_wind[
            env.dt_mod_roll_wind['ds'] == env.refresh_added_start
        ].index[0]
        
        temp = dt_input_train[env.paid_media_spends].iloc[
            refresh_added_start_which:env.rolling_window_length
        ]
        
        dt_spend_share_rf = pd.DataFrame({
            'rn': env.paid_media_selected,
            'total_spend': temp.sum(),
            'mean_spend': temp.mean()
        })
        dt_spend_share_rf['spend_share'] = dt_spend_share_rf['total_spend'] / dt_spend_share_rf['total_spend'].sum()

        # Handle exposure and organic variables for refresh
        if len(all_vars) > 0:
            temp = dt_input_train[all_vars].iloc[
                refresh_added_start_which:env.rolling_window_length
            ].mean()
            temp_df = pd.DataFrame({
                'rn': all_vars,
                'mean_exposure': temp
            })
            dt_spend_share_rf = dt_spend_share_rf.merge(temp_df, on='rn', how='outer')
        else:
            dt_spend_share_rf['mean_exposure'] = np.nan

        # Combine normal and refresh spend shares
        dt_spend_share = dt_spend_share.merge(
            dt_spend_share_rf,
            on='rn',
            how='left',
            suffixes=('', '_refresh')
        )

        return dt_spend_share