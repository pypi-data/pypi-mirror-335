import numpy as np
import rpy2.robjects as ro
from rpy2.robjects.packages import importr
from rpy2.robjects import numpy2ri
from sklearn.linear_model import Ridge

# Activate automatic conversion
numpy2ri.activate()

# Import necessary R packages
base = importr("base")
stats = importr("stats")
glmnet = importr("glmnet")

# Execute R code to generate the exact same data
ro.r("set.seed(42)")
ro.r("X <- matrix(rnorm(100 * 5), nrow = 100, ncol = 5)")
ro.r("true_coefficients <- c(1.0, -0.5, 0.3, -0.2, 0.1)")
ro.r("y <- X %*% true_coefficients + rnorm(100, mean = 0, sd = 0.1)")
ro.r("lambda_value <- 0.1")

# Get the data from R
X_r = np.array(ro.r("X"))
y_r = np.array(ro.r("y")).ravel()
true_coef_r = np.array(ro.r("true_coefficients"))

# Fit the glmnet model in R to use as reference
ro.r(
    """
model <- glmnet(
  x = X,
  y = y,
  family = "gaussian",
  alpha = 0,
  lambda = lambda_value,
  standardize = TRUE,
  intercept = TRUE,
  thresh = 1e-07,
  maxit = 1e5,
  nlambda = 1
)
coef <- coef(model, s = lambda_value)
predictions <- predict(model, newx = X, s = lambda_value, type = "response")
r2 <- 1 - sum((y - predictions)^2) / sum((y - mean(y))^2)
"""
)

# Now use sklearn with the SAME data
# For standardization, we need to do it manually like glmnet does
X_mean = X_r.mean(axis=0)
X_sd = X_r.std(axis=0, ddof=1)  # Use ddof=1 for sample standard deviation
X_scaled = (X_r - X_mean) / X_sd

# Fit Ridge model
# Note: glmnet uses lambda = alpha * (1/n) in the penalty, where sklearn uses alpha directly
n_samples = X_r.shape[0]
adjusted_alpha = 0.1 * n_samples  # Adjust alpha to match glmnet's penalty scaling

model_py = Ridge(
    alpha=adjusted_alpha,
    fit_intercept=True,
    max_iter=int(1e5),
    tol=1e-7,
    solver="cholesky",  # This is the most precise solver
)
model_py.fit(X_scaled, y_r)

# Convert sklearn coefficients back to original scale like glmnet does
coef_py = model_py.coef_ / X_sd
intercept_py = model_py.intercept_ - np.sum(coef_py * X_mean)

# Get R coefficients for comparison
r_coefs = np.array(ro.r("as.numeric(coef)"))
r_intercept = r_coefs[0]
r_coefs = r_coefs[1:]

# Print comparison
print("Coefficients comparison (R vs Python):")
print(
    f"Intercept: R={r_intercept}, Python={intercept_py}, Diff={r_intercept-intercept_py}"
)
for i in range(len(r_coefs)):
    diff = r_coefs[i] - coef_py[i]
    print(f"V{i+1}: R={r_coefs[i]}, Python={coef_py[i]}, Diff={diff}")

# Calculate predictions and R² the same way as R
pred_py = model_py.predict(X_scaled)
r2_py = 1 - np.sum((y_r - pred_py) ** 2) / np.sum((y_r - np.mean(y_r)) ** 2)
r2_r = float(ro.r("r2")[0])

print(f"\nR-squared: R={r2_r}, Python={r2_py}, Diff={r2_r-r2_py}")
