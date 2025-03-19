# pyre-strict

import warnings
import numpy as np
import pandas as pd
from typing import List, Optional, Dict, Any, Tuple
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_squared_error
import nevergrad as ng
from tqdm import tqdm
from robyn.calibration.media_effect_calibration import MediaEffectCalibrator
import logging
import time
from datetime import datetime
from robyn.modeling.convergence.convergence import Convergence
from sklearn.exceptions import ConvergenceWarning
from robyn.data.entities.calibration_input import CalibrationInput
from robyn.data.entities.holidays_data import HolidaysData
from robyn.data.entities.hyperparameters import Hyperparameters
from robyn.data.entities.mmmdata import MMMData
from robyn.modeling.entities.modeloutputs import ModelOutputs, Trial
from robyn.modeling.entities.modelrun_trials_config import TrialsConfig
from robyn.modeling.entities.model_refit_output import ModelRefitOutput
from robyn.modeling.feature_engineering import FeaturizedMMMData
from robyn.modeling.entities.enums import NevergradAlgorithm


class RidgeModelBuilder:
    def __init__(
        self,
        mmm_data: MMMData,
        holiday_data: HolidaysData,
        calibration_input: CalibrationInput,
        hyperparameters: Hyperparameters,
        featurized_mmm_data: FeaturizedMMMData,
    ):
        self.mmm_data = mmm_data
        self.holiday_data = holiday_data
        self.calibration_input = calibration_input
        self.hyperparameters = hyperparameters
        self.featurized_mmm_data = featurized_mmm_data
        self.logger = logging.getLogger(__name__)

    def build_models(
        self,
        trials_config: TrialsConfig,
        dt_hyper_fixed: Optional[pd.DataFrame] = None,
        ts_validation: bool = False,
        add_penalty_factor: bool = False,
        seed: List[int] = [123],
        rssd_zero_penalty: bool = True,
        objective_weights: Optional[List[float]] = None,
        nevergrad_algo: NevergradAlgorithm = NevergradAlgorithm.TWO_POINTS_DE,
        intercept: bool = True,
        intercept_sign: str = "non_negative",
        cores: Optional[int] = None,
    ) -> ModelOutputs:
        start_time = time.time()
        # Initialize hyperparameters with flattened structure
        hyper_collect = self._hyper_collector(
            self.hyperparameters,
            ts_validation,
            add_penalty_factor,
            dt_hyper_fixed,
            cores,
        )
        # Convert datetime to string format matching R's format
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Set up objective weights including calibration if available
        if objective_weights is None:
            if self.calibration_input is not None:
                objective_weights = [1 / 3, 1 / 3, 1 / 3]  # NRMSE, RSSD, MAPE
            else:
                objective_weights = [0.5, 0.5]  # NRMSE, RSSD only
        # Run trials
        trials = []
        for trial in range(1, trials_config.trials + 1):
            trial_result = self._run_nevergrad_optimization(
                hyper_collect=hyper_collect,
                iterations=trials_config.iterations,
                cores=cores,
                nevergrad_algo=nevergrad_algo,
                intercept=intercept,
                intercept_sign=intercept_sign,
                ts_validation=ts_validation,
                add_penalty_factor=add_penalty_factor,
                objective_weights=objective_weights,
                dt_hyper_fixed=dt_hyper_fixed,
                rssd_zero_penalty=rssd_zero_penalty,
                trial=trial,
                seed=seed[0] + trial,  # Use the first element of the seed list
                total_trials=trials_config.trials,
            )
            trials.append(trial_result)
        # Calculate convergence
        convergence = Convergence()
        convergence_results = convergence.calculate_convergence(trials)

        # Aggregate results with explicit type casting
        all_result_hyp_param = pd.concat(
            [trial.result_hyp_param for trial in trials], ignore_index=True
        )
        all_result_hyp_param = self.safe_astype(
            all_result_hyp_param,
            {
                "sol_id": "str",
                "trial": "int64",
                "iterNG": "int64",
                "iterPar": "int64",
                "nrmse": "float64",
                "decomp.rssd": "float64",
                "mape": "int64",
                "pos": "int64",
                "lambda": "float64",
                "lambda_hp": "float64",
                "lambda_max": "float64",
                "lambda_min_ratio": "float64",
                "rsq_train": "float64",
                "rsq_val": "float64",
                "rsq_test": "float64",
                "nrmse_train": "float64",
                "nrmse_val": "float64",
                "nrmse_test": "float64",
                "ElapsedAccum": "float64",
                "Elapsed": "float64",
            },
        )

        all_x_decomp_agg = pd.concat(
            [trial.x_decomp_agg for trial in trials], ignore_index=True
        )
        all_x_decomp_agg = self.safe_astype(
            all_x_decomp_agg,
            {
                "rn": "str",
                "coef": "float64",
                "xDecompAgg": "float64",
                "xDecompPerc": "float64",
                "xDecompMeanNon0": "float64",
                "xDecompMeanNon0Perc": "float64",
                "xDecompAggRF": "float64",
                "xDecompPercRF": "float64",
                "xDecompMeanNon0RF": "float64",
                "xDecompMeanNon0PercRF": "float64",
                "sol_id": "str",
                "pos": "bool",
                "mape": "int64",
            },
        )

        all_decomp_spend_dist = pd.concat(
            [
                trial.decomp_spend_dist
                for trial in trials
                if trial.decomp_spend_dist is not None
            ],
            ignore_index=True,
        )
        all_decomp_spend_dist = self.safe_astype(
            all_decomp_spend_dist,
            {
                "rn": "str",
                "coef": "float64",
                "total_spend": "float64",
                "mean_spend": "float64",
                "effect_share": "float64",
                "spend_share": "float64",
                "xDecompAgg": "float64",
                "xDecompPerc": "float64",
                "xDecompMeanNon0": "float64",
                "xDecompMeanNon0Perc": "float64",
                "sol_id": "str",
                "pos": "bool",
                "mape": "int64",
                "nrmse": "float64",
                "decomp.rssd": "float64",
                "trial": "int64",
                "iterNG": "int64",
                "iterPar": "int64",
            },
        )
        # Convert hyper_bound_ng from dict to DataFrame
        hyper_bound_ng_df = pd.DataFrame()
        for param_name, bounds in hyper_collect["hyper_bound_list_updated"].items():
            hyper_bound_ng_df.loc[0, param_name] = bounds[0]
            hyper_bound_ng_df[param_name] = hyper_bound_ng_df[param_name].astype(
                "float64"
            )
        if "lambda" in hyper_bound_ng_df.columns:
            hyper_bound_ng_df["lambda"] = hyper_bound_ng_df["lambda"].astype("int64")
        # Create ModelOutputs
        model_outputs = ModelOutputs(
            trials=trials,
            train_timestamp=current_time,
            cores=cores,
            iterations=trials_config.iterations,
            intercept=intercept,
            intercept_sign=intercept_sign,
            nevergrad_algo=nevergrad_algo,
            ts_validation=ts_validation,
            add_penalty_factor=add_penalty_factor,
            hyper_updated=hyper_collect["hyper_list_all"],
            hyper_fixed=hyper_collect["all_fixed"],
            convergence=convergence_results,
            select_id=self._select_best_model(trials),
            seed=seed,
            hyper_bound_ng=hyper_bound_ng_df,
            hyper_bound_fixed=hyper_collect["hyper_bound_list_fixed"],
            ts_validation_plot=None,
            all_result_hyp_param=all_result_hyp_param,
            all_x_decomp_agg=all_x_decomp_agg,
            all_decomp_spend_dist=all_decomp_spend_dist,
        )

        return model_outputs

    def _select_best_model(self, output_models: List[Trial]) -> str:
        # Extract relevant metrics
        nrmse_values = np.array([trial.nrmse for trial in output_models])
        decomp_rssd_values = np.array([trial.decomp_rssd for trial in output_models])

        # Normalize the metrics
        nrmse_norm = (nrmse_values - np.min(nrmse_values)) / (
            np.max(nrmse_values) - np.min(nrmse_values)
        )
        decomp_rssd_norm = (decomp_rssd_values - np.min(decomp_rssd_values)) / (
            np.max(decomp_rssd_values) - np.min(decomp_rssd_values)
        )

        # Calculate the combined score (assuming equal weights)
        combined_score = nrmse_norm + decomp_rssd_norm

        # Find the index of the best model (lowest combined score)
        best_index = np.argmin(combined_score)

        # Return the sol_id of the best model (changed from solID)
        return output_models[best_index].result_hyp_param["sol_id"].values[0]

    def _model_train(
        self,
        hyper_collect: Dict[str, Any],
        trials_config: TrialsConfig,
        intercept_sign: str,
        intercept: bool,
        nevergrad_algo: NevergradAlgorithm,
        dt_hyper_fixed: Optional[pd.DataFrame],
        ts_validation: bool,
        add_penalty_factor: bool,
        objective_weights: Optional[List[float]],
        rssd_zero_penalty: bool,
        seed: int,
        cores: int,
    ) -> List[Trial]:
        trials = []
        for trial in range(1, trials_config.trials + 1):
            trial_result = self._run_nevergrad_optimization(
                hyper_collect,
                trials_config.iterations,
                cores,
                nevergrad_algo,
                intercept,
                intercept_sign,
                ts_validation,
                add_penalty_factor,
                objective_weights,
                dt_hyper_fixed,
                rssd_zero_penalty,
                trial,
                seed + trial,
                trials_config.trials,
            )

            trials.append(trial_result)
        return trials

    def _run_nevergrad_optimization(
        self,
        hyper_collect: Dict[str, Any],
        iterations: int,
        cores: int,
        nevergrad_algo: NevergradAlgorithm,
        intercept: bool,
        intercept_sign: str,
        ts_validation: bool,
        add_penalty_factor: bool,
        objective_weights: Optional[List[float]],
        dt_hyper_fixed: Optional[pd.DataFrame],
        rssd_zero_penalty: bool,
        trial: int,
        seed: int,
        total_trials: int,
    ) -> Trial:
        warnings.filterwarnings("ignore", category=ConvergenceWarning)
        warnings.filterwarnings("ignore", category=RuntimeWarning)

        np.random.seed(seed)

        param_names = list(hyper_collect["hyper_bound_list_updated"].keys())
        param_bounds = [
            hyper_collect["hyper_bound_list_updated"][name] for name in param_names
        ]

        instrum_dict = {
            name: ng.p.Scalar(lower=bound[0], upper=bound[1])
            for name, bound in zip(param_names, param_bounds)
        }

        instrum = ng.p.Instrumentation(**instrum_dict)
        optimizer = ng.optimizers.registry[nevergrad_algo.value](
            instrum, budget=iterations, num_workers=cores
        )

        all_results = []
        start_time = time.time()

        with tqdm(
            total=iterations,
            desc=f"Running trial {trial} of total {total_trials} trials",
            bar_format="{l_bar}{bar}",
            ncols=75,
        ) as pbar:
            for iter_ng in range(iterations):
                candidate = optimizer.ask()
                params = candidate.kwargs

                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result = self._evaluate_model(
                        params,
                        ts_validation,
                        add_penalty_factor,
                        rssd_zero_penalty,
                        objective_weights,
                        start_time=start_time,
                        iter_ng=iter_ng,
                        trial=trial,
                    )

                optimizer.tell(candidate, result["loss"])

                # Important: Convert metrics to correct types
                sol_id = f"{trial}_{iter_ng + 1}_1"
                result["params"].update(
                    {
                        "sol_id": sol_id,
                        "ElapsedAccum": result["elapsed_accum"],
                        "trial": int(trial),
                        "rsq_train": float(result["rsq_train"]),
                        "rsq_val": float(result["rsq_val"]),
                        "rsq_test": float(result["rsq_test"]),
                        "nrmse": float(result["nrmse"]),
                        "nrmse_train": float(result["nrmse_train"]),
                        "nrmse_val": float(result["nrmse_val"]),
                        "nrmse_test": float(result["nrmse_test"]),
                        "decomp.rssd": float(result["decomp_rssd"]),
                        "mape": float(result["mape"]),
                        "lambda": float(
                            result["lambda"]
                        ),  # Critical: Using lambda not lambda_
                        "lambda_hp": float(result["lambda_hp"]),
                        "lambda_max": float(result["lambda_max"]),
                        "lambda_min_ratio": float(result["lambda_min_ratio"]),
                        "iterNG": int(iter_ng + 1),
                        "iterPar": 1,
                    }
                )

                all_results.append(result)
                pbar.update(1)

        end_time = time.time()
        self.logger.info(f" Finished in {(end_time - start_time) / 60:.2f} mins")

        # Aggregate results with explicit dtypes
        result_hyp_param = pd.DataFrame([r["params"] for r in all_results]).astype(
            {
                "sol_id": "str",
                "trial": "int64",
                "iterNG": "int64",
                "iterPar": "int64",
                "nrmse": "float64",
                "decomp.rssd": "float64",
                "mape": "float64",
                "lambda": "float64",
                "lambda_hp": "float64",
                "lambda_max": "float64",
                "lambda_min_ratio": "float64",
                "rsq_train": "float64",
                "rsq_val": "float64",
                "rsq_test": "float64",
            }
        )

        decomp_spend_dist = pd.concat(
            [r["decomp_spend_dist"] for r in all_results], ignore_index=True
        )
        x_decomp_agg = pd.concat(
            [r["x_decomp_agg"] for r in all_results], ignore_index=True
        )

        # Ensure correct dtypes in decomp_spend_dist and x_decomp_agg
        decomp_spend_dist = decomp_spend_dist.astype(
            {
                "rn": "str",
                "coef": "float64",
                "total_spend": "float64",
                "mean_spend": "float64",
                "effect_share": "float64",
                "spend_share": "float64",
                "sol_id": "str",
            }
        )

        x_decomp_agg = x_decomp_agg.astype(
            {
                "rn": "str",
                "coef": "float64",
                "xDecompAgg": "float64",
                "xDecompPerc": "float64",
                "sol_id": "str",
            }
        )

        # Find best result based on loss
        best_result = min(all_results, key=lambda x: x["loss"])
        # Convert values to Series before passing to Trial
        return Trial(
            result_hyp_param=result_hyp_param,
            lift_calibration=best_result.get("lift_calibration", pd.DataFrame()),
            decomp_spend_dist=decomp_spend_dist,
            x_decomp_agg=x_decomp_agg,
            nrmse=pd.Series([float(best_result["nrmse"])]),
            decomp_rssd=pd.Series([float(best_result["decomp_rssd"])]),
            mape=pd.Series([int(best_result["mape"])]),  # Cast to int
            rsq_train=pd.Series([float(best_result["rsq_train"])]),
            rsq_val=pd.Series([float(best_result["rsq_val"])]),
            rsq_test=pd.Series([float(best_result["rsq_test"])]),
            lambda_=pd.Series([float(best_result["lambda"])]),
            lambda_hp=pd.Series([float(best_result["lambda_hp"])]),
            lambda_max=pd.Series([float(best_result["lambda_max"])]),
            lambda_min_ratio=pd.Series([float(best_result["lambda_min_ratio"])]),
            pos=pd.Series([int(best_result.get("pos", 0))]),  # Cast to int
            elapsed=pd.Series([float(best_result["elapsed"])]),
            elapsed_accum=pd.Series([float(best_result["elapsed_accum"])]),
            trial=pd.Series([int(trial)]),
            iter_ng=pd.Series([int(best_result["iter_ng"])]),
            iter_par=pd.Series([int(best_result["iter_par"])]),
            train_size=pd.Series([float(best_result["params"].get("train_size", 1.0))]),
            sol_id=str(best_result["params"]["sol_id"]),
        )

    @staticmethod
    def safe_astype(df: pd.DataFrame, type_dict: Dict[str, str]) -> pd.DataFrame:
        """Only cast columns that exist in the DataFrame"""
        existing_cols = {
            col: dtype for col, dtype in type_dict.items() if col in df.columns
        }
        return df.astype(existing_cols) if existing_cols else df

    def _prepare_data(self, params: Dict[str, float]) -> Tuple[pd.DataFrame, pd.Series]:
        # Get the dependent variable
        # Check if 'dep_var' is in columns
        if "dep_var" in self.featurized_mmm_data.dt_mod.columns:
            # Rename 'dep_var' to the specified value
            self.featurized_mmm_data.dt_mod = self.featurized_mmm_data.dt_mod.rename(
                columns={"dep_var": self.mmm_data.mmmdata_spec.dep_var}
            )
        y = self.featurized_mmm_data.dt_mod[self.mmm_data.mmmdata_spec.dep_var]

        # Select all columns except the dependent variable
        X = self.featurized_mmm_data.dt_mod.drop(
            columns=[self.mmm_data.mmmdata_spec.dep_var]
        )

        # Convert date columns to numeric (number of days since the earliest date)
        date_columns = X.select_dtypes(include=["datetime64", "object"]).columns
        for col in date_columns:
            X[col] = pd.to_datetime(X[col], errors="coerce", format="%Y-%m-%d")
            # Fill NaT (Not a Time) values with a default date (e.g., the minimum date in the column)
            min_date = X[col].min()
            X[col] = X[col].fillna(min_date)
            # Convert to days since minimum date, handling potential NaT values
            X[col] = (
                (X[col] - min_date).dt.total_seconds().div(86400).fillna(0).astype(int)
            )

        # One-hot encode categorical variables
        categorical_columns = X.select_dtypes(include=["object", "category"]).columns
        X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)

        # Ensure all columns are numeric
        X = X.select_dtypes(include=[np.number])

        # Apply transformations based on hyperparameters
        for media in self.mmm_data.mmmdata_spec.paid_media_spends:
            if f"{media}_thetas" in params:
                X[media] = self._geometric_adstock(X[media], params[f"{media}_thetas"])
            if f"{media}_alphas" in params and f"{media}_gammas" in params:
                X[media] = self._hill_transformation(
                    X[media], params[f"{media}_alphas"], params[f"{media}_gammas"]
                )

        # Handle any remaining NaN or infinite values
        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        y = y.replace([np.inf, -np.inf], np.nan).fillna(y.mean())
        X = X + 1e-8 * np.random.randn(*X.shape)

        return X, y

    def _geometric_adstock(self, x: pd.Series, theta: float) -> pd.Series:
        # print(f"Before adstock: {x.head()}")
        y = x.copy()
        for i in range(1, len(x)):
            y.iloc[i] += theta * y.iloc[i - 1]
        # print(f"After adstock: {y.head()}")
        return y

    def _hill_transformation(
        self, x: pd.Series, alpha: float, gamma: float
    ) -> pd.Series:
        # Add debug self.logger.debugs
        # print(f"Before hill: {x.head()}")
        x_scaled = (x - x.min()) / (x.max() - x.min())
        result = x_scaled**alpha / (x_scaled**alpha + gamma**alpha)
        # print(f"After hill: {result.head()}")
        return result

    def _calculate_rssd(
        self,
        model: Ridge,
        X: pd.DataFrame,
        paid_media_cols: List[str],
        rssd_zero_penalty: bool,
    ) -> float:
        """Calculate RSSD exactly like R's implementation"""
        print(f"\nRSSD Calculation Debug:")
        print(f"Paid media columns: {paid_media_cols}")

        total_spend = np.abs(X[paid_media_cols].sum()).sum()
        effects = []
        spends = []

        print(f"Effect calculations per channel:")
        for col in paid_media_cols:
            idx = list(X.columns).index(col)
            coef = model.coef_[idx]
            spend = np.abs(X[col].sum())
            effect = coef * spend
            effects.append(effect)
            spends.append(spend)
            print(f"{col}: coef={coef:.6f}, spend={spend:.6f}, effect={effect:.6f}")

        effects = np.array(effects)
        spends = np.array(spends)

        # Calculate normalized effects and spends
        total_effect = np.sum(np.abs(effects))
        print(f"Totals - spend: {total_spend:.6f}, effect: {total_effect:.6f}")

        if total_effect > 0 and total_spend > 0:
            effects_norm = np.abs(effects) / total_effect
            spends_norm = spends / total_spend
            print(f"Normalized values:")
            print(f"Effects: {effects_norm}")
            print(f"Spends: {spends_norm}")

            rssd = np.sqrt(np.mean((effects_norm - spends_norm) ** 2))

            if rssd_zero_penalty:
                zero_effects = sum(1 for e in effects if abs(e) < 1e-10)
                if zero_effects > 0:
                    rssd_original = rssd
                    rssd *= 1 + zero_effects / len(effects)
                    print(f"Applied zero penalty: {zero_effects} zero effects found")
                    print(f"RSSD adjusted from {rssd_original:.6f} to {rssd:.6f}")

            print(f"Final RSSD: {rssd:.6f}")
            return float(rssd)

        print("RSSD calculation returned infinity")
        return float(np.inf)

    def _calculate_mape(
        self,
        model: Ridge,
        dt_raw: pd.DataFrame,
        hypParamSam: Dict[str, float],
        wind_start: int,
        wind_end: int,
    ) -> float:
        """
        Calculate MAPE using calibration data
        """
        if self.calibration_input is None:
            return 0.0

        try:
            # Use the MediaEffectCalibrator for MAPE calculation
            calibration_engine = MediaEffectCalibrator(
                mmm_data=self.mmm_data,
                hyperparameters=self.hyperparameters,
                calibration_input=self.calibration_input,
            )

            # Calculate MAPE using calibration engine
            lift_collect = calibration_engine.calibrate(
                df_raw=dt_raw,
                hypParamSam=hypParamSam,
                wind_start=wind_start,
                wind_end=wind_end,
                dayInterval=1,  # Default to 1 if not specified
                adstock=self.hyperparameters.adstock,
            )

            # Return mean MAPE across all lift studies
            if lift_collect is not None and not lift_collect.empty:
                return float(lift_collect["mape_lift"].mean())
            return 0.0
        except Exception as e:
            self.logger.warning(f"Error calculating MAPE: {str(e)}")
            return 0.0

    def _calculate_x_decomp_agg(
        self, model: Ridge, X: pd.DataFrame, y: pd.Series, metrics: Dict[str, Any]
    ) -> pd.DataFrame:
        """Calculate x decomposition aggregates matching R's implementation exactly"""
        # Calculate decomposition effects
        x_decomp = X * model.coef_
        x_decomp_sum = x_decomp.sum().sum()

        results = []
        for col in X.columns:
            coef = model.coef_[list(X.columns).index(col)]
            decomp_values = x_decomp[col]
            decomp_sum = decomp_values.sum()

            # Handle non-zero values
            non_zero_values = decomp_values[decomp_values > 0]
            non_zero_mean = non_zero_values.mean() if len(non_zero_values) > 0 else 0

            # Calculate total non-zero means across all columns
            total_non_zero_mean = sum(
                [
                    x_decomp[c][x_decomp[c] > 0].mean() if any(x_decomp[c] > 0) else 0
                    for c in X.columns
                ]
            )

            result = {
                "rn": str(col),  # Ensure string type
                "coef": float(coef),  # Ensure float type
                "xDecompAgg": float(decomp_sum),  # Ensure float type
                "xDecompPerc": float(
                    decomp_sum / x_decomp_sum if x_decomp_sum != 0 else 0
                ),
                "xDecompMeanNon0": float(non_zero_mean),
                "xDecompMeanNon0Perc": float(
                    non_zero_mean / total_non_zero_mean
                    if total_non_zero_mean != 0
                    else 0
                ),
                "xDecompAggRF": float(decomp_sum),  # RF version
                "xDecompPercRF": float(
                    decomp_sum / x_decomp_sum if x_decomp_sum != 0 else 0
                ),
                "xDecompMeanNon0RF": float(non_zero_mean),
                "xDecompMeanNon0PercRF": float(
                    non_zero_mean / total_non_zero_mean
                    if total_non_zero_mean != 0
                    else 0
                ),
                "pos": bool(coef >= 0),
            }

            # Add model performance metrics with correct types
            result.update(
                {
                    "train_size": float(metrics.get("train_size", 1.0)),
                    "rsq_train": float(metrics.get("rsq_train", 0)),
                    "rsq_val": float(metrics.get("rsq_val", 0)),
                    "rsq_test": float(metrics.get("rsq_test", 0)),
                    "nrmse_train": float(metrics.get("nrmse_train", 0)),
                    "nrmse_val": float(metrics.get("nrmse_val", 0)),
                    "nrmse_test": float(metrics.get("nrmse_test", 0)),
                    "nrmse": float(metrics.get("nrmse", 0)),
                    "decomp.rssd": float(metrics.get("decomp_rssd", 0)),
                    "mape": float(metrics.get("mape", 0)),
                    "lambda": float(
                        metrics.get("lambda", 0)
                    ),  # Critical: Using lambda not lambda_
                    "lambda_hp": float(metrics.get("lambda_hp", 0)),
                    "lambda_max": float(metrics.get("lambda_max", 0)),
                    "lambda_min_ratio": float(metrics.get("lambda_min_ratio", 0)),
                    "sol_id": str(metrics.get("sol_id", "")),
                    "trial": int(metrics.get("trial", 0)),
                    "iterNG": int(metrics.get("iterNG", 0)),
                    "iterPar": int(metrics.get("iterPar", 0)),
                    "Elapsed": float(metrics.get("Elapsed", 0)),
                }
            )

            results.append(result)

        df = pd.DataFrame(results)

        # Ensure correct column order and types
        required_cols = [
            "rn",
            "coef",
            "xDecompAgg",
            "xDecompPerc",
            "xDecompMeanNon0",
            "xDecompMeanNon0Perc",
            "xDecompAggRF",
            "xDecompPercRF",
            "xDecompMeanNon0RF",
            "xDecompMeanNon0PercRF",
            "pos",
            "train_size",
            "rsq_train",
            "rsq_val",
            "rsq_test",
            "nrmse_train",
            "nrmse_val",
            "nrmse_test",
            "nrmse",
            "decomp.rssd",
            "mape",
            "lambda",
            "lambda_hp",
            "lambda_max",
            "lambda_min_ratio",
            "sol_id",
            "trial",
            "iterNG",
            "iterPar",
            "Elapsed",
        ]

        df = df[required_cols]
        return df

    def _format_hyperparameter_names(
        self, params: Dict[str, float]
    ) -> Dict[str, float]:
        """Format hyperparameter names to match R's naming convention."""
        formatted = {}
        for param_name, value in params.items():
            if param_name == "lambda" or param_name == "train_size":
                formatted[param_name] = value
            else:
                # Split parameter name into media and param type
                # E.g., facebook_S_alphas -> (facebook_S, alphas)
                media, param_type = param_name.rsplit("_", 1)
                if param_type in ["alphas", "gammas", "thetas", "shapes", "scales"]:
                    formatted[f"{media}_{param_type}"] = value
                else:
                    formatted[param_name] = value
        return formatted

    @staticmethod
    def _hyper_collector(
        hyperparameters: Dict[str, Any],
        ts_validation: bool,
        add_penalty_factor: bool,
        dt_hyper_fixed: Optional[pd.DataFrame],
        cores: Optional[int],
    ) -> Dict[str, Any]:
        """
        Collect and organize hyperparameters to match R's structure
        """
        logger = logging.getLogger(__name__)
        logger.info("Collecting hyperparameters for optimization...")
        prepared_hyperparameters = hyperparameters["prepared_hyperparameters"]
        hyper_collect = {
            "hyper_list_all": {},
            "hyper_bound_list_updated": {},
            "hyper_bound_list_fixed": {},
            "all_fixed": False,
        }

        # Adjust hyper_list_all to store lists
        for channel, channel_params in prepared_hyperparameters.hyperparameters.items():
            for param in ["thetas", "alphas", "gammas"]:
                param_value = getattr(channel_params, param, None)
                if param_value is not None:
                    if isinstance(param_value, list) and len(param_value) == 2:
                        param_key = f"{channel}_{param}"
                        hyper_collect["hyper_bound_list_updated"][
                            param_key
                        ] = param_value
                        hyper_collect["hyper_list_all"][
                            f"{channel}_{param}"
                        ] = param_value  # Store as list
                    elif not isinstance(param_value, list):
                        hyper_collect["hyper_bound_list_fixed"][
                            f"{channel}_{param}"
                        ] = param_value
                        hyper_collect["hyper_list_all"][f"{channel}_{param}"] = [
                            param_value,
                            param_value,
                        ]  # Store as list
        # Handle lambda parameter similarly
        if (
            isinstance(prepared_hyperparameters.lambda_, list)
            and len(prepared_hyperparameters.lambda_) == 2
        ):
            hyper_collect["hyper_bound_list_updated"][
                "lambda"
            ] = prepared_hyperparameters.lambda_
            hyper_collect["hyper_list_all"]["lambda"] = prepared_hyperparameters.lambda_
        else:
            hyper_collect["hyper_bound_list_fixed"][
                "lambda"
            ] = prepared_hyperparameters.lambda_
            hyper_collect["hyper_list_all"]["lambda"] = [
                prepared_hyperparameters.lambda_,
                prepared_hyperparameters.lambda_,
            ]
        # Handle train_size similarly
        if ts_validation:
            if (
                isinstance(prepared_hyperparameters.train_size, list)
                and len(prepared_hyperparameters.train_size) == 2
            ):
                hyper_collect["hyper_bound_list_updated"][
                    "train_size"
                ] = prepared_hyperparameters.train_size
                hyper_collect["hyper_list_all"][
                    "train_size"
                ] = prepared_hyperparameters.train_size
            else:
                train_size = [0.5, 0.8]
                hyper_collect["hyper_bound_list_updated"]["train_size"] = train_size
                hyper_collect["hyper_list_all"]["train_size"] = train_size
        else:
            hyper_collect["hyper_list_all"]["train_size"] = [1.0, 1.0]
        return hyper_collect

    @staticmethod
    def _model_refit(
        x_train: np.ndarray,
        y_train: np.ndarray,
        x_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        x_test: Optional[np.ndarray] = None,
        y_test: Optional[np.ndarray] = None,
        lambda_: float = 1.0,
        lower_limits: Optional[List[float]] = None,
        upper_limits: Optional[List[float]] = None,
        intercept: bool = True,
        intercept_sign: str = "non_negative",
    ) -> ModelRefitOutput:
        model = Ridge(alpha=lambda_, fit_intercept=intercept)
        model.fit(x_train, y_train)

        y_train_pred = model.predict(x_train)
        y_val_pred = model.predict(x_val) if x_val is not None else None
        y_test_pred = model.predict(x_test) if x_test is not None else None

        rsq_train = r2_score(y_train, y_train_pred)
        rsq_val = r2_score(y_val, y_val_pred) if y_val is not None else None
        rsq_test = r2_score(y_test, y_test_pred) if y_test is not None else None

        nrmse_train = np.sqrt(np.mean((y_train - y_train_pred) ** 2)) / (
            np.max(y_train) - np.min(y_train)
        )
        nrmse_val = (
            np.sqrt(np.mean((y_val - y_val_pred) ** 2))
            / (np.max(y_val) - np.min(y_val))
            if y_val is not None
            else None
        )
        nrmse_test = (
            np.sqrt(np.mean((y_test - y_test_pred) ** 2))
            / (np.max(y_test) - np.min(y_test))
            if y_test is not None
            else None
        )

        return ModelRefitOutput(
            rsq_train=rsq_train,
            rsq_val=rsq_val,
            rsq_test=rsq_test,
            nrmse_train=nrmse_train,
            nrmse_val=nrmse_val,
            nrmse_test=nrmse_test,
            coefs=model.coef_,
            y_train_pred=y_train_pred,
            y_val_pred=y_val_pred,
            y_test_pred=y_test_pred,
            y_pred=(
                np.concatenate([y_train_pred, y_val_pred, y_test_pred])
                if y_val is not None and y_test is not None
                else y_train_pred
            ),
            mod=model,
            df_int=1 if intercept else 0,
        )

    def _r_scale(self, x: np.ndarray) -> np.ndarray:
        """Implement R's scaling exactly"""
        x_mean = np.mean(x, axis=0)
        # R-style scaling (using n not n-1 in denominator)
        x_sd = np.sqrt(np.sum((x - x_mean) ** 2, axis=0) / x.shape[0])
        # Handle zero sd case
        x_sd[x_sd == 0] = 1
        return (x - x_mean) / x_sd

    def _lambda_seq(
        self, x: pd.DataFrame, y: pd.Series, seq_len: int = 100
    ) -> np.ndarray:
        """Calculate lambda sequence exactly matching R's glmnet implementation"""
        x_np = x.to_numpy()
        y_np = y.to_numpy()
        n = len(y_np)

        # R's stdization uses n (not n-1) in denominator
        def r_scale(x: np.ndarray) -> np.ndarray:
            mu = np.mean(x)
            sigma = np.sqrt(np.sum((x - mu) ** 2) / len(x))  # R-style sd
            return (x - mu) / (sigma if sigma > 0 else 1)

        # Scale x and y like R
        x_scaled = np.column_stack([r_scale(x_np[:, j]) for j in range(x_np.shape[1])])
        y_scaled = r_scale(y_np)

        # R's glmnet lambda calculation
        alpha = 0.001  # Ridge regression default
        dot_prod = np.abs(x_norm.T @ y_norm)
        lambda_max = np.max(dot_prod) / (alpha * len(y_norm))
        lambda_min_ratio = 0.0001

        # Generate sequence with exact R spacing
        log_lambda = np.linspace(
            np.log(lambda_max), np.log(lambda_max * lambda_min_ratio), seq_len
        )
        return np.exp(log_lambda)

    def calculate_r2_score(
        self, y_true: np.ndarray, y_pred: np.ndarray, n_features: int, df_int: int = 1
    ) -> float:
        """Match R's R² calculation exactly"""
        n = len(y_true)
        y_mean = np.mean(y_true)

        # Calculate SS exactly like R
        ss_tot = np.sum((y_true - y_mean) ** 2)
        ss_res = np.sum((y_true - y_pred) ** 2)

        # Calculate unadjusted R²
        r2 = 1 - (ss_res / ss_tot)

        # Apply R's adjustment formula
        adj_r2 = 1 - ((1 - r2) * (n - df_int) / (n - n_features - df_int))

        # Handle negative values like R
        if adj_r2 < 0:
            adj_r2 = -abs(adj_r2)

        return float(adj_r2)

    def calculate_nrmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Match R's NRMSE calculation exactly"""
        n = len(y_true)
        rss = np.sum((y_true - y_pred) ** 2)
        scale = np.max(y_true) - np.min(y_true)

        if scale > 0:
            nrmse = np.sqrt(rss / n) / scale
        else:
            nrmse = np.sqrt(rss / n)

        return float(nrmse)

    def _evaluate_model(
        self,
        params: Dict[str, float],
        ts_validation: bool,
        add_penalty_factor: bool,
        rssd_zero_penalty: bool,
        objective_weights: Optional[List[float]],
        start_time: float,
        iter_ng: int,
        trial: int,
    ) -> Dict[str, Any]:
        """Evaluate model with parameter set matching R's implementation exactly"""
        X, y = self._prepare_data(params)
        sol_id = f"{trial}_{iter_ng + 1}_1"
        # After preparing data
        print(f"Data shapes - X: {X.shape}, y: {y.shape}")
        print(f"Sample of X values: {X.head()}")
        print(f"Sample of y values: {y.head()}")

        # Split data using R's approach
        train_size = params.get("train_size", 1.0) if ts_validation else 1.0
        train_idx = int(len(X) * train_size)

        metrics = {}
        if ts_validation:
            val_test_size = (len(X) - train_idx) // 2
            X_train = X.iloc[:train_idx]
            y_train = y.iloc[:train_idx]
            X_val = X.iloc[train_idx : train_idx + val_test_size]
            y_val = y.iloc[train_idx : train_idx + val_test_size]
            X_test = X.iloc[train_idx + val_test_size :]
            y_test = y.iloc[train_idx + val_test_size :]
        else:
            X_train, y_train = X, y
            X_val = X_test = y_val = y_test = None

        x_norm = X_train.to_numpy()
        y_norm = y_train.to_numpy()

        # Calculate lambda using R-matching helper function
        lambda_hp = params.get("lambda", 1.0)
        lambda_, lambda_max = self._calculate_lambda(x_norm, y_norm, lambda_hp)
        # After calculating lambda
        print(f"Lambda calculation debug:")
        print(f"lambda_hp: {lambda_hp}")
        print(f"lambda_: {lambda_}")
        print(f"lambda_max: {lambda_max}")

        # Scale inputs for model
        model = Ridge(alpha=lambda_ / len(x_norm), fit_intercept=True)
        model.fit(x_norm, y_norm)

        # Calculate metrics using R-style calculations
        y_train_pred = model.predict(x_norm)
        metrics["rsq_train"] = self.calculate_r2_score(
            y_norm, y_train_pred, x_norm.shape[1]
        )
        metrics["nrmse_train"] = self.calculate_nrmse(y_norm, y_train_pred)

        # Validation and test metrics
        if ts_validation and X_val is not None and X_test is not None:
            y_val_pred = model.predict(X_val)
            y_test_pred = model.predict(X_test)

            metrics["rsq_val"] = self.calculate_r2_score(
                y_val, y_val_pred, X_val.shape[1]
            )
            metrics["nrmse_val"] = self.calculate_nrmse(y_val, y_val_pred)

            metrics["rsq_test"] = self.calculate_r2_score(
                y_test, y_test_pred, X_test.shape[1]
            )
            metrics["nrmse_test"] = self.calculate_nrmse(y_test, y_test_pred)

            metrics["nrmse"] = metrics["nrmse_val"]
        else:
            metrics["rsq_val"] = metrics["rsq_test"] = 0.0
            metrics["nrmse_val"] = metrics["nrmse_test"] = 0.0
            metrics["nrmse"] = metrics["nrmse_train"]

        # Calculate RSSD
        paid_media_cols = [
            col
            for col in X.columns
            if col in self.mmm_data.mmmdata_spec.paid_media_spends
        ]
        decomp_rssd = self._calculate_rssd(
            model, X_train, paid_media_cols, rssd_zero_penalty
        )

        elapsed_time = time.time() - start_time

        # Format hyperparameter names to match R's format
        params_formatted = self._format_hyperparameter_names(params)

        # Update metrics dictionary
        metrics.update(
            {
                "decomp_rssd": float(decomp_rssd),
                "lambda": float(lambda_),
                "lambda_hp": float(lambda_hp),
                "lambda_max": float(lambda_max),
                "lambda_min_ratio": float(0.0001),
                "mape": int(0),  # Cast to int as in R
                "sol_id": str(sol_id),
                "trial": int(trial),
                "iterNG": int(iter_ng + 1),
                "iterPar": int(1),
                "Elapsed": float(elapsed_time),
                "elapsed": float(elapsed_time),
                "elapsed_accum": float(elapsed_time),
            }
        )

        # Calculate decompositions
        x_decomp_agg = self._calculate_x_decomp_agg(
            model, X_train, y_train, {**params_formatted, **metrics}
        )
        decomp_spend_dist = self._calculate_decomp_spend_dist(
            model, X_train, y_train, {**metrics, "params": params_formatted}
        )

        # Calculate loss
        loss = (
            objective_weights[0] * metrics["nrmse"]
            + objective_weights[1] * metrics["decomp_rssd"]
            + (
                objective_weights[2] * metrics["mape"]
                if len(objective_weights) > 2
                else 0
            )
        )
        print(f"Model coefficients range: {model.coef_.min()} to {model.coef_.max()}")
        print(f"Sample predictions: {y_train_pred[:5]}")
        print(f"Sample actual values: {y_norm[:5]}")
        return {
            "loss": loss,
            "params": params_formatted,
            **metrics,
            "decomp_spend_dist": decomp_spend_dist,
            "x_decomp_agg": x_decomp_agg,
            "elapsed": elapsed_time,
            "elapsed_accum": elapsed_time,
            "iter_ng": iter_ng + 1,
            "iter_par": 1,
        }

    # Updated _calculate_decomp_spend_dist method
    def _calculate_decomp_spend_dist(
        self, model: Ridge, X: pd.DataFrame, y: pd.Series, metrics: Dict[str, float]
    ) -> pd.DataFrame:
        """Calculate decomposition spend distribution matching R's implementation exactly."""
        paid_media_cols = [
            col
            for col in X.columns
            if col in self.mmm_data.mmmdata_spec.paid_media_spends
        ]

        # First pass to calculate total spend and effect for normalization
        total_media_spend = np.abs(X[paid_media_cols].sum().sum())
        all_effects = {}
        all_spends = {}

        for col in paid_media_cols:
            idx = list(X.columns).index(col)
            coef = model.coef_[idx]
            spend = np.abs(X[col].sum())  # Ensure positive spend
            effect = coef * spend  # Keep original sign for effect
            all_effects[col] = effect
            all_spends[col] = spend

        total_effect = np.sum(
            np.abs([e for e in all_effects.values()])
        )  # Use absolute sum

        # Second pass to calculate normalized metrics
        results = []
        for col in paid_media_cols:
            idx = list(X.columns).index(col)
            coef = float(model.coef_[idx])
            spend = float(np.abs(all_spends[col]))
            effect = float(all_effects[col])

            # Handle non-zero values properly
            non_zero_mask = X[col] != 0
            non_zero_effect = X[col][non_zero_mask] * coef
            non_zero_mean = float(
                non_zero_effect.mean() if len(non_zero_effect) > 0 else 0
            )

            # Calculate normalized shares
            spend_share = (
                float(spend / total_media_spend) if total_media_spend > 0 else 0
            )
            effect_share = (
                float(np.abs(effect) / total_effect) if total_effect > 0 else 0
            )

            result = {
                "rn": str(col),
                "coef": float(coef),
                "xDecompAgg": float(effect),
                "total_spend": float(spend),
                "mean_spend": float(np.abs(X[col].mean())),
                "spend_share": spend_share,
                "effect_share": effect_share,
                "xDecompPerc": effect_share,
                "xDecompMeanNon0": non_zero_mean,
                "xDecompMeanNon0Perc": float(
                    non_zero_mean
                    / sum(
                        [
                            all_effects[c] / X[c][X[c] != 0].size
                            for c in paid_media_cols
                            if any(X[c] != 0)
                        ]
                    )
                    if any(X[c][X[c] != 0].size > 0 for c in paid_media_cols)
                    else 0
                ),
                "pos": bool(coef >= 0),
                "sol_id": str(metrics.get("sol_id", "")),
            }

            # Add model performance metrics
            for metric_key in [
                "rsq_train",
                "rsq_val",
                "rsq_test",
                "nrmse",
                "decomp_rssd",
                "mape",
                "lambda",
                "lambda_hp",
                "lambda_max",
                "lambda_min_ratio",
            ]:
                result[metric_key] = float(metrics.get(metric_key, 0))

            result.update(
                {
                    "trial": int(metrics.get("trial", 0)),
                    "iterNG": int(metrics.get("iterNG", 0)),
                    "iterPar": int(metrics.get("iterPar", 0)),
                    "Elapsed": float(metrics.get("elapsed", 0)),
                }
            )

            results.append(result)

        df = pd.DataFrame(results)

        # Ensure correct column order
        required_cols = [
            "rn",
            "coef",
            "xDecompAgg",
            "total_spend",
            "mean_spend",
            "spend_share",
            "effect_share",
            "xDecompPerc",
            "xDecompMeanNon0",
            "xDecompMeanNon0Perc",
            "pos",
            "sol_id",
            "rsq_train",
            "rsq_val",
            "rsq_test",
            "nrmse",
            "decomp_rssd",
            "mape",
            "lambda",
            "lambda_hp",
            "lambda_max",
            "lambda_min_ratio",
            "trial",
            "iterNG",
            "iterPar",
            "Elapsed",
        ]
        print(f"Decomp spend distribution debug:")
        print(f"Total media spend: {total_media_spend}")
        print(f"Total effect: {total_effect}")
        for col in paid_media_cols:
            print(f"{col} - effect: {all_effects[col]}, spend: {all_spends[col]}")
        return df[required_cols]

    def _calculate_lambda(
        self, x_norm: np.ndarray, y_norm: np.ndarray, lambda_hp: float
    ) -> Tuple[float, float]:
        """Match R's glmnet lambda calculation exactly"""
        n_samples = len(y_norm)
        print(f"\nLambda Calculation Debug:")
        print(f"Input shapes - x_norm: {x_norm.shape}, y_norm: {y_norm.shape}")

        # R's standardization
        mysd = lambda x: np.sqrt(np.sum((x - np.mean(x)) ** 2) / len(x))
        x_mean = np.mean(x_norm, axis=0)
        y_mean = np.mean(y_norm)
        print(f"Means - x: {x_mean[:5]}..., y: {y_mean}")

        x_scaled = np.apply_along_axis(
            lambda col: (col - np.mean(col)) / mysd(col), 0, x_norm
        )
        y_scaled = (y_norm - y_mean) / mysd(y_norm)
        print(f"Scaled data samples - x: {x_scaled[:5,0]}..., y: {y_scaled[:5]}...")

        # Handle NaN values like R
        x_scaled[np.isnan(x_scaled)] = 0

        # R's lambda calculation
        alpha = 0.001  # Ridge regression default
        lambda_max = np.max(np.abs(x_scaled.T @ y_scaled)) * n_samples / alpha
        lambda_min_ratio = 0.0001

        # Calculate final lambda
        lambda_ = lambda_min_ratio * lambda_max + lambda_hp * (
            lambda_max - lambda_min_ratio * lambda_max
        )

        print(
            f"Lambda values - lambda_max: {lambda_max}, lambda_: {lambda_}, lambda_hp: {lambda_hp}"
        )
        return lambda_, lambda_max
