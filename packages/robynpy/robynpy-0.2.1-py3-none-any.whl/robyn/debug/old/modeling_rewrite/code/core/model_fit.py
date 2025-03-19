import numpy as np
from typing import Dict, Optional, Any, Union
from sklearn.linear_model import Ridge
from dataclasses import dataclass
import numpy.typing as npt

@dataclass
class ModelOutput:
    """Output from model refitting"""
    rsq_train: float
    rsq_val: Optional[float]
    rsq_test: Optional[float]
    nrmse_train: float
    nrmse_val: Optional[float]
    nrmse_test: Optional[float]
    coefs: npt.NDArray[np.float64]
    y_train_pred: npt.NDArray[np.float64]
    y_val_pred: Optional[npt.NDArray[np.float64]]
    y_test_pred: Optional[npt.NDArray[np.float64]]
    y_pred: npt.NDArray[np.float64]
    model: Ridge
    df_int: int

def get_rsq(
    true: npt.NDArray[np.float64], 
    predicted: npt.NDArray[np.float64], 
    p: int, 
    df_int: int, 
    n_train: Optional[int] = None
) -> float:
    """
    Calculate adjusted R-squared
    
    Args:
        true: True values
        predicted: Predicted values
        p: Number of predictors
        df_int: Degrees of freedom for intercept
        n_train: Number of training samples (for validation/test R-squared)
    
    Returns:
        Adjusted R-squared value
    """
    n = len(true)
    if n_train is not None:
        n = n_train
    
    ss_tot = np.sum((true - np.mean(true))**2)
    ss_res = np.sum((true - predicted)**2)
    
    r2 = 1 - (ss_res / ss_tot)
    adj_r2 = 1 - (1 - r2) * ((n - df_int) / (n - p - df_int))
    
    return adj_r2

def model_refit(
    x_train: npt.NDArray[np.float64],
    y_train: npt.NDArray[np.float64],
    x_val: Optional[npt.NDArray[np.float64]] = None,
    y_val: Optional[npt.NDArray[np.float64]] = None,
    x_test: Optional[npt.NDArray[np.float64]] = None,
    y_test: Optional[npt.NDArray[np.float64]] = None,
    lambda_: float = 1.0,
    lower_limits: Optional[npt.NDArray[np.float64]] = None,
    upper_limits: Optional[npt.NDArray[np.float64]] = None,
    intercept: bool = True,
    intercept_sign: str = "non_negative",
    penalty_factor: Optional[npt.NDArray[np.float64]] = None,
    **kwargs
) -> ModelOutput:
    """
    Refit model with given parameters
    
    Args:
        x_train: Training features
        y_train: Training target
        x_val: Validation features
        y_val: Validation target
        x_test: Test features
        y_test: Test target
        lambda_: Ridge regression penalty parameter
        lower_limits: Lower bounds for coefficients
        upper_limits: Upper bounds for coefficients
        intercept: Whether to fit intercept
        intercept_sign: Sign constraint for intercept ("non_negative" or None)
        penalty_factor: Per-feature penalty factors
        **kwargs: Additional arguments passed to Ridge
    
    Returns:
        ModelOutput containing fit results
    """
    if penalty_factor is None:
        penalty_factor = np.ones(x_train.shape[1])
        
    # Initial model fit
    model = Ridge(
        alpha=lambda_,
        fit_intercept=intercept,
        **kwargs
    )
    
    model.fit(x_train, y_train)
    df_int = 1 if intercept else 0
    
    # Refit without intercept if needed
    if intercept_sign == "non_negative" and model.intercept_ < 0:
        model = Ridge(
            alpha=lambda_,
            fit_intercept=False,
            **kwargs
        )
        model.fit(x_train, y_train)
        df_int = 0
    
    # Apply coefficient constraints if provided
    if lower_limits is not None or upper_limits is not None:
        coefs = model.coef_.copy()
        if lower_limits is not None:
            coefs = np.maximum(coefs, lower_limits)
        if upper_limits is not None:
            coefs = np.minimum(coefs, upper_limits)
        model.coef_ = coefs
    
    # Calculate predictions
    y_train_pred = model.predict(x_train)
    y_val_pred = model.predict(x_val) if x_val is not None else None
    y_test_pred = model.predict(x_test) if x_test is not None else None
    
    # Calculate R-squared values
    rsq_train = get_rsq(y_train, y_train_pred, x_train.shape[1], df_int)
    
    if x_val is not None and y_val is not None:
        rsq_val = get_rsq(y_val, y_val_pred, x_val.shape[1], df_int, len(y_train))
        rsq_test = get_rsq(y_test, y_test_pred, x_test.shape[1], df_int, len(y_train))
        y_pred = np.concatenate([y_train_pred, y_val_pred, y_test_pred])
    else:
        rsq_val = rsq_test = None
        y_pred = y_train_pred
    
    # Calculate NRMSE values
    nrmse_train = np.sqrt(np.mean((y_train - y_train_pred)**2)) / (np.max(y_train) - np.min(y_train))
    
    if x_val is not None and y_val is not None:
        nrmse_val = np.sqrt(np.mean((y_val - y_val_pred)**2)) / (np.max(y_val) - np.min(y_val))
        nrmse_test = np.sqrt(np.mean((y_test - y_test_pred)**2)) / (np.max(y_test) - np.min(y_test))
    else:
        nrmse_val = nrmse_test = None
    
    # Combine coefficients with intercept
    if intercept:
        coefs = np.concatenate([[model.intercept_], model.coef_])
    else:
        coefs = model.coef_
    
    return ModelOutput(
        rsq_train=rsq_train,
        rsq_val=rsq_val,
        rsq_test=rsq_test,
        nrmse_train=nrmse_train,
        nrmse_val=nrmse_val,
        nrmse_test=nrmse_test,
        coefs=coefs,
        y_train_pred=y_train_pred,
        y_val_pred=y_val_pred,
        y_test_pred=y_test_pred,
        y_pred=y_pred,
        model=model,
        df_int=df_int
    ) 