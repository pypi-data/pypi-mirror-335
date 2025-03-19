import numpy as np
import pandas as pd
from typing import Union, List

def lambda_seq(
    x: Union[pd.DataFrame, np.ndarray],
    y: Union[pd.Series, np.ndarray],
    seq_len: int = 100,
    lambda_min_ratio: float = 0.0001
) -> np.ndarray:
    """
    Calculate sequence of lambda values for regularization.
    
    Args:
        x: Feature matrix
        y: Target vector
        seq_len: Length of the sequence
        lambda_min_ratio: Minimum lambda ratio
        
    Returns:
        Array of lambda values
    """
    def mysd(y: np.ndarray) -> float:
        """Custom standard deviation calculation matching R implementation"""
        return np.sqrt(np.sum((y - np.mean(y))**2) / len(y))
    
    # Calculate standard deviation for each column
    if isinstance(x, pd.DataFrame):
        x = x.values
    if isinstance(y, pd.Series):
        y = y.values
        
    # Scale features
    x_sd = np.apply_along_axis(mysd, 0, x)
    sx = x / x_sd[None, :]
    
    # Check for NaN columns and replace with zeros
    check_nan = np.isnan(sx).all(axis=0)
    sx[:, check_nan] = 0
    
    # Calculate lambda sequence
    lambda_max = np.max(np.abs(np.sum(sx * y[:, None], axis=0))) / (0.001 * x.shape[0])
    lambda_max_log = np.log(lambda_max)
    log_seq = np.linspace(
        np.log(lambda_max),
        np.log(lambda_max * lambda_min_ratio),
        seq_len
    )
    lambdas = np.exp(log_seq)
    
    return lambdas 