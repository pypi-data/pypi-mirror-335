from dataclasses import dataclass
from typing import Optional, List, Dict
import multiprocessing
import logging
from datetime import datetime

from robyn.data.entities.enums import Models, NevergradAlgorithm
from robyn.debug.modeling_new.data.inputs.featurized_mmm_data import FeaturizedMMMData
from robyn.debug.modeling_new.data.inputs.holidays_data import HolidaysData
from robyn.debug.modeling_new.data.inputs.hyperparameters import Hyperparameters
from robyn.debug.modeling_new.data.inputs.mmmdata import MMMData
from robyn.debug.modeling_new.data.outputs.modeloutputs import ModelOutputs, Trial
from .model_trainer import robyn_train
from robyn.debug.modeling_new.code.convergence import robyn_converge
from robyn.debug.modeling_new.code.validation import ts_validation

@dataclass
class TrialsConfig:
    iterations: int = 2000
    trials: int = 5

class ModelExecutor:
    def __init__(
        self,
        mmmdata: MMMData,
        holidays_data: HolidaysData,
        hyperparameters: Hyperparameters,
        calibration_input: Optional[dict] = None,
        featurized_mmm_data: Optional[FeaturizedMMMData] = None,
    ):
        self.mmmdata = mmmdata
        self.holidays_data = holidays_data
        self.hyperparameters = hyperparameters
        self.calibration_input = calibration_input
        self.featurized_mmm_data = featurized_mmm_data

    def model_run(
        self,
        trials_config: TrialsConfig,
        dt_hyper_fixed: Optional[dict] = None,
        ts_validation: bool = False,
        add_penalty_factor: bool = False,
        rssd_zero_penalty: bool = True,
        cores: int = 8,
        nevergrad_algo: NevergradAlgorithm = NevergradAlgorithm.TWO_POINTS_DE,
        intercept: bool = True,
        intercept_sign: str = "non_negative",
        model_name: Models = Models.RIDGE,
        objective_weights: Optional[List[float]] = None,
        seed: int = 123,
        quiet: bool = False,
        refresh: bool = False,
        outputs: bool = False
    ):
        """
        Main modeling function that runs the MMM optimization process.
        
        Args:
            trials_config: Configuration for number of trials and iterations
            dt_hyper_fixed: Fixed hyperparameters
            ts_validation: Whether to use time series validation
            add_penalty_factor: Whether to add penalty factors to optimization
            rssd_zero_penalty: Whether to penalize models with zero coefficients
            cores: Number of CPU cores to use
            nevergrad_algo: Algorithm to use for optimization
            intercept: Whether to include intercept term
            intercept_sign: Constraint on intercept sign
            model_name: Type of model to use
            objective_weights: Weights for objective function
            seed: Random seed for reproducibility
            quiet: Whether to suppress output
            refresh: Whether to refresh model
            outputs: Whether to return model outputs
            
        Returns:
            Trained model results
        """
        # Input validation
        if not self.hyperparameters:
            raise ValueError("Must provide hyperparameters first")
        
        # Core setup for parallel processing
        max_cores = max(1, multiprocessing.cpu_count())
        if cores > max_cores:
            logging.warning(f"Max possible cores is {max_cores} (requested {cores})")
            cores = max_cores
        cores = max(1, cores)  # Ensure at least 1 core
        
        # Check if hyperparameters are fixed
        hyps_fixed = dt_hyper_fixed is not None
        
        # If hyperparameters are fixed, set trials and iterations to 1
        if hyps_fixed:
            trials_config.trials = 1
            trials_config.iterations = 1
        # Prepare hyperparameters
        hyper_collect = self._prepare_hyperparameters(
            ts_validation=ts_validation,
            add_penalty_factor=add_penalty_factor,
            cores=cores,
            dt_hyper_fixed=dt_hyper_fixed
        )

        # Run model training
        output_models = self._train_model(
            hyper_collect=hyper_collect,
            trials_config=trials_config,
            ts_validation=ts_validation,
            add_penalty_factor=add_penalty_factor,
            rssd_zero_penalty=rssd_zero_penalty,
            cores=cores,
            nevergrad_algo=nevergrad_algo,
            intercept=intercept,
            intercept_sign=intercept_sign,
            model_name=model_name,
            objective_weights=objective_weights,
            seed=seed,
            quiet=quiet,
            refresh=refresh,
            outputs=outputs
        )
        
        # Check convergence and validation when hyperparameters aren't fixed
        if not hyper_collect.all_fixed:
            # Add convergence check results
            output_models.convergence = robyn_converge(output_models)
            
            # Add time series validation plot data
            output_models.ts_validation_plot = ts_validation(output_models)
        else:
            # Handle fixed hyperparameters case
            if dt_hyper_fixed and "solID" in dt_hyper_fixed:
                select_id = dt_hyper_fixed["solID"]
            else:
                # Get solID from first trial's results
                select_id = output_models.trials[0].result_collect.result_hyp_param.solID
            
            output_models.select_id = select_id
            
            if not quiet:
                logging.info(f"Successfully recreated model ID: {select_id}")
        
        return output_models

    def _prepare_hyperparameters(
        self,
        ts_validation: bool,
        add_penalty_factor: bool,
        cores: int,
        dt_hyper_fixed: Optional[dict] = None
    ) -> Hyperparameters:
        """
        Prepare hyperparameters for model training.
        
        Args:
            ts_validation: Whether to use time series validation
            add_penalty_factor: Whether to add penalty factors
            cores: Number of cores for parallel processing
            dt_hyper_fixed: Fixed hyperparameters to use
            
        Returns:
            Updated hyperparameters object
        """
        # Create a copy to avoid modifying original
        hyper_collect = self.hyperparameters.copy()
        
        # Handle fixed hyperparameters if provided
        if dt_hyper_fixed is not None:
            hyper_collect.update_from_fixed(dt_hyper_fixed)
        
        # Update penalty factors if needed
        if add_penalty_factor:
            for channel, params in hyper_collect.hyperparameters.items():
                if params.penalty is None:
                    params.penalty = [True]  # Initialize penalty for optimization
                
        # Update train size if using ts_validation
        if ts_validation and not hyper_collect.all_fixed:
            hyper_collect.update_hyper_bounds()
        
        # Store updated hyperparameters in mmmdata
        self.mmmdata.hyper_updated = hyper_collect.hyper_list_all
        
        return hyper_collect

    def _train_model(
        self,
        hyper_collect: Hyperparameters,
        trials_config: TrialsConfig,
        ts_validation: bool,
        add_penalty_factor: bool,
        rssd_zero_penalty: bool,
        cores: int,
        nevergrad_algo: NevergradAlgorithm,
        intercept: bool,
        intercept_sign: str,
        model_name: Models,
        objective_weights: Optional[List[float]],
        seed: int,
        quiet: bool,
        refresh: bool,
        outputs: bool
    ) -> ModelOutputs:
        """
        Train the MMM model using the specified configuration.
        """
        return robyn_train(
            mmmdata=self.mmmdata,
            hyper_collect=hyper_collect,
            trials_config=trials_config,
            intercept_sign=intercept_sign,
            intercept=intercept,
            nevergrad_algo=nevergrad_algo,
            dt_hyper_fixed=None,  # This should be passed from model_run
            ts_validation=ts_validation,
            add_penalty_factor=add_penalty_factor,
            rssd_zero_penalty=rssd_zero_penalty,
            objective_weights=objective_weights,
            cores=cores,
            refresh=refresh,
            seed=seed,
            quiet=quiet
        )