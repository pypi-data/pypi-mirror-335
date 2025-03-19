from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np

def calculate_decomp_rssd(
    decomp_result: Dict[str, Any],
    dt_spend_share: pd.DataFrame,
    paid_media_vars: List[str],
    organic_vars: List[str],
    refresh: bool = False,
    x_decomp_agg_prev: Optional[pd.DataFrame] = None,
    rssd_zero_penalty: bool = True
) -> float:
    """
    Calculate decomposition RSSD (Root Sum of Squared Distances)
    
    Args:
        decomp_result: Results from model decomposition
        dt_spend_share: Spend share data
        paid_media_vars: List of paid media variables
        organic_vars: List of organic variables
        refresh: Whether in refresh mode
        x_decomp_agg_prev: Previous decomposition results
        rssd_zero_penalty: Whether to apply penalty for zero coefficients
        
    Returns:
        RSSD value
    """
    x_decomp_agg = decomp_result['x_decomp_agg']
    
    # Calculate loss
    dt_loss_calc = (
        x_decomp_agg[x_decomp_agg['rn'].isin(paid_media_vars + organic_vars)]
        .merge(
            dt_spend_share[['rn', 'spend_share', 'spend_share_refresh']],
            on='rn',
            how='left'
        )
    )

    if not refresh:
        # Calculate effect shares for paid media
        paid_media_effects = dt_loss_calc[dt_loss_calc['rn'].isin(paid_media_vars)]
        effect_share = paid_media_effects['x_decomp_perc'] / paid_media_effects['x_decomp_perc'].sum()
        
        # Calculate RSSD
        decomp_rssd = np.sqrt(np.sum((effect_share - paid_media_effects['spend_share'])**2))
        
        # Apply zero penalty if requested
        if rssd_zero_penalty:
            is_zero_effect = np.round(effect_share, 4) == 0
            share_zero_effect = is_zero_effect.sum() / len(effect_share)
            decomp_rssd *= (1 + share_zero_effect)
    else:
        # Calculate RSSD for refresh mode
        dt_decomp_rf = (
            pd.DataFrame({'rn': x_decomp_agg['rn'], 'decomp_perc': x_decomp_agg['x_decomp_perc']})
            .merge(
                pd.DataFrame({'rn': x_decomp_agg_prev['rn'], 'decomp_perc_prev': x_decomp_agg_prev['x_decomp_perc']}),
                on='rn'
            )
        )
        
        # Calculate media and non-media RSSD
        rssd_media = np.sqrt(np.mean(
            (dt_decomp_rf[dt_decomp_rf['rn'].isin(paid_media_vars)]['decomp_perc'] - 
             dt_decomp_rf[dt_decomp_rf['rn'].isin(paid_media_vars)]['decomp_perc_prev'])**2
        ))
        
        rssd_nonmedia = np.sqrt(np.mean(
            (dt_decomp_rf[~dt_decomp_rf['rn'].isin(paid_media_vars)]['decomp_perc'] - 
             dt_decomp_rf[~dt_decomp_rf['rn'].isin(paid_media_vars)]['decomp_perc_prev'])**2
        ))
        
        decomp_rssd = rssd_media + rssd_nonmedia
    
    # Handle case where all media coefficients are zero
    if np.isnan(decomp_rssd):
        decomp_rssd = float('inf')
        x_decomp_agg.loc[x_decomp_agg['rn'].isin(paid_media_vars), 'effect_share'] = 0
        
    return decomp_rssd 