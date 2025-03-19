from typing import Dict, List, Any, Tuple, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
from scipy import stats

@dataclass
class TransformationOutput:
    """Output from media transformations"""
    dt_mod_saturated: pd.DataFrame
    dt_saturated_immediate: pd.DataFrame
    dt_saturated_carryover: pd.DataFrame
    inflexions: Dict[str, float]
    inflations: Dict[str, float]

def normalize(x: np.ndarray) -> np.ndarray:
    """
    Normalize array to [0,1] range
    
    Args:
        x: Input array
        
    Returns:
        Normalized array
    """
    if np.ptp(x) == 0:  # ptp = peak to peak (max - min)
        result = np.zeros_like(x)
        result[0] = 1
        return result
    return (x - np.min(x)) / np.ptp(x)

def saturation_hill(
    x: np.ndarray,
    alpha: float,
    gamma: float,
    x_marginal: Optional[np.ndarray] = None
) -> Dict[str, Any]:
    """
    Apply Hill saturation transformation
    
    Args:
        x: Input values
        alpha: Shape parameter (larger = more S-shape, smaller = more C-shape)
        gamma: Inflexion point control (larger = later inflexion)
        x_marginal: Optional marginal values for transformation
        
    Returns:
        Dictionary containing transformed values and inflexion point
    """
    assert isinstance(alpha, (int, float)), "alpha must be a single number"
    assert isinstance(gamma, (int, float)), "gamma must be a single number"
    
    inflexion = np.max(x) * gamma
    
    if x_marginal is None:
        x_saturated = x**alpha / (x**alpha + inflexion**alpha)
    else:
        x_saturated = x_marginal**alpha / (x_marginal**alpha + inflexion**alpha)
        
    return {
        'x_saturated': x_saturated,
        'inflexion': inflexion
    }

def adstock_geometric(x: np.ndarray, theta: float) -> Dict[str, Any]:
    """
    Apply geometric adstock transformation
    
    Args:
        x: Input values
        theta: Decay rate parameter. Examples:
            - TV: 0.3 to 0.8
            - OOH/Print/Radio: 0.1 to 0.4
            - Digital: 0 to 0.3
            
    Returns:
        Dictionary containing:
            - x: Original values
            - x_decayed: Transformed values
            - theta_vec_cum: Cumulative theta values
            - inflation_total: Total inflation factor
    """
    assert isinstance(theta, (int, float)), "theta must be a single number"
    
    if len(x) > 1:
        x_decayed = np.zeros_like(x, dtype=float)
        x_decayed[0] = x[0]
        
        # Calculate decay
        for xi in range(1, len(x_decayed)):
            x_decayed[xi] = x[xi] + theta * x_decayed[xi - 1]
            
        # Calculate cumulative theta
        theta_vec_cum = np.zeros_like(x, dtype=float)
        theta_vec_cum[0] = theta
        for t in range(1, len(x)):
            theta_vec_cum[t] = theta_vec_cum[t - 1] * theta
    else:
        x_decayed = x
        theta_vec_cum = np.array([theta])
    
    inflation_total = np.sum(x_decayed) / np.sum(x)
    
    return {
        'x': x,
        'x_decayed': x_decayed,
        'theta_vec_cum': theta_vec_cum,
        'inflation_total': inflation_total
    }

def adstock_weibull(
    x: np.ndarray,
    shape: float,
    scale: float,
    windlen: Optional[int] = None,
    type: str = "pdf"
) -> Dict[str, Any]:
    """
    Apply Weibull adstock transformation
    
    Args:
        x: Input values
        shape: Shape parameter. Controls decay curve shape:
            - CDF: Recommended (0.0001, 2). Larger = more S-shape, smaller = more L-shape
            - PDF: Recommended (0.0001, 10) or (2.0001, 10) for strong lagged effect
        scale: Scale parameter. Controls inflection point. Recommended (0, 0.1)
        windlen: Window length (defaults to length of x)
        type: "pdf" or "cdf"
            - PDF: Allows lagged effect (peak after x=0)
            - CDF: Peak always at first period
            
    Returns:
        Dictionary containing transformed values and parameters
    """
    if windlen is None:
        windlen = len(x)
        
    if len(x) > 1:
        x_bin = np.arange(1, windlen + 1)
        scale_trans = int(np.quantile(x_bin, scale))
        
        if shape == 0 or scale == 0:
            x_decayed = x
            theta_vec_cum = theta_vec = np.zeros(windlen)
            x_imme = x
        else:
            if type.lower() == "pdf":
                # PDF transformation
                theta_vec_cum = normalize(
                    stats.weibull_min.pdf(x_bin, shape, loc=0, scale=scale_trans)
                )
            else:  # CDF
                # CDF transformation
                theta_vec = np.ones(windlen)
                theta_vec[1:] = 1 - stats.weibull_min.cdf(
                    x_bin[:-1], shape, loc=0, scale=scale_trans
                )
                theta_vec_cum = np.cumprod(theta_vec)
            
            # Calculate decayed values
            x_decayed_matrix = np.zeros((windlen, len(x)))
            for i, (x_val, x_pos) in enumerate(zip(x, range(1, len(x) + 1))):
                x_vec = np.zeros(windlen)
                x_vec[x_pos - 1:] = x_val
                theta_vec_cum_lag = np.pad(
                    theta_vec_cum[:-x_pos + 1], 
                    (x_pos - 1, 0), 
                    'constant'
                )
                x_decayed_matrix[:, i] = x_vec * theta_vec_cum_lag
                
            x_imme = np.diag(x_decayed_matrix)
            x_decayed = np.sum(x_decayed_matrix, axis=1)[:len(x)]
    else:
        x_decayed = x_imme = x
        theta_vec_cum = np.array([1])
    
    inflation_total = np.sum(x_decayed) / np.sum(x)
    
    return {
        'x': x,
        'x_decayed': x_decayed,
        'theta_vec_cum': theta_vec_cum,
        'inflation_total': inflation_total,
        'x_imme': x_imme
    }

