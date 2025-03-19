import pandas as pd
import numpy as np
import sys

sys.path.append("/Users/yijuilee/robynpy_release_reviews/Robyn/python/src")
from robyn.modeling.ridge.ridge_data_builder import RidgeDataBuilder
from robyn.data.entities.mmmdata import MMMData
from robyn.data.entities.enums import AdstockType
from robyn.data.entities.holidays_data import HolidaysData
from robyn.modeling.feature_engineering import FeatureEngineering


def setup_test_data():
    # 1. Load simulated data
    dt_simulated_weekly = pd.read_csv(
        "/Users/yijuilee/robynpy_release_reviews/Robyn/python/src/robyn/tutorials/resources/dt_simulated_weekly.csv"
    )
    dt_prophet_holidays = pd.read_csv(
        "/Users/yijuilee/robynpy_release_reviews/Robyn/python/src/robyn/tutorials/resources/dt_prophet_holidays.csv"
    )

    # 2. Setup MMMData
    mmm_data_spec = MMMData.MMMDataSpec(
        dep_var="revenue",
        dep_var_type="revenue",
        date_var="DATE",
        context_vars=["competitor_sales_B", "events"],
        factor_vars=["events"],
        paid_media_spends=["tv_S", "ooh_S", "print_S", "facebook_S", "search_S"],
        paid_media_vars=["tv_S", "ooh_S", "print_S", "facebook_I", "search_clicks_P"],
        organic_vars=["newsletter"],
        window_start="2016-01-01",
        window_end="2018-12-31",
    )
    mmm_data = MMMData(data=dt_simulated_weekly, mmmdata_spec=mmm_data_spec)

    # 3. Setup hyperparameters exactly from R debug log
    hyperparameters = {
        "facebook_S_alphas": 2.1377,
        "facebook_S_gammas": 0.4236,
        "facebook_S_thetas": 0.1237,
        "newsletter_alphas": 1.7219,
        "newsletter_gammas": 0.6612,
        "newsletter_thetas": 0.279,
        "ooh_S_alphas": 1.9042,
        "ooh_S_gammas": 0.5971,
        "ooh_S_thetas": 0.2413,
        "print_S_alphas": 1.4685,
        "print_S_gammas": 0.505,
        "print_S_thetas": 0.277,
        "search_S_alphas": 0.9416,
        "search_S_gammas": 0.6003,
        "search_S_thetas": 0.116,
        "tv_S_alphas": 1.2399,
        "tv_S_gammas": 0.7889,
        "tv_S_thetas": 0.5454,
        "train_size": 0.6856,
        "lambda": 0.501,
    }

    # 4. Setup holidays data
    holidays_data = HolidaysData(
        dt_holidays=dt_prophet_holidays,
        prophet_vars=["trend", "season", "holiday"],
        prophet_country="DE",
        prophet_signs=["default", "default", "default"],
    )

    # 5. Run feature engineering
    feature_engineering = FeatureEngineering(mmm_data, hyperparameters, holidays_data)
    featurized_mmm_data = feature_engineering.perform_feature_engineering()

    return mmm_data, featurized_mmm_data, hyperparameters


def test_run_transformations():
    # 1. Get data from feature engineering
    mmm_data, featurized_mmm_data, hyperparameters = setup_test_data()

    # 2. Create RidgeDataBuilder instance
    ridge_builder = RidgeDataBuilder(mmm_data, featurized_mmm_data)

    # 3. Run transformations
    result = ridge_builder.run_transformations(
        hyperparameters, current_iteration=1, total_iterations=5, cores=9
    )

    # 4. Print comparison stats
    print("\ndt_modSaturated stats:")
    print("Shape:", result["dt_modSaturated"].shape)
    print("Columns:", result["dt_modSaturated"].columns.tolist())
    print("Min values:", result["dt_modSaturated"].min())
    print("Max values:", result["dt_modSaturated"].max())

    print("\ndt_saturatedImmediate stats:")
    print("Shape:", result["dt_saturatedImmediate"].shape)
    print("Columns:", result["dt_saturatedImmediate"].columns.tolist())
    print("Min values:", result["dt_saturatedImmediate"].min())
    print("Max values:", result["dt_saturatedImmediate"].max())

    print("\ndt_saturatedCarryover stats:")
    print("Shape:", result["dt_saturatedCarryover"].shape)
    print("Columns:", result["dt_saturatedCarryover"].columns.tolist())
    print("Min values:", result["dt_saturatedCarryover"].min())
    print("Max values:", result["dt_saturatedCarryover"].max())


if __name__ == "__main__":
    test_run_transformations()
