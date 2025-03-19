import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
import time
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
from rpy2.robjects.conversion import localconverter

import os
import sys

sys.path.append("/Users/yijuilee/robynpy_release_reviews/Robyn/python/src")

# Import our custom rpy2 ridge model implementation
from robyn.modeling.ridge.models.ridge_utils import create_ridge_model_rpy2

# Enable automatic conversion between NumPy and R
numpy2ri.activate()

# Set random seed for reproducibility
np.random.seed(42)
ro.r("set.seed(42)")  # Also set seed in R


def test_rpy2_ridge_modeling():
    print("Testing Ridge model with rpy2 integration")

    # Generate synthetic data (same as in test_sklearn.py)
    n_samples = 100
    n_features = 5

    # Generate data in both Python and R to compare
    # Python data generation
    X = np.random.randn(n_samples, n_features)
    true_coefficients = np.array([1.0, -0.5, 0.3, -0.2, 0.1])
    y = X @ true_coefficients + np.random.normal(0, 0.1, n_samples)

    # Generate identical data in R
    ro.r(
        f"""
    X_r <- matrix(rnorm(100 * 5), nrow = 100, ncol = 5)
    true_coefficients_r <- c(1.0, -0.5, 0.3, -0.2, 0.1)
    y_r <- X_r %*% true_coefficients_r + rnorm(100, mean = 0, sd = 0.1)
    """
    )

    # Get the data from R
    X_r = np.array(ro.r("X_r"))
    y_r = np.array(ro.r("y_r")).ravel()

    # 1. Fit with scikit-learn's Ridge (for comparison)
    print("\n1. Fitting scikit-learn Ridge model")
    lambda_value = 0.1

    # Use our create_ridge_model_sklearn function instead of directly using Ridge
    # This will better align the sklearn implementation with glmnet
    from robyn.modeling.ridge.models.ridge_utils import create_ridge_model_sklearn

    sklearn_model = create_ridge_model_sklearn(
        lambda_value=lambda_value,
        n_samples=n_samples,
        fit_intercept=True,
        standardize=True,
    )
    sklearn_start = time.time()
    sklearn_model.fit(X, y)
    sklearn_elapsed = time.time() - sklearn_start
    sklearn_pred = sklearn_model.predict(X)

    # 2. Fit with our rpy2 wrapper (using identical data to sklearn)
    print("\n2. Fitting R glmnet model via rpy2 wrapper (Python data)")
    rpy2_model = create_ridge_model_rpy2(
        lambda_value=lambda_value,
        n_samples=n_samples,
        fit_intercept=True,
        standardize=True,
    )
    rpy2_start = time.time()
    rpy2_model.fit(X, y)
    rpy2_elapsed = time.time() - rpy2_start
    rpy2_pred = rpy2_model.predict(X)

    # 3. Fit with pure R code (for validation)
    print("\n3. Fitting pure R glmnet model (R data)")
    r_start = time.time()
    ro.r(
        f"""
    lambda_value <- {lambda_value}
    library(glmnet)
    r_model <- glmnet(
        x = X_r,
        y = y_r, 
        family = "gaussian",
        alpha = 0,  # 0 for ridge regression
        lambda = lambda_value,
        standardize = TRUE,
        intercept = TRUE,
        type.measure = "mse"
    )
    r_coef <- as.numeric(coef(r_model, s = lambda_value))
    r_pred <- as.numeric(predict(r_model, newx = X_r, s = lambda_value, type = "response"))
    """
    )
    r_elapsed = time.time() - r_start

    # Get results from R
    r_coef = np.array(ro.r("r_coef"))
    r_pred = np.array(ro.r("r_pred"))

    # Calculate metrics - Fixed: Use y_r for the pure R model evaluation
    def calculate_r2(y_true, y_pred):
        return 1 - np.sum((y_true - y_pred) ** 2) / np.sum(
            (y_true - np.mean(y_true)) ** 2
        )

    sklearn_r2 = calculate_r2(y, sklearn_pred)
    rpy2_r2 = calculate_r2(y, rpy2_pred)
    r_r2 = calculate_r2(y, r_pred)

    # Compare coefficients
    print("\nCoefficients comparison:")
    print(f"True coefficients: {true_coefficients}")
    print(f"sklearn intercept: {sklearn_model.intercept_:.6f}")
    print(f"sklearn coefficients: {sklearn_model.coef_}")
    print(f"rpy2 intercept: {rpy2_model.intercept_:.6f}")
    print(f"rpy2 coefficients: {rpy2_model.coef_}")
    print(f"pure R intercept: {r_coef[0]:.6f}")
    print(f"pure R coefficients: {r_coef[1:]}")

    # Compare R² values
    print("\nPerformance metrics:")
    print(f"sklearn R²: {sklearn_r2:.6f}, time: {sklearn_elapsed:.6f}s")
    print(f"rpy2 R²: {rpy2_r2:.6f}, time: {rpy2_elapsed:.6f}s")
    print(f"pure R R²: {r_r2:.6f}, time: {r_elapsed:.6f}s")

    # Compare predictions
    print("\nPrediction differences:")
    print(
        f"sklearn vs rpy2 mean absolute diff: {np.mean(np.abs(sklearn_pred - rpy2_pred)):.6f}"
    )
    print(
        f"rpy2 vs pure R mean absolute diff: {np.mean(np.abs(rpy2_pred - r_pred)):.6f}"
    )
    print(
        f"sklearn vs pure R mean absolute diff: {np.mean(np.abs(sklearn_pred - r_pred)):.6f}"
    )

    # Visualize predictions for the first few samples
    n_display = min(10, n_samples)
    print(f"\nSample predictions (first {n_display}):")
    for i in range(n_display):
        print(
            f"Sample {i}: True={y[i]:.4f}, sklearn={sklearn_pred[i]:.4f}, rpy2={rpy2_pred[i]:.4f}, pure R={r_pred[i]:.4f}"
        )

    # Plot predictions comparison
    plt.figure(figsize=(12, 8))

    # Plot 1: True vs predicted
    plt.subplot(2, 2, 1)
    plt.scatter(y, sklearn_pred, alpha=0.5, label="sklearn")
    plt.scatter(y, rpy2_pred, alpha=0.5, label="rpy2")
    plt.plot([min(y), max(y)], [min(y), max(y)], "k--")
    plt.xlabel("True values")
    plt.ylabel("Predicted values")
    plt.title("True vs Predicted")
    plt.legend()

    # Plot 2: sklearn vs rpy2
    plt.subplot(2, 2, 2)
    plt.scatter(sklearn_pred, rpy2_pred)
    plt.plot(
        [min(sklearn_pred), max(sklearn_pred)],
        [min(sklearn_pred), max(sklearn_pred)],
        "k--",
    )
    plt.xlabel("sklearn predictions")
    plt.ylabel("rpy2 predictions")
    plt.title("sklearn vs rpy2 predictions")

    # Plot 3: Coefficients comparison
    plt.subplot(2, 2, 3)
    width = 0.25
    x = np.arange(len(true_coefficients))
    plt.bar(x - width, true_coefficients, width, label="True")
    plt.bar(x, sklearn_model.coef_, width, label="sklearn")
    plt.bar(x + width, rpy2_model.coef_, width, label="rpy2")
    plt.bar(x + 2 * width, r_coef[1:], width, label="pure R")
    plt.xticks(x, [f"X{i+1}" for i in range(len(true_coefficients))])
    plt.ylabel("Coefficient value")
    plt.title("Coefficient comparison")
    plt.legend()

    # Plot 4: Intercept comparison
    plt.subplot(2, 2, 4)
    intercepts = [0, sklearn_model.intercept_, rpy2_model.intercept_, r_coef[0]]
    plt.bar(["True", "sklearn", "rpy2", "pure R"], intercepts)
    plt.ylabel("Intercept value")
    plt.title("Intercept comparison")

    plt.tight_layout()
    plt.savefig(
        "/Users/yijuilee/robynpy_release_reviews/Robyn/python/src/robyn/debug/modeling_approach"
    )
    plt.close()
    print("\nPlot saved as 'ridge_model_comparison.png'")

    return {
        "sklearn_model": sklearn_model,
        "rpy2_model": rpy2_model,
        "sklearn_r2": sklearn_r2,
        "rpy2_r2": rpy2_r2,
        "r_r2": r_r2,
    }


if __name__ == "__main__":
    results = test_rpy2_ridge_modeling()
    print("\nTest completed successfully!")
