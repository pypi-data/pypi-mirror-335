import pandas as pd
import numpy as np
import logging
from typing import List, Dict, Optional
from plotnine import (
    ggplot, aes, geom_density_ridges, facet_grid, scale_fill_distiller,
    theme_minimal, labs, geom_point, scale_color_gradient, guides
)
from mizani.palettes import brewer_pal

def winsorize(x: pd.Series, limits: List[float]) -> pd.Series:
    """Winsorize a series between specified quantiles."""
    lower = x.quantile(limits[0])
    upper = x.quantile(limits[1])
    return x.clip(lower=lower, upper=upper)

def robyn_converge(
    output_models: 'ModelOutputs',
    n_cuts: int = 20,
    sd_qtref: int = 3,
    med_lowb: int = 2,
    nrmse_win: List[float] = [0, 0.998]
) -> Dict:
    """
    Check model convergence and create convergence plots.
    
    Args:
        output_models: Output from model training
        n_cuts: Number of cuts for analysis (default: 20)
        sd_qtref: Reference quantile for std deviation convergence (default: 3)
        med_lowb: Lower bound distance for median convergence (default: 2)
        nrmse_win: Winsorization bounds for NRMSE [min, max] (default: [0, 0.998])
    
    Returns:
        Dictionary containing convergence plots and results
    """
    if n_cuts <= min(sd_qtref, med_lowb) + 1:
        raise ValueError("n_cuts must be greater than min(sd_qtref, med_lowb) + 1")

    # Gather all trials
    trials_data = []
    for trial in output_models.trials:
        trials_data.append(trial.result_collect.result_hyp_param)
    df = pd.concat(trials_data)
    
    calibrated = df['mape'].sum() > 0

    # Calculate quantiles
    error_types = ['nrmse', 'decomp.rssd', 'mape'] if calibrated else ['nrmse', 'decomp.rssd']
    dt_objfunc_cvg = []
    
    for error_type in error_types:
        if error_type in df.columns:
            temp_df = df[['ElapsedAccum', 'trial', error_type]].copy()
            temp_df = temp_df[temp_df[error_type] > 0]
            temp_df = temp_df[np.isfinite(temp_df[error_type])]
            temp_df['error_type'] = error_type.upper()
            temp_df['value'] = temp_df[error_type]
            temp_df['iter'] = temp_df.groupby('trial').cumcount() + 1
            dt_objfunc_cvg.append(temp_df)
    
    dt_objfunc_cvg = pd.concat(dt_objfunc_cvg)
    
    # Calculate cuts
    max_iter = dt_objfunc_cvg['iter'].max()
    cut_bins = np.linspace(0, max_iter, n_cuts + 1)
    dt_objfunc_cvg['cuts'] = pd.cut(
        dt_objfunc_cvg['iter'],
        bins=cut_bins,
        labels=[round(x) for x in np.linspace(max_iter/n_cuts, max_iter, n_cuts)],
        include_lowest=True
    )

    # Calculate statistics for each cut
    errors = []
    for error_type in dt_objfunc_cvg['error_type'].unique():
        group_data = dt_objfunc_cvg[dt_objfunc_cvg['error_type'] == error_type]
        stats = group_data.groupby('cuts').agg({
            'value': ['count', 'median', 'std']
        }).reset_index()
        
        stats.columns = ['cuts', 'n', 'median', 'std']
        stats['error_type'] = error_type
        
        # Calculate convergence metrics
        stats['first_med'] = abs(stats['median'].iloc[0])
        stats['first_med_avg'] = abs(stats['median'].iloc[:sd_qtref].mean())
        stats['last_med'] = abs(stats['median'].iloc[-1])
        stats['first_sd'] = stats['std'].iloc[0]
        stats['first_sd_avg'] = stats['std'].iloc[:sd_qtref].mean()
        stats['last_sd'] = stats['std'].iloc[-1]
        
        # Calculate thresholds and flags
        stats['med_thres'] = abs(stats['first_med'] - med_lowb * stats['first_sd_avg'])
        stats['flag_med'] = abs(stats['median']) < stats['med_thres']
        stats['flag_sd'] = stats['std'] < stats['first_sd_avg']
        
        errors.append(stats)
    
    errors = pd.concat(errors)

    # Generate convergence messages
    conv_msg = []
    for error_type in errors['error_type'].unique():
        temp_df = errors[errors['error_type'] == error_type].copy()
        last_qt = temp_df.iloc[-1]
        
        did_converge = last_qt['flag_sd'] and last_qt['flag_med']
        msg = (
            f"{error_type} {'converged' if did_converge else 'NOT converged'}: "
            f"sd@qt.{n_cuts} {last_qt['last_sd']:.2f} "
            f"{'<=' if last_qt['flag_sd'] else '>'} {last_qt['first_sd_avg']:.2f} & "
            f"|med@qt.{n_cuts}| {abs(last_qt['last_med']):.2f} "
            f"{'<=' if last_qt['flag_med'] else '>'} {last_qt['med_thres']:.2f}"
        )
        conv_msg.append(msg)
        logging.info(msg)

    # Create subtitle for plots
    subtitle = (
        f"{max(df['trial'])} trial{'s' if max(df['trial']) > 1 else ''} "
        f"with {max(dt_objfunc_cvg['cuts'])} iteration"
        f"{'s each' if max(df['trial']) > 1 else ''} "
        f"using {output_models.nevergrad_algo}"
    )

    # Create distribution plot
    plot_data = dt_objfunc_cvg.copy()
    plot_data['id'] = plot_data['cuts'].astype(str).astype(int)
    plot_data['cuts'] = pd.Categorical(
        plot_data['cuts'],
        categories=sorted(plot_data['cuts'].unique(), reverse=True)
    )
    
    # Winsorize values by error type
    for error_type in plot_data['error_type'].unique():
        mask = plot_data['error_type'] == error_type
        plot_data.loc[mask, 'value'] = winsorize(
            plot_data.loc[mask, 'value'],
            nrmse_win
        )

    moo_distrb_plot = (
        ggplot(plot_data, aes(x='value', y='cuts', fill='-id'))
        + geom_density_ridges(
            scale=2.5,
            color='white',
            alpha=0.7
        )
        + facet_grid('~ error_type', scales='free')
        + scale_fill_distiller(palette='GnBu')
        + theme_minimal()
        + guides(fill='none')
        + labs(
            x='Objective functions',
            y='Iterations [#]',
            title='Objective convergence by iterations quantiles',
            subtitle=subtitle,
            caption='\n'.join(conv_msg)
        )
    )

    # Create cloud plot
    plot_data = df.copy()
    plot_data['nrmse'] = winsorize(plot_data['nrmse'], nrmse_win)
    
    moo_cloud_plot = (
        ggplot(plot_data, aes(
            x='nrmse',
            y='decomp.rssd',
            color='ElapsedAccum'
        ))
        + scale_color_gradient(
            low='skyblue',
            high='navyblue'
        )
        + labs(
            title=('Multi-objective evolutionary performance with calibration'
                  if calibrated else
                  'Multi-objective evolutionary performance'),
            subtitle=subtitle,
            x=(f"NRMSE [Winsorized {'-'.join(map(str, nrmse_win))}]"
               if max(nrmse_win) != 1 else "NRMSE"),
            y='DECOMP.RSSD',
            color='Time [s]',
            size='MAPE',
            caption='\n'.join(conv_msg)
        )
        + theme_minimal()
    )

    if calibrated:
        moo_cloud_plot = (
            moo_cloud_plot
            + geom_point(aes(size='mape', alpha='1 - mape'))
            + guides(alpha='none')
        )
    else:
        moo_cloud_plot = moo_cloud_plot + geom_point()

    return {
        'errors': errors,
        'conv_msg': conv_msg,
        'sd_qtref': sd_qtref,
        'med_lowb': med_lowb,
        'moo_distrb_plot': moo_distrb_plot,
        'moo_cloud_plot': moo_cloud_plot
    } 