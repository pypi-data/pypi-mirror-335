import numpy as np
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
from rpy2.robjects.conversion import localconverter

# Activate automatic conversion
numpy2ri.activate()

# Import necessary R packages
base = importr("base")
try:
    glmnet = importr("glmnet")
    print("glmnet package successfully imported")
except Exception as e:
    print(f"Error importing glmnet: {e}")
    print("Installing glmnet package in R...")
    utils = importr("utils")
    utils.install_packages("glmnet")
    glmnet = importr("glmnet")

# Set seed and create the exact same data as in R
ro.r("set.seed(42)")
ro.r("X <- matrix(rnorm(100 * 5), nrow = 100, ncol = 5)")
ro.r("true_coefficients <- c(1.0, -0.5, 0.3, -0.2, 0.1)")
ro.r("y <- X %*% true_coefficients + rnorm(100, mean = 0, sd = 0.1)")
ro.r("lambda_value <- 0.1")

# Fit model with glmnet in R
print("Fitting model with glmnet...")
ro.r(
    """
model <- glmnet(
  x = X,
  y = y,
  family = "gaussian", 
  alpha = 0,  # 0 for ridge regression
  lambda = lambda_value,
  standardize = TRUE,
  intercept = TRUE,
  thresh = 1e-07,
  maxit = 1e5,
  nlambda = 1
)
"""
)

# Get model coefficients
ro.r("coef <- coef(model, s = lambda_value)")
print("Model coefficients from R:")
print(ro.r("coef"))

# Make predictions
ro.r('predictions <- predict(model, newx = X, s = lambda_value, type = "response")')
print("\nFirst few predictions:")
print(ro.r("head(predictions)"))

# Calculate R-squared
ro.r("r2 <- 1 - sum((y - predictions)^2) / sum((y - mean(y))^2)")
r2_value = ro.r("r2")[0]
print(f"\nR-squared: {r2_value}")

# Compare with true coefficients
print("\nTrue vs Estimated coefficients:")
coef_values = np.array(ro.r("as.numeric(coef)"))
true_coef_values = np.array(ro.r("true_coefficients"))
print(f"(Intercept): {coef_values[0]}")
for i in range(len(true_coef_values)):
    print(
        f"Feature {i+1}: True = {true_coef_values[i]}, Estimated = {coef_values[i+1]}"
    )

# Convert results to numpy arrays for further use in Python if needed
with localconverter(ro.default_converter + numpy2ri.converter):
    X_np = np.array(ro.r("X"))
    y_np = np.array(ro.r("y")).ravel()
    coef_np = np.array(ro.r("as.numeric(coef)"))
    predictions_np = np.array(ro.r("predictions")).ravel()

print("\nData and results are now available as NumPy arrays in Python")
