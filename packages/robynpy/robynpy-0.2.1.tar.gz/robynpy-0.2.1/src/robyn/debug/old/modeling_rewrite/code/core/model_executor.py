# robyn/debug/modeling_rewrite/code/model_executor.py

import datetime
from typing import Optional, Dict, List, Union, Any
import logging

from robyn.debug.modeling_rewrite.code.types.config_types import TrialsConfig
from robyn.debug.modeling_rewrite.code.core.model_trainer import ModelTrainer
from robyn.debug.modeling_rewrite.data.inputs.mmmdata import MMMData
from robyn.debug.modeling_rewrite.data.inputs.holidays_data import HolidaysData
from robyn.debug.modeling_rewrite.data.inputs.hyperparameters import Hyperparameters
from robyn.debug.modeling_rewrite.data.inputs.featurized_mmm_data import FeaturizedMMMData
from robyn.debug.modeling_rewrite.data.outputs.modeloutputs import ModelOutputs, Trial
from typing import Optional, Dict, Any
import multiprocessing
from typing import Optional, List

from robyn.debug.modeling_rewrite.code.hyperparameters.hyper_collector import HyperCollector, HyperCollectorOutput


logger = logging.getLogger(__name__)

class ModelExecutor:
    def __init__(
        self,
        raw_input_collect: Dict[str, Any],
    ):
        """
        Initialize with raw R InputCollect format
        
        Args:
            raw_input_collect: Raw R InputCollect dictionary containing all model inputs
        """
        self.input_collect = raw_input_collect
        
        # Quick validation of critical fields
        critical_fields = ["dt_mod", "hyperparameters", "dep_var", "paid_media_vars"]
        missing = [f for f in critical_fields if f not in raw_input_collect]
        if missing:
            raise ValueError(f"Missing critical fields in raw_input_collect: {missing}")

    def model_run(
        self,
        trials_config: TrialsConfig,
        ts_validation: bool = False,
        add_penalty_factor: bool = False,
        rssd_zero_penalty: bool = True,
        cores: Optional[int] = None,
        nevergrad_algo: str = "TwoPointsDE",
        intercept: bool = True,
        intercept_sign: str = "non_negative",
        model_name: str = "ridge",
        quiet: bool = False,
        seed: int = 123,
        **kwargs
    ) -> ModelOutputs:
        """Run MMM model training using raw InputCollect format"""
        start_time = datetime.now()
        
        if not quiet:
            self._print_input_summary()
        
        trials = []
        for trial in range(trials_config.trials):
            trainer = ModelTrainer(
                input_collect=self.input_collect,
                trial_seed=seed + trial
            )
            
            result = trainer.train(
                iterations=trials_config.iterations,
                ts_validation=ts_validation,
                add_penalty_factor=add_penalty_factor,
                rssd_zero_penalty=rssd_zero_penalty,
                nevergrad_algo=nevergrad_algo,
                intercept=intercept,
                intercept_sign=intercept_sign,
                model_name=model_name,
                quiet=quiet
            )
            
            trials.append(Trial(result_collect=result))
            
            if not quiet:
                logger.info(f"Completed trial {trial + 1}/{trials_config.trials}")
        
        output = ModelOutputs(trials=trials)
        output.run_time = round((datetime.now() - start_time).total_seconds() / 60.0, 2)
        
        if not quiet:
            logger.info(f"Total run time: {output.run_time} mins")
            
        return output

    def _print_input_summary(self):
        """Print summary of input data similar to R's init_msgs_run"""
        logger.info(
            f"Input data has {len(self.input_collect['dt_mod'])} "
            f"{self.input_collect['intervalType']}s in total: "
            f"{min(self.input_collect['dt_mod']['ds'])} to "
            f"{max(self.input_collect['dt_mod']['ds'])}"
        )