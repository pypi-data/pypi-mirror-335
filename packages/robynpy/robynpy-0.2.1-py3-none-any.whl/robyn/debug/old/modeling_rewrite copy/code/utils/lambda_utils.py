# robyn/debug/modeling_rewrite/utils/lambda_utils.py

import numpy as np
from typing import Tuple

def lambda_seq(
    x: np.ndarray,
    y: np.ndarray,
    seq_len: int = 100,
    lambda_min_ratio: float = 0.0001
) -> np.ndarray:
    """Calculate lambda sequence for ridge regression
    
    Args:
        x: Feature matrix
        y: Target vector
        seq_len: Number of lambda values to generate
        lambda_min_ratio: Minimum lambda ratio
        
    Returns:
        Array of lambda values
    """
    # Scale features
    x_scaled = (x - x.mean(axis=0)) / x.std(axis=0, ddof=1)
    x_scaled = np.nan_to_num(x_scaled, 0)  # Replace NaN with 0
    
    # Calculate lambda max
    lambda_max = np.max(np.abs(x_scaled.T @ y)) / (0.001 * x.shape[0])
    
    # Generate sequence
    log_vals = np.linspace(
        np.log(lambda_max), 
        np.log(lambda_max * lambda_min_ratio), 
        seq_len
    )
    return np.exp(log_vals)