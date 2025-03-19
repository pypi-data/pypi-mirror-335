# pyre-strict

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
from dataclasses import field
from datetime import datetime


@dataclass
class Trial:
    """
    Represents a single trial's results
    """
    result_collect: Dict[str, Any]
    result_hyp_param: pd.DataFrame = field(default_factory=pd.DataFrame)
    sol_id: str = "1_1_1"
    lift_calibration: pd.DataFrame = field(default_factory=pd.DataFrame)


@dataclass
class ModelOutputs:
    """
    Represents the overall outputs of the modeling process.
    """
    # Required fields (no defaults)
    trials: List[Trial]
    hyper_bound_ng: Dict[str, Any]
    hyper_bound_fixed: Dict[str, Any]
    hyper_updated: Dict[str, Any]
    
    # Optional fields (with defaults)
    train_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    cores: Optional[int] = None
    iterations: int = 2000
    intercept: bool = True
    intercept_sign: str = "non_negative"
    nevergrad_algo: str = "TwoPointsDE"
    ts_validation: bool = False
    add_penalty_factor: bool = False
    bootstrap: bool = False
    refresh: bool = False
    convergence: Optional[Any] = None
    ts_validation_plot: Optional[Any] = None
    select_id: Optional[str] = None
    run_time: Optional[float] = None
    seed: Optional[int] = None
    hyper_fixed: bool = False
