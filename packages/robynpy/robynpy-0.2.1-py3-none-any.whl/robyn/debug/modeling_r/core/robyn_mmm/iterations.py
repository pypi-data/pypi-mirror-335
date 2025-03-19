from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
from ...transformations.transformations import run_transformations
from ...utils.checks import check_adstock
from ...core.model_decomp import model_decomp
from ...core.lift_calibration import lift_calibration

def apply_sign_control(
    x_train: np.ndarray,
    paid_media_signs: Dict[str, str],
    context_signs: Dict[str, str],
    prophet_signs: Dict[str, str],
    organic_signs: Dict[str, str],
    feature_names: List[str]
) -> np.ndarray:
    """Apply sign control to features based on business knowledge"""
    sign_constraints = np.ones(x_train.shape[1])
    
    # Combine all sign dictionaries
    all_signs = {
        **paid_media_signs,
        **context_signs,
        **prophet_signs,
        **organic_signs
    }
    
    # Apply signs
    for i, feature in enumerate(feature_names):
        if feature in all_signs:
            if all_signs[feature] == "positive":
                sign_constraints[i] = 1
            elif all_signs[feature] == "negative":
                sign_constraints[i] = -1
            
    return sign_constraints

def run_iteration(
    i: int,
    hyp_param_sam: pd.Series,
    input_collect: Dict[str, Any],
    rolling_window_start_which: int,
    rolling_window_end_which: int,
    dt_mod: pd.DataFrame,
    adstock: str,
    lambda_max: float,
    lambda_min_ratio: float,
    intercept: bool,
    ts_validation: bool,
    trial: int = 1,
    rssd_zero_penalty: bool = True,
    refresh: bool = False,
    x_decomp_agg_prev: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Run a single iteration of the MMM optimization
    
    Args:
        i: Iteration number
        hyp_param_sam: Hyperparameter sample
        input_collect: Input data collection
        rolling_window_start_which: Start of rolling window
        rolling_window_end_which: End of rolling window
        dt_mod: Model data
        adstock: Adstock type
        lambda_max: Maximum lambda value
        lambda_min_ratio: Minimum lambda ratio
        intercept: Whether to include intercept
        ts_validation: Whether to use time series validation
        trial: Trial number
        rssd_zero_penalty: Whether to apply RSSD zero penalty
        refresh: Whether to refresh decomposition
        x_decomp_agg_prev: Previous decomposition aggregation
        
    Returns:
        Dictionary containing iteration results
    """
    # Start timing
    import time
    t1 = time.time()
    t0 = input_collect.get('t0', t1)  # Get global start time if available

    # Transform media for model fitting
    adstock = check_adstock(adstock)
    temp = run_transformations(
        all_media=input_collect['all_media'],
        window_start_loc=rolling_window_start_which,
        window_end_loc=rolling_window_end_which,
        dt_mod=dt_mod,
        adstock=adstock,
        dt_hyppar=hyp_param_sam
    )

    # Split train & test and prepare data for modeling
    dt_window = temp.dt_mod_saturated
    
    # Prepare model inputs
    y_window = dt_window['dep_var'].values
    x_window = dt_window.drop('dep_var', axis=1)
    
    # One-hot encode categorical variables
    from sklearn.preprocessing import OneHotEncoder
    cat_cols = x_window.select_dtypes(include=['category', 'object']).columns
    if len(cat_cols) > 0:
        enc = OneHotEncoder(sparse=False, drop='first')
        x_cat = enc.fit_transform(x_window[cat_cols])
        x_num = x_window.drop(cat_cols, axis=1).values
        x_window = np.hstack([x_num, x_cat])
    else:
        x_window = x_window.values

    # Split data based on train_size
    train_size = hyp_param_sam['train_size']
    if train_size < 1:
        train_size_index = int(np.floor(len(dt_window) * train_size))
        val_size = test_size = (1 - train_size) / 2
        val_size_index = train_size_index + int(np.floor(val_size * len(dt_window)))
        
        x_train = x_window[:train_size_index]
        x_val = x_window[train_size_index:val_size_index]
        x_test = x_window[val_size_index:]
        
        y_train = y_window[:train_size_index]
        y_val = y_window[train_size_index:val_size_index]
        y_test = y_window[val_size_index:]
    else:
        x_train = x_window
        y_train = y_window
        x_val = y_val = x_test = y_test = None

    # Apply sign control
    sign_constraints = apply_sign_control(
        x_train=x_train,
        paid_media_signs=input_collect['paid_media_signs'],
        context_signs=input_collect['context_signs'],
        prophet_signs=input_collect['prophet_signs'],
        organic_signs=input_collect['organic_signs'],
        feature_names=x_window.columns
    )
    
    # Scale lambda and fit model with sign constraints
    lambda_scaled = lambda_max * (lambda_min_ratio ** hyp_param_sam['lambda'])
    lambda_hp = lambda_scaled * x_train.shape[0]
    
    model = Ridge(alpha=lambda_hp, fit_intercept=intercept, positive=(sign_constraints == 1).all())
    model.fit(x_train * sign_constraints, y_train)
    coef = model.coef_ * sign_constraints
    
    # Get predictions and calculate metrics
    y_pred_train = model.predict(x_train)
    rsq_train = r2_score(y_train, y_pred_train)
    nrmse_train = np.sqrt(mean_squared_error(y_train, y_pred_train)) / np.mean(y_train)
    
    # Validation metrics if available
    if x_val is not None:
        y_pred_val = model.predict(x_val)
        rsq_val = r2_score(y_val, y_pred_val)
        nrmse_val = np.sqrt(mean_squared_error(y_val, y_pred_val)) / np.mean(y_val)
    else:
        rsq_val = nrmse_val = None
        
    # Test metrics if available
    if x_test is not None:
        y_pred_test = model.predict(x_test)
        rsq_test = r2_score(y_test, y_pred_test)
        nrmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test)) / np.mean(y_test)
    else:
        rsq_test = nrmse_test = None
        
    # Calculate overall NRMSE
    if ts_validation and nrmse_val is not None:
        nrmse = (nrmse_train + nrmse_val) / 2
    else:
        nrmse = nrmse_train

    # Run model decomposition
    decomp_result = model_decomp(
        x_train=x_train,
        coef=coef,
        intercept=model.intercept_ if intercept else 0,
        dt_mod=dt_mod,
        paid_media_spends=input_collect['paid_media_spends'],
        paid_media_vars=input_collect['paid_media_vars'],
        organic_vars=input_collect['organic_vars'],
        context_vars=input_collect['context_vars'],
        prophet_vars=input_collect['prophet_vars']
    )

    # Calculate lift calibration if provided
    mape = None
    lift_result = None
    if input_collect.get('calibration_input') is not None:
        lift_result = lift_calibration(
            calibration_input=input_collect['calibration_input'],
            df_raw=dt_mod,
            hyp_param_sam=hyp_param_sam,
            wind_start=rolling_window_start_which,
            wind_end=rolling_window_end_which,
            day_interval=input_collect['day_interval'],
            adstock=adstock,
            x_decomp_vec=decomp_result['x_decomp_vec'],
            coefs=decomp_result['coefs_out_cat']
        )
        mape = np.mean(lift_result['mape_lift'])

    # Calculate decomposition RSSD
    decomp_rssd = calculate_decomp_rssd(
        decomp_result=decomp_result,
        dt_spend_share=input_collect['dt_spend_share'],
        paid_media_vars=input_collect['paid_media_vars'],
        organic_vars=input_collect['organic_vars'],
        refresh=refresh,
        x_decomp_agg_prev=x_decomp_agg_prev,
        rssd_zero_penalty=rssd_zero_penalty
    )

    # Collect results
    common = {
        'rsq_train': rsq_train,
        'rsq_val': rsq_val,
        'rsq_test': rsq_test,
        'nrmse_train': nrmse_train,
        'nrmse_val': nrmse_val,
        'nrmse_test': nrmse_test,
        'nrmse': nrmse,
        'decomp_rssd': decomp_rssd,
        'mape': mape,
        'lambda': lambda_scaled,
        'lambda_hp': lambda_hp,
        'lambda_max': lambda_max,
        'lambda_min_ratio': lambda_min_ratio,
        'sol_id': f"{trial}_{i}",
        'trial': trial,
        'iter_par': i,
        'elapsed': time.time() - t1,
        'elapsed_accum': time.time() - t0
    }

    return {
        'model': model,
        'coef': coef,
        'transformations': temp,
        'decomp_result': decomp_result,
        'lift_result': lift_result,
        'common': common,
        'hyper_params': hyp_param_sam.to_dict()
    } 