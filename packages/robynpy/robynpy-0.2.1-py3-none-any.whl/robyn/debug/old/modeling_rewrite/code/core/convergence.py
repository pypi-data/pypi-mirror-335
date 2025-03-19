from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

@dataclass
class ConvergenceOutput:
    """Output from convergence analysis
    
    Attributes:
        moo_distrb_plot: Distribution plot showing convergence by iterations
        moo_cloud_plot: Scatter plot showing multi-objective performance
        errors: DataFrame containing convergence metrics
        conv_msg: List of convergence messages
        sd_qtref: Reference quantile used for std dev convergence
        med_lowb: Lower bound used for median convergence
    """
    moo_distrb_plot: plt.Figure
    moo_cloud_plot: plt.Figure
    errors: pd.DataFrame
    conv_msg: List[str]
    sd_qtref: int
    med_lowb: int

def robyn_converge(
    output_models: Any,
    n_cuts: int = 20,
    sd_qtref: int = 3,
    med_lowb: int = 2,
    nrmse_win: Tuple[float, float] = (0, 0.998),
    **kwargs
) -> ConvergenceOutput:
    """
    Check model convergence and create convergence plots
    
    Convergence is calculated using two criteria:
    1. Last quantile's standard deviation < first 3 quantiles' mean standard deviation
    2. Last quantile's absolute median < absolute first quantile's median - 2 * first 3 quantiles' mean standard deviation
    
    Args:
        output_models: Output from model training
        n_cuts: Number of quantile cuts (default 20 = 5% cuts each)
        sd_qtref: Reference quantile for std dev convergence rule (default 3)
        med_lowb: Lower bound distance for median convergence rule (default 2)
        nrmse_win: NRMSE winsorization bounds (default (0, 0.998))
        
    Returns:
        ConvergenceOutput containing plots and convergence results
    
    Raises:
        AssertionError: If n_cuts is not greater than min(sd_qtref, med_lowb) + 1
    """
    assert n_cuts > min(sd_qtref, med_lowb) + 1, "n_cuts must be greater than min(sd_qtref, med_lowb) + 1"
    
    # Gather all trials
    trials = [f"trial{i}" for i in range(1, output_models.trials + 1)]
    df_list = []
    for trial in trials:
        trial_data = getattr(output_models, trial)
        df_list.append(trial_data.result_collect['result_hyp_param'])
    df = pd.concat(df_list)
    
    calibrated = bool(df['mape'].sum() > 0)
    
    # Calculate quantiles
    error_cols = ['nrmse', 'decomp_rssd']
    if calibrated:
        error_cols.append('mape')
        
    dt_objfunc_cvg = pd.melt(
        df,
        id_vars=['elapsed_accum', 'trial', 'iter'],
        value_vars=error_cols,
        var_name='error_type',
        value_name='value'
    )
    
    # Filter and process
    dt_objfunc_cvg = dt_objfunc_cvg[
        (dt_objfunc_cvg['value'] > 0) & 
        (dt_objfunc_cvg['value'].notna())
    ]
    dt_objfunc_cvg['error_type'] = dt_objfunc_cvg['error_type'].str.upper()
    
    # Create quantile cuts
    dt_objfunc_cvg['cuts'] = pd.qcut(
        dt_objfunc_cvg['iter'],
        q=n_cuts,
        labels=[round(x) for x in np.linspace(
            dt_objfunc_cvg['iter'].max()/n_cuts,
            dt_objfunc_cvg['iter'].max(),
            n_cuts
        )]
    )
    
    # Calculate statistics by cut
    errors = (dt_objfunc_cvg
        .groupby(['error_type', 'cuts'])
        .agg({
            'value': ['count', 'median', 'std']
        })
        .reset_index()
    )
    errors.columns = ['error_type', 'cuts', 'n', 'median', 'std']
    
    # Calculate convergence metrics
    errors = (errors
        .groupby('error_type')
        .apply(lambda x: x.assign(
            med_var_p=abs(round(100 * (x['median'] - x['median'].shift(1)) / x['median'], 2)),
            first_med=abs(x['median'].iloc[0]),
            first_med_avg=abs(x['median'].iloc[:sd_qtref].mean()),
            last_med=abs(x['median'].iloc[-1]),
            first_sd=x['std'].iloc[0],
            first_sd_avg=x['std'].iloc[:sd_qtref].mean(),
            last_sd=x['std'].iloc[-1]
        ))
        .reset_index(drop=True)
    )
    
    # Calculate thresholds and flags
    errors['med_thres'] = abs(errors['first_med'] - med_lowb * errors['first_sd_avg'])
    errors['flag_med'] = abs(errors['median']) < errors['med_thres']
    errors['flag_sd'] = errors['std'] < errors['first_sd_avg']
    
    # Generate convergence messages
    conv_msg = []
    for obj_fun in errors['error_type'].unique():
        temp_df = errors[errors['error_type'] == obj_fun].copy()
        last_qt = temp_df.iloc[-1]
        
        msg = (
            f"{obj_fun} {'NOT ' if not (last_qt['flag_sd'] and last_qt['flag_med']) else ''}"
            f"converged: sd@qt.{n_cuts} {last_qt['last_sd']:.2f} "
            f"{'<=' if last_qt['flag_sd'] else '>'} {last_qt['first_sd_avg']:.2f} & "
            f"|med@qt.{n_cuts}| {abs(last_qt['last_med']):.2f} "
            f"{'<=' if last_qt['flag_med'] else '>'} {last_qt['med_thres']:.2f}"
        )
        conv_msg.append(msg)
        logger.info(f"- {msg}")
    
    # Create plots
    subtitle = (
        f"{max(df['trial'])} trial{'s' if max(df['trial']) > 1 else ''} with "
        f"{max(dt_objfunc_cvg['cuts'])} iterations{' each' if max(df['trial']) > 1 else ''} "
        f"using {output_models.nevergrad_algo}"
    )
    
    # Distribution plot
    fig_dist = plt.figure(figsize=(12, 6))
    for error_type in dt_objfunc_cvg['error_type'].unique():
        data = dt_objfunc_cvg[dt_objfunc_cvg['error_type'] == error_type]
        plt.subplot(1, len(error_cols), error_cols.index(error_type.lower()) + 1)
        sns.violinplot(data=data, x='value', y='cuts', orient='h')
        plt.title(error_type)
    plt.suptitle(f"Objective convergence by iterations quantiles\n{subtitle}")
    plt.tight_layout()
    
    # Cloud plot
    fig_cloud = plt.figure(figsize=(8, 6))
    plt.scatter(df['nrmse'], df['decomp_rssd'], c=df['elapsed_accum'], 
               cmap='viridis', alpha=0.6)
    if calibrated:
        plt.scatter(df['nrmse'], df['decomp_rssd'], 
                   s=df['mape']*100, alpha=0.3, c='red')
    plt.colorbar(label='Time [s]')
    plt.xlabel(f"NRMSE [Winsorized {nrmse_win[0]}-{nrmse_win[1]}]" 
              if max(nrmse_win) != 1 else "NRMSE")
    plt.ylabel("DECOMP.RSSD")
    plt.title(f"{'Multi-objective evolutionary performance with calibration' if calibrated else 'Multi-objective evolutionary performance'}\n{subtitle}")
    plt.tight_layout()
    
    return ConvergenceOutput(
        moo_distrb_plot=fig_dist,
        moo_cloud_plot=fig_cloud,
        errors=errors,
        conv_msg=conv_msg,
        sd_qtref=sd_qtref,
        med_lowb=med_lowb
    ) 