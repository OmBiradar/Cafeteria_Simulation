import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

# ==========================================
# Step 1: Collect and Prepare the Data
# ==========================================
# Load the raw data from the CSV file.
try:
    df = pd.read_csv("../../data/service_times.csv")
    # UPDATED: Use the new column name 'service_time_seconds'
    raw_data = df["service_time_seconds"].dropna()  # Remove any missing values
except FileNotFoundError:
    print(
        "Error: 'service_times.csv' not found. Please ensure the file is in the same directory."
    )
    # exit the program
    raise SystemExit(1)

# Apply the natural logarithm to transform the data
# If the raw data is log-normal, the log-transformed data will be normal
log_data = np.log(raw_data)

# ==========================================
# Step 2: Identify the Distribution Visually
# ==========================================
# Create a figure with two subplots: Histogram and Q-Q plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# --- 2a. Histogram ---
# Using the square root of the sample size for the number of bins as suggested
num_bins = int(np.sqrt(len(log_data)))
ax1.hist(log_data, bins=num_bins, color="skyblue", edgecolor="black", density=True)
ax1.set_title("Histogram of Log-Transformed Service Times")
ax1.set_xlabel("Log(Service Time in Seconds)")
ax1.set_ylabel("Density")

# Superimpose the theoretical normal curve for visual comparison
xmin, xmax = ax1.get_xlim()
x_line = np.linspace(xmin, xmax, 100)
p = stats.norm.pdf(x_line, log_data.mean(), log_data.std(ddof=1))
ax1.plot(x_line, p, "k", linewidth=2, label="Normal Curve")
ax1.legend()

# --- 2b. Quantile-Quantile (Q-Q) Plot ---
# This plots the ordered data against the theoretical quantiles of a normal distribution
stats.probplot(log_data, dist="norm", plot=ax2)
ax2.set_title("Q-Q Plot of Log-Transformed Service Times")

plt.tight_layout()
# You can use plt.show() if you run this locally, but here we save it to an image
plt.savefig("distribution_checks.png")
print("Saved distribution plot to 'distribution_checks.png'")

# ==========================================
# Step 3: Parameter Estimation
# ==========================================
# Calculate the sample mean and variance of the log-transformed data
sample_mean = np.mean(log_data)
# Use ddof=1 for sample variance (n-1 in the denominator)
sample_variance = np.var(log_data, ddof=1)
sample_std_dev = np.sqrt(sample_variance)

print("\n--- Parameter Estimation (Log-Transformed Data) ---")
print(f"Sample Mean (μ): {sample_mean:.4f}")
print(f"Sample Variance (σ²): {sample_variance:.4f}")
print(f"Sample Standard Deviation (σ): {sample_std_dev:.4f}")

# ==========================================
# Step 4: Evaluate Goodness-of-Fit
# ==========================================
# We use the Kolmogorov-Smirnov (K-S) Test to evaluate if the log-transformed data
# follows a normal distribution with our estimated mean and standard deviation.

# Perform the K-S test
ks_statistic, p_value = stats.kstest(
    log_data, "norm", args=(sample_mean, sample_std_dev)
)

print("\n--- Goodness-of-Fit Test (Kolmogorov-Smirnov) ---")
print(f"K-S Statistic (D): {ks_statistic:.4f}")
print(f"P-value: {p_value:.4f}")

# Interpret the results
alpha = 0.05  # Significance level (5%)
print(f"\nSignificance Level (α): {alpha}")
if p_value > alpha:
    print("Verdict: We CANNOT reject the null hypothesis.")
    print(
        "Conclusion: The log-transformed data appears to follow a normal distribution."
    )
    print(
        "Final Confirmation: Therefore, the original service times follow a Log-Normal distribution."
    )
else:
    print("Verdict: We REJECT the null hypothesis.")
    print("Conclusion: The log-transformed data DOES NOT follow a normal distribution.")
    print(
        "Final Confirmation: The original service times do not strictly follow a Log-Normal distribution."
    )
