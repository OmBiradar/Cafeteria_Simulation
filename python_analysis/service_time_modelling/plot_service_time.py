import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm

# Estimated parameters from the previous steps
mu = 4.9280
sigma = 0.4836

# Load the data
try:
    df = pd.read_csv("service_times.csv")
    raw_data = df["service_time_seconds"].dropna()
except FileNotFoundError:
    print(
        "Error: 'service_times.csv' not found. Ensure it is in the current directory."
    )
    # Fallback for demonstration
    raw_data = pd.Series(np.random.lognormal(mean=mu, sigma=sigma, size=100))

# Create the plot
plt.figure(figsize=(10, 6))

# Plot the histogram of the raw service times
# We use density=True so the y-axis matches the probability density function (PDF)
num_bins = int(np.sqrt(len(raw_data))) * 2
plt.hist(
    raw_data,
    bins=num_bins,
    density=True,
    alpha=0.6,
    color="skyblue",
    edgecolor="black",
    label="Observed Data (Histogram)",
)

# Generate the theoretical log-normal curve
# Get the limits of the x-axis from the histogram
x_min, x_max = plt.xlim()

# Generate x values for the smooth curve (must be > 0 for log-normal)
x = np.linspace(max(0.1, x_min), x_max, 1000)

# In scipy.stats.lognorm:
# - 's' is the shape parameter (which is the standard deviation of the log-transformed data, sigma)
# - 'scale' is exp(mu), where mu is the mean of the log-transformed data
pdf_fitted = lognorm.pdf(x, s=sigma, scale=np.exp(mu))

# Plot the theoretical curve
plt.plot(
    x,
    pdf_fitted,
    "r-",
    lw=2,
    label=f"Theoretical Log-Normal\n($\mu$={mu}, $\sigma$={sigma})",
)

# Formatting the plot
plt.title("Service Times: Observed Data vs. Estimated Log-Normal Curve")
plt.xlabel("Service Time (seconds)")
plt.ylabel("Density")
plt.legend()
plt.grid(axis="y", alpha=0.75)
plt.tight_layout()

# Save the plot
plt.savefig("fitted_lognormal_plot.png")
print("Plot successfully saved as 'fitted_lognormal_plot.png'")
