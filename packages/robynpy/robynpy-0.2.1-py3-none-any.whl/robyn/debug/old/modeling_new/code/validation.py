import pandas as pd
import numpy as np
from typing import Dict, Optional
from plotnine import (
    ggplot, aes, geom_point, geom_smooth, facet_grid, theme_minimal,
    labs, scale_color_brewer, geom_hline
)
from patchwork import vstack  # For combining plots vertically

def winsorize(x: pd.Series, limits: List[float]) -> pd.Series:
    """Winsorize a series between specified quantiles."""
    lower = x.quantile(limits[0])
    upper = x.quantile(limits[1])
    return x.clip(lower=lower, upper=upper)

def ts_validation(
    output_models: 'ModelOutputs',
    quiet: bool = False,
    **kwargs
) -> Dict:
    """
    Generate plots for Time-Series Validation and Convergence.
    
    Args:
        output_models: Output from model training
        quiet: Whether to suppress messages
        **kwargs: Additional arguments
        
    Returns:
        Combined validation plots
    """
    # Gather results from all trials
    trials_data = []
    for trial_num in range(output_models.trials):
        trial = getattr(output_models, f'trial{trial_num + 1}')
        trial_data = trial.result_collect.result_hyp_param.copy()
        trial_data['trial'] = trial_num + 1
        trials_data.append(trial_data)
    
    result_hyp_param = pd.concat(trials_data)
    result_hyp_param['i'] = result_hyp_param.groupby('trial').cumcount() + 1
    
    # Create long format data for RSQ and NRMSE
    rsq_cols = [col for col in result_hyp_param.columns if col.startswith('rsq_')]
    nrmse_cols = [col for col in result_hyp_param.columns if col.startswith('nrmse_')]
    
    result_hyp_param_long = pd.melt(
        result_hyp_param,
        id_vars=['solID', 'i', 'trial', 'train_size'],
        value_vars=rsq_cols,
        var_name='dataset',
        value_name='rsq'
    )
    
    # Add NRMSE values
    nrmse_data = pd.melt(
        result_hyp_param[['solID'] + nrmse_cols],
        id_vars=['solID'],
        value_vars=nrmse_cols,
        value_name='nrmse'
    )['nrmse']
    result_hyp_param_long['nrmse'] = nrmse_data.values
    
    # Clean up dataset names and apply winsorization
    result_hyp_param_long['dataset'] = result_hyp_param_long['dataset'].str.replace('rsq_', '')
    result_hyp_param_long['trial'] = 'Trial ' + result_hyp_param_long['trial'].astype(str)
    
    # Winsorize RSQ and NRMSE
    result_hyp_param_long['rsq'] = winsorize(result_hyp_param_long['rsq'], [0.01, 0.99])
    result_hyp_param_long['nrmse'] = winsorize(result_hyp_param_long['nrmse'], [0.00, 0.99])
    
    # Create iterations plot
    p_iters = (
        ggplot(result_hyp_param, aes(x='i', y='train_size'))
        + geom_point(alpha=0.5, size=1.2, shape='s', fill='black')
        + labs(y='Train Size', x='Iteration')
        + theme_minimal()
    )
    
    # Create NRMSE plot
    p_nrmse = (
        ggplot(result_hyp_param_long, aes(x='i', y='nrmse', color='dataset'))
        + geom_point(alpha=0.2, size=0.9)
        + geom_smooth(method='gam')
        + facet_grid('trial ~ .')
        + geom_hline(yintercept=0, linetype='dashed')
        + labs(
            y='NRMSE [Upper 1% Winsorized]',
            x='Iteration',
            color='Dataset'
        )
        + theme_minimal()
        + scale_color_brewer(palette='Set2')
    )
    
    # Combine plots vertically
    combined_plot = vstack([
        p_nrmse,
        p_iters
    ], heights=[len(result_hyp_param_long['trial'].unique()), 1])
    
    return {
        'plot': combined_plot,
        'data': result_hyp_param_long
    } 