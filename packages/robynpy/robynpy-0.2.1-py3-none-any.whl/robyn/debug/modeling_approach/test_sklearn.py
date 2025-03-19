import numpy as np
from sklearn.linear_model import Ridge
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Create sample data with a known relationship
X = np.random.normal(size=(100, 5))
true_coefficients = np.array([1.0, -0.5, 0.3, -0.2, 0.1])
noise = np.random.normal(0, 0.1, size=100)
y = X @ true_coefficients + noise
lambda_value = 0.1

# Fit model with Ridge regression (equivalent to glmnet with alpha=0)
# Note: sklearn's alpha is equivalent to glmnet's lambda
model = Ridge(
    alpha=lambda_value,
    fit_intercept=True,
    max_iter=int(1e5),
    tol=1e-7,
)
model.fit(X, y)

# Print model coefficients
print("Model coefficients:")
print(f"(Intercept): {model.intercept_}")
for i, coef in enumerate(model.coef_):
    print(f"V{i+1}: {coef}")

# Make predictions
predictions = model.predict(X)

# Print first few predictions
print("\nFirst few predictions:")
for i in range(6):  # Equivalent to head() in R
    print(f"[{i+1},]: {predictions[i]}")

# Calculate R-squared
r2 = 1 - np.sum((y - predictions) ** 2) / np.sum((y - np.mean(y)) ** 2)
print(f"\nR-squared: {r2}")

# Compare with true coefficients
print("\nTrue vs Estimated coefficients:")
for i in range(len(true_coefficients)):
    print(f"Feature {i+1}: True = {true_coefficients[i]}, Estimated = {model.coef_[i]}")
