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
        mmm_data: MMMData,
        holidays_data: HolidaysData,
        hyperparameters: Hyperparameters,
        calibration_input: Optional[Any] = None,
        featurized_mmm_data: Optional[FeaturizedMMMData] = None,
    ):
        self.mmm_data = mmm_data
        self.holidays_data = holidays_data
        self.hyperparameters = hyperparameters
        self.calibration_input = calibration_input
        self.featurized_mmm_data = featurized_mmm_data

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
        """
        Run MMM model training
        
        Args:
            trials_config: Configuration for trials and iterations
            ts_validation: Whether to use time series validation
            add_penalty_factor: Add penalty factor to hyperparameters
            rssd_zero_penalty: Apply zero penalty to RSSD
            cores: Number of cores for parallel processing
            nevergrad_algo: Nevergrad algorithm to use
            intercept: Whether to include intercept
            intercept_sign: Sign constraint for intercept
            model_name: Type of model to use
            quiet: Suppress logging
            seed: Random seed
            
        Returns:
            Model training outputs
        """
        start_time = datetime.datetime.now()
        
        trials = []
        for trial in range(trials_config.trials):
            trainer = ModelTrainer(
                mmm_data=self.mmm_data,
                holidays_data=self.holidays_data,
                hyperparameters=self.hyperparameters,
                calibration_input=self.calibration_input,
                featurized_mmm_data=self.featurized_mmm_data
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
                seed=seed + trial,
                quiet=quiet
            )
            
            trials.append(Trial(result_collect=result))
            
            if not quiet:
                logger.info(f"Completed trial {trial + 1}/{trials_config.trials}")
        
        output = ModelOutputs(
            trials=trials,
            hyper_bound_ng=self.hyperparameters.hyper_bound_ng,
            hyper_bound_fixed=self.hyperparameters.hyper_bound_fixed,
            hyper_updated=self.hyperparameters.hyper_updated
        )
        
        run_time = (datetime.datetime.now() - start_time).total_seconds() / 60.0
        output.run_time = round(run_time, 2)
        
        if not quiet and trials_config.iterations > 1:
            logger.info(f"Total run time: {output.run_time} mins")
            
        return output