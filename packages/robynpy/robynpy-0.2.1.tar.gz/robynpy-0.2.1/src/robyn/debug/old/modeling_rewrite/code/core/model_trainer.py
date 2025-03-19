# robyn/debug/modeling_rewrite/core/model_trainer.py

from typing import Optional, Dict, Any, List
import logging
from robyn.debug.modeling_rewrite.data.inputs.mmmdata import MMMData 
from robyn.debug.modeling_rewrite.code.hyperparameters.hyper_collector import HyperCollectorOutput
from robyn.debug.modeling_rewrite.data.inputs.holidays_data import HolidaysData
from robyn.debug.modeling_rewrite.data.inputs.hyperparameters import Hyperparameters
from robyn.debug.modeling_rewrite.data.inputs.featurized_mmm_data import FeaturizedMMMData
from robyn.debug.modeling_rewrite.code.core.mmm import RobynMMM  # We'll need to create this

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(
        self,
        mmm_data: MMMData,  # Note: it's mmm_data, not mmmdata
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
        self.mmm_model = RobynMMM()

    def train(
        self,
        input_collect: MMMData,
        hyper_collect: HyperCollectorOutput,
        cores: int,
        iterations: int,
        trials: int,
        intercept_sign: str,
        intercept: bool,
        nevergrad_algo: str,
        dt_hyper_fixed: Optional[Dict] = None,
        ts_validation: bool = True,
        add_penalty_factor: bool = False,
        rssd_zero_penalty: bool = True,
        objective_weights: Optional[List[float]] = None,
        refresh: bool = False,
        seed: int = 123,
        quiet: bool = False,
        model_name: str = "ridge"
    ):
        # Check if hyperparameters are fixed
        hyper_fixed = hyper_collect.all_fixed

        if hyper_fixed:
            # Handle fixed hyperparameters case
            output_models = self._train_fixed_hyperparameters(
                input_collect=input_collect,
                hyper_collect=hyper_collect,
                iterations=iterations,
                cores=cores,
                nevergrad_algo=nevergrad_algo,
                intercept=intercept,
                intercept_sign=intercept_sign,
                dt_hyper_fixed=dt_hyper_fixed,
                ts_validation=ts_validation,
                add_penalty_factor=add_penalty_factor,
                rssd_zero_penalty=rssd_zero_penalty,
                objective_weights=objective_weights,
                seed=seed,
                quiet=quiet
            )
        else:
            # Handle non-fixed hyperparameters case
            output_models = self._train_multiple_trials(
                input_collect=input_collect,
                hyper_collect=hyper_collect,
                iterations=iterations,
                cores=cores,
                trials=trials,
                nevergrad_algo=nevergrad_algo,
                intercept=intercept,
                intercept_sign=intercept_sign,
                ts_validation=ts_validation,
                add_penalty_factor=add_penalty_factor,
                rssd_zero_penalty=rssd_zero_penalty,
                objective_weights=objective_weights,
                refresh=refresh,
                seed=seed,
                quiet=quiet
            )

        return output_models

    def _train_fixed_hyperparameters(self, input_collect, hyper_collect, **kwargs):
        # Run single model with fixed hyperparameters
        model_output = self.mmm_model.run(
            input_collect=input_collect,
            hyper_collect=hyper_collect,
            **kwargs
        )
        
        # Set trial number
        model_output.trial = 1

        # Update solID if provided in dt_hyper_fixed
        dt_hyper_fixed = kwargs.get('dt_hyper_fixed')
        if dt_hyper_fixed is not None and "solID" in dt_hyper_fixed:
            for table in ["result_hyp_param", "x_decomp_vec", "x_decomp_agg"]:
                if hasattr(model_output.result_collect, table):
                    getattr(model_output.result_collect, table)["solID"] = dt_hyper_fixed["solID"]

        return {"trial1": model_output}

    def _train_multiple_trials(self, input_collect, hyper_collect, trials, **kwargs):
        if not kwargs.get('quiet', False):
            calibration_status = "with calibration using" if input_collect.calibration_input else "using"
            logger.info(
                f">>> Starting {trials} trials with {kwargs['iterations']} iterations each "
                f"{calibration_status} {kwargs['nevergrad_algo']} nevergrad algorithm..."
            )

        output_models = {}
        
        for trial_num in range(1, trials + 1):
            if not kwargs.get('quiet', False):
                logger.info(f"Running trial {trial_num} of {trials}")

            # Run single trial
            model_output = self._run_single_trial(
                input_collect=input_collect,
                hyper_collect=hyper_collect,
                trial_num=trial_num,
                **kwargs
            )

            output_models[f"trial{trial_num}"] = model_output

        return output_models

    def _run_single_trial(self, input_collect, hyper_collect, trial_num, **kwargs):
        # Increment seed for each trial
        local_seed = kwargs['seed'] + trial_num
        
        # Run model for this trial
        model_output = self.mmm_model.run(
            input_collect=input_collect,
            hyper_collect=hyper_collect,
            trial=trial_num,
            seed=local_seed,
            **kwargs
        )

        # Check for zero coefficients
        self._check_zero_coefficients(model_output, kwargs.get('iterations'), kwargs.get('quiet', False))
        
        model_output["trial"] = trial_num
        return model_output

    def _check_zero_coefficients(self, model_output, iterations, quiet):
        if hasattr(model_output, 'result_collect') and hasattr(model_output.result_collect, 'result_hyp_param'):
            decomp_rssd = model_output.result_collect.result_hyp_param.get('decomp.rssd', [])
            zero_coef_models = sum(1 for x in decomp_rssd if x == float('inf'))
            
            if zero_coef_models > 0:
                zero_coef_models = min(zero_coef_models, iterations)
                if not quiet:
                    logger.warning(
                        f"This trial contains {zero_coef_models} iterations with all media coefficient = 0.\n"
                        "Please reconsider your media variable choice if the pareto choices are unreasonable.\n"
                        "Recommendations:\n"
                        "1. Increase hyperparameter ranges for 0-coef channels to give Robyn more freedom\n"
                        "2. Split media into sub-channels, and/or aggregate similar channels, and/or introduce other media\n"
                        "3. Increase trials to get more samples"
                    )