import logging
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import numpy as np


class RidgeDataBuilder:
    def __init__(self, mmm_data, featurized_mmm_data):
        self.mmm_data = mmm_data
        self.featurized_mmm_data = featurized_mmm_data
        self.logger = logging.getLogger(__name__)

    def _prepare_data(self, params: Dict[str, float]) -> Tuple[pd.DataFrame, pd.Series]:
        print("\nridge_data_builder prepare_data:")
        print(
            f"Window indices: {self.mmm_data.mmmdata_spec.rolling_window_start_which} to {self.mmm_data.mmmdata_spec.rolling_window_end_which}"
        )
        print(
            f"Full data shape before windowing: {self.featurized_mmm_data.dt_mod.shape}"
        )

        # Apply window indices
        start_idx = self.mmm_data.mmmdata_spec.rolling_window_start_which
        end_idx = self.mmm_data.mmmdata_spec.rolling_window_end_which

        # Window the data first
        windowed_data = self.featurized_mmm_data.dt_mod.iloc[
            start_idx : end_idx + 1
        ].copy()
        print(f"Data shape after windowing: {windowed_data.shape}")

        # Get the dependent variable from windowed data
        if "dep_var" in windowed_data.columns:
            windowed_data = windowed_data.rename(
                columns={"dep_var": self.mmm_data.mmmdata_spec.dep_var}
            )
        y = windowed_data[self.mmm_data.mmmdata_spec.dep_var]

        # Select all columns except the dependent variable
        X = windowed_data.drop(columns=[self.mmm_data.mmmdata_spec.dep_var])

        # Rest of your existing code...
        date_columns = X.select_dtypes(include=["datetime64", "object"]).columns
        for col in date_columns:
            X[col] = pd.to_datetime(X[col], errors="coerce", format="%Y-%m-%d")
            min_date = X[col].min()
            X[col] = X[col].fillna(min_date)
            X[col] = (
                (X[col] - min_date).dt.total_seconds().div(86400).fillna(0).astype(int)
            )

        categorical_columns = X.select_dtypes(include=["object", "category"]).columns
        X = pd.get_dummies(X, columns=categorical_columns, drop_first=True)
        X = X.select_dtypes(include=[np.number])

        for media in self.mmm_data.mmmdata_spec.paid_media_spends:
            if f"{media}_thetas" in params:
                X[media] = self._geometric_adstock(X[media], params[f"{media}_thetas"])
            if f"{media}_alphas" in params and f"{media}_gammas" in params:
                X[media] = self._hill_transformation(
                    X[media], params[f"{media}_alphas"], params[f"{media}_gammas"]
                )

        X = X.replace([np.inf, -np.inf], np.nan).fillna(0)
        y = y.replace([np.inf, -np.inf], np.nan).fillna(y.mean())
        X = X + 1e-8 * np.random.randn(*X.shape)

        if "ds" in X.columns:
            X = X.drop(columns=["ds"])

        print(f"Final data shapes - X: {X.shape}, y: {y.shape}")
        return X, y

    @staticmethod
    def safe_astype(df: pd.DataFrame, type_dict: Dict[str, str]) -> pd.DataFrame:
        """Only cast columns that exist in the DataFrame"""
        existing_cols = {
            col: dtype for col, dtype in type_dict.items() if col in df.columns
        }
        return df.astype(existing_cols) if existing_cols else df

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

    def _geometric_adstock(self, x: pd.Series, theta: float) -> pd.Series:
        y = x.copy()
        for i in range(1, len(x)):
            y.iloc[i] += theta * y.iloc[i - 1]
        return y

    def _hill_transformation(
        self, x: pd.Series, alpha: float, gamma: float
    ) -> pd.Series:

        x_scaled = (x - x.min()) / (x.max() - x.min())
        result = x_scaled**alpha / (x_scaled**alpha + gamma**alpha)

        return result