def transform_adstock(
    x: np.ndarray,
    adstock: str,
    theta: Optional[float] = None,
    shape: Optional[float] = None,
    scale: Optional[float] = None,
    windlen: Optional[int] = None
) -> Dict[str, Any]:
    """
    Apply adstock transformation
    
    Args:
        x: Input values
        adstock: Type of adstock ("geometric", "weibull_cdf", or "weibull_pdf")
        theta: Decay parameter for geometric adstock
        shape: Shape parameter for Weibull adstock
        scale: Scale parameter for Weibull adstock
        windlen: Window length (defaults to length of x)
        
    Returns:
        Dictionary containing transformed values and parameters
    """
    if windlen is None:
        windlen = len(x)
        
    if adstock == "geometric":
        return adstock_geometric(x=x, theta=theta)
    else:
        adstock_type = adstock[-3:]  # get 'cdf' or 'pdf' from end
        return adstock_weibull(
            x=x,
            shape=shape,
            scale=scale,
            windlen=windlen,
            type=adstock_type
        )

def run_transformations(
    all_media: List[str],
    window_start_loc: int,
    window_end_loc: int,
    dt_mod: pd.DataFrame,
    adstock: str,
    dt_hyppar: pd.DataFrame,
    **kwargs
) -> TransformationOutput:
    """
    Transform media variables using adstock and saturation transformations
    
    Args:
        all_media: List of all selected paid media variable names
        window_start_loc: Rolling window start location
        window_end_loc: Rolling window end location
        dt_mod: Transformed input table
        adstock: Adstock configuration type
        dt_hyppar: All hyperparameters for provided media
        
    Returns:
        TransformationOutput containing transformed data and parameters
    """
    dt_mod_adstocked = dt_mod.drop('ds', axis=1)
    window_loc = slice(window_start_loc, window_end_loc + 1)
    
    adstocked_collect = {}
    saturated_total_collect = {}
    saturated_immediate_collect = {}
    saturated_carryover_collect = {}
    inflexion_collect = {}
    inflation_collect = {}
    
    for media in all_media:
        ################################################
        # 1. Adstocking (whole data)
        # Decayed/adstocked response = Immediate response + Carryover response
        m = dt_mod_adstocked[media].values
        
        if adstock == "geometric":
            theta = dt_hyppar[f"{media}_thetas"].iloc[0]
        elif "weibull" in adstock:
            shape = dt_hyppar[f"{media}_shapes"].iloc[0]
            scale = dt_hyppar[f"{media}_scales"].iloc[0]
        
        x_list = transform_adstock(
            m, 
            adstock, 
            theta=theta if adstock == "geometric" else None,
            shape=shape if "weibull" in adstock else None,
            scale=scale if "weibull" in adstock else None
        )
        
        input_total = x_list['x_decayed']
        input_immediate = x_list['x_imme'] if adstock == "weibull_pdf" else m
        adstocked_collect[media] = input_total
        input_carryover = input_total - input_immediate
        
        ################################################
        # 2. Saturation (only window data)
        # Saturated response = Immediate response + carryover response
        input_total_rw = input_total[window_loc]
        input_carryover_rw = input_carryover[window_loc]
        
        alpha = dt_hyppar[f"{media}_alphas"].iloc[0]
        gamma = dt_hyppar[f"{media}_gammas"].iloc[0]
        
        sat_temp_total = saturation_hill(
            x=input_total_rw,
            alpha=alpha,
            gamma=gamma
        )
        
        sat_temp_caov = saturation_hill(
            x=input_total_rw,
            alpha=alpha,
            gamma=gamma,
            x_marginal=input_carryover_rw
        )
        
        saturated_total_collect[media] = sat_temp_total['x_saturated']
        saturated_carryover_collect[media] = sat_temp_caov['x_saturated']
        saturated_immediate_collect[media] = (
            saturated_total_collect[media] - saturated_carryover_collect[media]
        )
        
        inflexion_collect[f"{media}_inflexion"] = sat_temp_total['inflexion']
        inflation_collect[f"{media}_inflation"] = x_list['inflation_total']
    
    # Prepare output dataframes
    non_media_cols = [col for col in dt_mod_adstocked.columns if col not in all_media]
    
    dt_mod_saturated = pd.concat([
        dt_mod_adstocked.loc[window_loc, non_media_cols],
        pd.DataFrame(saturated_total_collect)
    ], axis=1)
    
    dt_saturated_immediate = pd.DataFrame(saturated_immediate_collect).fillna(0)
    dt_saturated_carryover = pd.DataFrame(saturated_carryover_collect).fillna(0)
    
    return TransformationOutput(
        dt_mod_saturated=dt_mod_saturated,
        dt_saturated_immediate=dt_saturated_immediate,
        dt_saturated_carryover=dt_saturated_carryover,
        inflexions=inflexion_collect,
        inflations=inflation_collect
    )
