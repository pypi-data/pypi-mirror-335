from typing import Dict, Any

def check_init_msg(input_collect: Dict[str, Any], cores: int) -> None:
    """
    Print initialization message about hyperparameters and computation setup.
    
    Args:
        input_collect: Dictionary containing model input parameters
        cores: Number of CPU cores to use
    """
    # Count parameters to optimize and fixed parameters
    opt_count = sum(1 for params in input_collect['hyper_updated'].values() if len(params) == 2)
    fix_count = sum(1 for params in input_collect['hyper_updated'].values() if len(params) == 1)
    
    details = f"({opt_count} to iterate + {fix_count} fixed)"
    base_msg = (
        f"Using {input_collect['adstock']} adstocking with "
        f"{len(input_collect['hyper_updated'])} hyperparameters {details}"
    )
    
    if cores == 1:
        print(f"{base_msg} with no parallel computation")
    else:
        print(f"{base_msg} on {cores} cores")