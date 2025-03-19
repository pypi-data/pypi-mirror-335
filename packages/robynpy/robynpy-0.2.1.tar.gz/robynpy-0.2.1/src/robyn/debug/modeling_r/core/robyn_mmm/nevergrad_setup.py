from typing import Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class NevergradSetup:
    """Container for Nevergrad optimization setup"""
    iter_total: int
    iter_par: int
    iter_ng: int
    optimizer: Any = None  # nevergrad optimizer instance

def setup_nevergrad(
    hyper_fixed: bool,
    iterations: int,
    cores: int,
    optimizer_name: str,
    hyper_count: int,
    calibration_input: Optional[Dict] = None,
    objective_weights: Optional[Tuple[float, ...]] = None,
    quiet: bool = False
) -> NevergradSetup:
    """
    Setup Nevergrad optimization parameters and optimizer
    
    Args:
        hyper_fixed: Whether hyperparameters are fixed
        iterations: Total number of iterations
        cores: Number of cores for parallel processing
        optimizer_name: Name of Nevergrad optimizer
        hyper_count: Number of hyperparameters
        calibration_input: Optional calibration input data
        objective_weights: Optional weights for objectives
        quiet: Whether to suppress progress output
        
    Returns:
        NevergradSetup object containing optimization parameters
    """
    # Import nevergrad only when needed
    import nevergrad as ng
    
    # Set iterations
    if not hyper_fixed:
        iter_total = iterations
        iter_par = cores
        iter_ng = np.ceil(iterations / cores)  # Sometimes progress bar may not get to 100%
    else:
        iter_total = iter_par = iter_ng = 1

    setup = NevergradSetup(
        iter_total=iter_total,
        iter_par=iter_par,
        iter_ng=iter_ng
    )

    # Start Nevergrad optimizer if not using fixed hyperparameters
    if not hyper_fixed:
        # Set up nevergrad instrumentation
        instrumentation = ng.p.Array(shape=(hyper_count,), lower=0, upper=1)
        setup.optimizer = ng.optimizers.registry[optimizer_name](
            instrumentation, 
            budget=iter_total, 
            num_workers=cores
        )

        # Set multi-objective dimensions for objective functions (errors)
        if calibration_input is None:
            setup.optimizer.tell(ng.p.MultiobjectiveReference(), (1, 1))
            if objective_weights is None:
                objective_weights = (1, 1)
        else:
            setup.optimizer.tell(ng.p.MultiobjectiveReference(), (1, 1, 1))
            if objective_weights is None:
                objective_weights = (1, 1, 1)
                
        setup.optimizer.set_objective_weights(objective_weights)

        # Setup progress bar if needed
        if not quiet:
            from tqdm import tqdm
            setup.pbar = tqdm(total=iter_total, desc="Optimization Progress")

    return setup 