import pandas as pd
import numpy as np
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class DecompositionInputs:
    """Input data structure for model decomposition"""
    coefs: np.ndarray
    y_pred: np.ndarray
    dt_mod_saturated: pd.DataFrame
    dt_saturated_immediate: pd.DataFrame
    dt_saturated_carryover: pd.DataFrame
    dt_mod_roll_wind: pd.DataFrame
    refresh_added_start: str

def model_decomp(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decompose model results into various components
    
    Args:
        inputs: Dictionary containing model outputs and data
    
    Returns:
        Dictionary containing decomposition results
    """
    # Unpack inputs
    coefs = inputs['coefs']
    y_pred = inputs['y_pred']
    dt_mod_saturated = inputs['dt_mod_saturated']
    dt_saturated_immediate = inputs['dt_saturated_immediate']
    dt_saturated_carryover = inputs['dt_saturated_carryover']
    dt_mod_roll_wind = inputs['dt_mod_roll_wind']
    refresh_added_start = inputs['refresh_added_start']

    # Input for decomp
    y = dt_mod_saturated['dep_var']
    x = dt_mod_saturated.drop('dep_var', axis=1)
    intercept = coefs[0]
    x_name = x.columns
    x_factor = x.select_dtypes(include=['category', 'object']).columns

    # Decomp x
    x_decomp = pd.DataFrame()
    for col, coef in zip(x.columns, coefs[1:]):
        x_decomp[col] = x[col] * coef
    x_decomp.insert(0, 'intercept', intercept)
    
    x_decomp_out = pd.concat([
        pd.DataFrame({
            'ds': dt_mod_roll_wind['ds'],
            'y': y,
            'y_pred': y_pred
        }),
        x_decomp
    ], axis=1)

    # Decomp immediate & carryover response
    sel_coef = [name in dt_saturated_immediate.columns for name in coefs.index]
    coefs_media = coefs[sel_coef]
    
    media_decomp_immediate = pd.DataFrame()
    for col, coef in zip(dt_saturated_immediate.columns, coefs_media):
        media_decomp_immediate[col] = dt_saturated_immediate[col] * coef

    media_decomp_carryover = pd.DataFrame()
    for col, coef in zip(dt_saturated_carryover.columns, coefs_media):
        media_decomp_carryover[col] = dt_saturated_carryover[col] * coef

    # Output decomp
    y_hat = x_decomp.sum(axis=1)
    y_hat_scaled = x_decomp.abs().sum(axis=1)
    x_decomp_out_perc_scaled = x_decomp.abs().div(y_hat_scaled, axis=0)
    x_decomp_out_scaled = y_hat * x_decomp_out_perc_scaled

    # Calculate aggregates
    temp = x_decomp_out[['intercept'] + list(x_name)]
    x_decomp_out_agg = temp.sum()
    x_decomp_out_agg_perc = x_decomp_out_agg / y_hat.sum()
    
    x_decomp_out_agg_mean_non0 = temp.apply(lambda x: x[x != 0].mean() if len(x[x != 0]) > 0 else 0)
    x_decomp_out_agg_mean_non0_perc = x_decomp_out_agg_mean_non0 / x_decomp_out_agg_mean_non0.sum()

    # Calculate refresh period aggregates
    refresh_added_start_idx = x_decomp_out[x_decomp_out['ds'] == refresh_added_start].index[0]
    refresh_added_end_idx = x_decomp_out['ds'].last_valid_index()
    
    temp_rf = temp.iloc[refresh_added_start_idx:refresh_added_end_idx + 1]
    x_decomp_out_agg_rf = temp_rf.sum()
    y_hat_rf = y_hat[refresh_added_start_idx:refresh_added_end_idx + 1]
    x_decomp_out_agg_perc_rf = x_decomp_out_agg_rf / y_hat_rf.sum()
    
    x_decomp_out_agg_mean_non0_rf = temp_rf.apply(lambda x: x[x != 0].mean() if len(x[x != 0]) > 0 else 0)
    x_decomp_out_agg_mean_non0_perc_rf = x_decomp_out_agg_mean_non0_rf / x_decomp_out_agg_mean_non0_rf.sum()

    # Prepare coefficients output
    coefs_out_cat = coefs_out = pd.DataFrame({
        'rn': coefs.index,
        'coef': coefs.values
    })
    
    if len(x_factor) > 0:
        for factor in x_factor:
            coefs_out['rn'] = coefs_out['rn'].str.replace(f"{factor}.*", factor, regex=True)
    
    rn_order = list(x_decomp_out_agg.index)
    rn_order[rn_order.index('intercept')] = '(Intercept)'
    
    coefs_out = (coefs_out.groupby('rn')['coef']
                 .mean()
                 .reset_index()
                 .set_index('rn')
                 .reindex(rn_order)
                 .reset_index())

    # Final aggregated output
    decomp_out_agg = pd.concat([
        coefs_out,
        pd.DataFrame({
            'xDecompAgg': x_decomp_out_agg,
            'xDecompPerc': x_decomp_out_agg_perc,
            'xDecompMeanNon0': x_decomp_out_agg_mean_non0,
            'xDecompMeanNon0Perc': x_decomp_out_agg_mean_non0_perc,
            'xDecompAggRF': x_decomp_out_agg_rf,
            'xDecompPercRF': x_decomp_out_agg_perc_rf,
            'xDecompMeanNon0RF': x_decomp_out_agg_mean_non0_rf,
            'xDecompMeanNon0PercRF': x_decomp_out_agg_mean_non0_perc_rf,
            'pos': x_decomp_out_agg >= 0
        })
    ], axis=1)

    return {
        'xDecompVec': x_decomp_out,
        'xDecompVec_scaled': x_decomp_out_scaled,
        'xDecompAgg': decomp_out_agg,
        'coefsOutCat': coefs_out_cat,
        'mediaDecompImmediate': media_decomp_immediate.assign(
            ds=x_decomp_out['ds'],
            y=x_decomp_out['y']
        ),
        'mediaDecompCarryover': media_decomp_carryover.assign(
            ds=x_decomp_out['ds'],
            y=x_decomp_out['y']
        )
    }
