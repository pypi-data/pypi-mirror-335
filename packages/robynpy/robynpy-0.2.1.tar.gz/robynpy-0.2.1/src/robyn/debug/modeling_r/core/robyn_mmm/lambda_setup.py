from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from ...utils.lambda_calc import lambda_seq

def setup_lambda(
    dt_mod: pd.DataFrame,
    lambda_min_ratio: float = 0.0001
) -> Tuple[float, float, np.ndarray]:
    """
    Calculate lambda sequence and boundaries for regularization
    
    Args:
        dt_mod: Model data containing features and target
        lambda_min_ratio: Minimum lambda ratio (default from glmnet)
        
    Returns:
        Tuple containing:
            - lambda_max: Maximum lambda value
            - lambda_min: Minimum lambda value
            - lambdas: Full sequence of lambda values
    """
    # Get feature matrix and target
    x_vars = dt_mod.drop(['ds', 'dep_var'], axis=1)
    y_var = dt_mod['dep_var']
    
    # Calculate lambda sequence
    lambdas = lambda_seq(
        x=x_vars,
        y=y_var,
        seq_len=100,
        lambda_min_ratio=lambda_min_ratio
    )
    
    # Calculate lambda boundaries
    lambda_max = max(lambdas) * 0.1
    lambda_min = lambda_max * lambda_min_ratio
    
    return lambda_max, lambda_min, lambdas 