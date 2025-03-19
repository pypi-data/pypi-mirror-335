from typing import Dict, Any, List
import pandas as pd
import numpy as np

def calculate_spend_share(
    input_collect: Dict[str, Any],
    rolling_window_start_which: int,
    rolling_window_end_which: int,
    paid_media_spends: List[str],
    paid_media_selected: List[str],
    exposure_vars: List[str],
    organic_vars: List[str],
    refresh_added_start: str,
    dt_mod_roll_wind: pd.DataFrame,
    rolling_window_length: int
) -> pd.DataFrame:
    """
    Calculate spend share metrics for media variables
    
    Args:
        input_collect: Dictionary containing input data
        rolling_window_start_which: Start index of rolling window
        rolling_window_end_which: End index of rolling window
        paid_media_spends: List of paid media spend column names
        paid_media_selected: List of selected paid media names
        exposure_vars: List of exposure variable names
        organic_vars: List of organic variable names
        refresh_added_start: Start date for refresh period
        dt_mod_roll_wind: Rolling window data
        rolling_window_length: Length of rolling window
        
    Returns:
        DataFrame containing spend share calculations
    """
    # Get training data slice
    dt_input_train = input_collect['dt_input'].iloc[rolling_window_start_which:rolling_window_end_which]
    
    # Calculate total and mean spend for paid media
    temp = dt_input_train[paid_media_spends]
    dt_spend_share = pd.DataFrame({
        'rn': paid_media_selected,
        'total_spend': temp.sum(),
        'mean_spend': temp.mean()
    })
    dt_spend_share['spend_share'] = dt_spend_share['total_spend'] / dt_spend_share['total_spend'].sum()

    # Handle exposure and organic variables
    if exposure_vars or organic_vars:
        all_vars = exposure_vars + organic_vars
        temp = dt_input_train[all_vars].mean()
        temp_df = pd.DataFrame({
            'rn': all_vars,
            'mean_exposure': temp
        })
        dt_spend_share = pd.merge(dt_spend_share, temp_df, on='rn', how='outer')
    else:
        dt_spend_share['mean_exposure'] = np.nan

    # Calculate refresh period metrics
    refresh_added_start_which = dt_mod_roll_wind[dt_mod_roll_wind['ds'] == refresh_added_start].index[0]
    temp = dt_input_train[paid_media_spends].iloc[refresh_added_start_which:rolling_window_length]
    
    dt_spend_share_rf = pd.DataFrame({
        'rn': paid_media_selected,
        'total_spend': temp.sum(),
        'mean_spend': temp.mean()
    })
    dt_spend_share_rf['spend_share'] = dt_spend_share_rf['total_spend'] / dt_spend_share_rf['total_spend'].sum()

    # Join exposure variables for refresh data
    if exposure_vars or organic_vars:
        all_vars = exposure_vars + organic_vars
        temp = dt_input_train[all_vars].iloc[refresh_added_start_which:rolling_window_length].mean()
        temp_df = pd.DataFrame({
            'rn': all_vars,
            'mean_exposure': temp
        })
        dt_spend_share_rf = pd.merge(dt_spend_share_rf, temp_df, on='rn', how='outer')
    else:
        dt_spend_share_rf['mean_exposure'] = np.nan

    # Join both dataframes
    return pd.merge(
        dt_spend_share, 
        dt_spend_share_rf,
        on='rn',
        suffixes=('', '_refresh')
    ) 