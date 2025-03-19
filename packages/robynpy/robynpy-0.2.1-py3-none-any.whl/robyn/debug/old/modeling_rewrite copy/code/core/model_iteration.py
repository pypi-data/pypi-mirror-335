# robyn/debug/modeling_rewrite/core/model_iteration.py

import time
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, Any
from sklearn.preprocessing import OneHotEncoder

from robyn.debug.modeling_rewrite.core.transformations import run_transformations
from robyn.debug.modeling_rewrite.utils.validation import check_adstock

class ModelIteration:
    def __init__(self):
        self.encoder = OneHotEncoder(sparse=False)
        
    def run_iteration(
        self,
        i: int,
        hyper_param_sam_ng: pd.DataFrame,
        env: Any,  # Replace with proper type
        **kwargs
    ) -> Dict[str, Any]:
        """Run a single model iteration"""
        start_time = time.time()
        
        # Get hyperparameter sample
        hyper_param_sam = hyper_param_sam_ng.iloc[i]
        adstock = check_adstock(env.adstock)
        
        # Transform media
        transformed = run_transformations(
            all_media=env.all_media,
            window_start_loc=env.rolling_window_start_which,
            window_end_loc=env.rolling_window_end_which,
            dt_mod=env.dt_mod,
            adstock=adstock,
            dt_hyppar=hyper_param_sam,
            **kwargs
        )
        
        # Prepare training data
        x_train, x_val, x_test, y_train, y_val, y_test = self._prepare_training_data(
            transformed.dt_modSaturated,
            hyper_param_sam['train_size']
        )
        
        # Get model constraints
        lower_limits, upper_limits = self._get_model_constraints(
            x_train=x_train,
            env=env,
            dt_window=transformed.dt_modSaturated
        )
        
        return {
            'x_train': x_train,
            'x_val': x_val,
            'x_test': x_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'lower_limits': lower_limits,
            'upper_limits': upper_limits,
            'transformed': transformed
        }
    
    def _prepare_training_data(
        self,
        dt_window: pd.DataFrame,
        train_size: float
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray], 
               np.ndarray, Optional[np.ndarray], Optional[np.ndarray]]:
        """Prepare train/val/test splits with one-hot encoding"""
        
        # Get target and features
        y_window = dt_window['dep_var'].values
        x_window = self._one_hot_encode(dt_window.drop('dep_var', axis=1))
        
        # Initialize variables
        y_train = y_val = y_test = y_window
        x_train = x_val = x_test = x_window
        
        # Split data if train_size < 1
        if train_size < 1:
            n_samples = len(dt_window)
            val_size = test_size = (1 - train_size) / 2
            
            train_idx = int(np.floor(n_samples * train_size))
            val_idx = train_idx + int(np.floor(n_samples * val_size))
            
            # Split features
            x_train = x_window[:train_idx]
            x_val = x_window[train_idx:val_idx]
            x_test = x_window[val_idx:]
            
            # Split target
            y_train = y_window[:train_idx]
            y_val = y_window[train_idx:val_idx]
            y_test = y_window[val_idx:]
        else:
            x_val = x_test = y_val = y_test = None
            
        return x_train, x_val, x_test, y_train, y_val, y_test
    
    def _one_hot_encode(self, df: pd.DataFrame) -> np.ndarray:
        """One-hot encode categorical variables"""
        return self.encoder.fit_transform(df)
        
    def _get_model_constraints(
        self,
        x_train: np.ndarray,
        env: Any,
        dt_window: pd.DataFrame
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Get model constraints for ridge regression"""
        
        # Combine all signs
        x_sign = {
            **dict(zip(env.prophet_vars, env.prophet_signs)),
            **dict(zip(env.context_vars, env.context_signs)),
            **dict(zip(env.paid_media_selected, env.paid_media_signs)),
            **dict(zip(env.organic_vars, env.organic_signs))
        }
        
        # Initialize limits
        lower_limits = np.zeros(len(env.prophet_signs))
        upper_limits = np.ones(len(env.prophet_signs))
        
        # Handle trend
        trend_loc = np.where(self.encoder.get_feature_names() == 'trend')[0]
        if len(trend_loc) > 0 and np.sum(x_train[:, trend_loc]) < 0:
            trend_prophet_loc = env.prophet_vars.index('trend')
            lower_limits[trend_prophet_loc] = -1
            upper_limits[trend_prophet_loc] = 0
            
        # Handle other variables
        for col, sign in x_sign.items():
            if col in dt_window.columns and dt_window[col].dtype == 'category':
                n_levels = len(dt_window[col].unique())
                if n_levels <= 1:
                    raise ValueError(f"Factor variable {col} must have more than 1 level")
                    
                # Set limits based on sign
                if sign == 'positive':
                    lower_limits = np.append(lower_limits, [0] * (n_levels - 1))
                    upper_limits = np.append(upper_limits, [np.inf] * (n_levels - 1))
                elif sign == 'negative':
                    lower_limits = np.append(lower_limits, [-np.inf] * (n_levels - 1))
                    upper_limits = np.append(upper_limits, [0] * (n_levels - 1))
            else:
                lower_limits = np.append(lower_limits, 0 if sign == 'positive' else -np.inf)
                upper_limits = np.append(upper_limits, 0 if sign == 'negative' else np.inf)
                
        return lower_limits, upper_limits