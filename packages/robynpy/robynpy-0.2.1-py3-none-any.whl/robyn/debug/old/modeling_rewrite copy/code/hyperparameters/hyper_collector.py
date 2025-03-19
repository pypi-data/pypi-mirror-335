# robyn/debug/modeling_rewrite/hyperparameters/hyper_collector.py

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import pandas as pd
import logging
from robyn.debug.modeling_rewrite.data.inputs.hyperparameters import Hyperparameters
from typing import List, Optional
import itertools
from robyn.debug.modeling_rewrite.code.constants import AdstockOptions, HYPS_NAMES, HYPS_OTHERS
from robyn.debug.modeling_rewrite.code.utils.hyper_utils import check_hyper_fixed, get_hyper_names

logger = logging.getLogger(__name__)

@dataclass
class HyperCollectorOutput:
    hyper_list_all: Dict[str, Any]
    hyper_bound_list_updated: Dict[str, List[float]]
    hyper_bound_list_fixed: Dict[str, float]
    dt_hyper_fixed_mod: pd.DataFrame
    all_fixed: bool

class HyperCollector:
    def __init__(
        self,
        input_collect: Any,  # Need to know the type
        hyper_in: Hyperparameters,
        ts_validation: bool,
        add_penalty_factor: bool,
        dt_hyper_fixed: Optional[Dict] = None,
        cores: int = 1
    ):
        self.input_collect = input_collect
        self.hyper_in = hyper_in
        self.ts_validation = ts_validation
        self.add_penalty_factor = add_penalty_factor
        self.dt_hyper_fixed = dt_hyper_fixed
        self.cores = cores

    def collect(self) -> HyperCollectorOutput:
        # Get hyperparameter names
        hyp_param_sam_name = get_hyper_names(
            adstock=self.input_collect.adstock,
            all_media=self.input_collect.all_media,
            all_vars=self.input_collect.dt_mod.columns.drop(['ds', 'dep_var']).tolist()
        )
        
        # Add standard hyperparameters
        hyp_param_sam_name.extend(self.HYPS_OTHERS)  # Need to define this constant
        
        # Check fixed status and validate
        all_fixed, hyp_param_sam_name = check_hyper_fixed(
            self.input_collect,
            self.dt_hyper_fixed,
            self.add_penalty_factor
        )
        hyp_param_sam_name = self._update_hyper_param_names(hyp_param_sam_name)

        if not all_fixed:
            # Handle non-fixed hyperparameters case
            hyper_bound_list = self._collect_media_hyperparameters(hyp_param_sam_name)
            hyper_bound_list = self._add_lambda_hyperparameter(hyper_bound_list)
            hyper_bound_list = self._handle_train_size(hyper_bound_list)
            
            if self.add_penalty_factor:
                hyper_bound_list = self._add_penalty_factors(hyper_bound_list)
                
            results = self._process_hyper_bounds(hyper_bound_list, hyp_param_sam_name)
        else:
            # Handle fixed hyperparameters case
            results = self._process_fixed_hyperparameters(hyp_param_sam_name)

        return HyperCollectorOutput(**results)

    def _collect_media_hyperparameters(self, param_names: List[str]) -> Dict:
        hyper_bound_list = {}
        for name in param_names:
            if name in self.hyper_in:
                hyper_bound_list[name] = self.hyper_in[name]
        return hyper_bound_list

    def _add_lambda_hyperparameter(self, hyper_bound_list: Dict) -> Dict:
        if "lambda" not in hyper_bound_list:
            hyper_bound_list["lambda"] = [0.0, 1.0]
        return hyper_bound_list

    def _handle_train_size(self, hyper_bound_list: Dict) -> Dict:
        if self.ts_validation:
            if "train_size" not in hyper_bound_list:
                hyper_bound_list["train_size"] = [0.5, 0.8]
            logger.info(
                f"Time-series validation with train_size range of "
                f"{hyper_bound_list['train_size'][0]*100}%-{hyper_bound_list['train_size'][1]*100}% "
                f"of the data..."
            )
        else:
            if "train_size" in hyper_bound_list:
                logger.warning("Provided train_size but ts_validation = FALSE. Time series validation inactive.")
            hyper_bound_list["train_size"] = 1
            logger.info("Fitting time series with all available data...")
        return hyper_bound_list