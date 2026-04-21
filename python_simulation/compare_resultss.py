import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("./resultss/overall_results.csv")

# Create a combined label for the x-axis
df["x_label"] = (
    df["num_human"].astype(str) + " Human + " + df["num_kiosk"].astype(str) + " kiosks"
)

# Define the exact order for the x-axis
x_order = [
    "1 Human + 0 kiosks",
    "1 Human + 1 kiosks",
    "1 Human + 2 kiosks",
    "1 Human + 3 kiosks",
    "2 Human + 0 kiosks",
    "2 Human + 1 kiosks",
    "2 Human + 2 kiosks",
    "2 Human + 3 kiosks",
]

# Ensure data is ordered according to the x_order
df["x_label"] = pd.Categorical(df["x_label"], categories=x_order, ordered=True)
df = df.sort_values(["x_label", "config_profile"])

configs = ["config_1", "config_2", "config_3", "config_4", "config_5"]
colors = {
    "config_1": "blue",
    "config_2": "orange",
    "config_3": "green",
    "config_4": "red",
    "config_5": "purple",
}

# ---------------------------------------------------------
# Plot 1: Queue Lengths
# ---------------------------------------------------------
plt.figure(figsize=(14, 8))
for config in configs:
    config_data = df[df["config_profile"] == config]
    # Solid line for Max Capacity
    plt.plot(
        config_data["x_label"],
        config_data["max_queue_capacity"],
        color=colors[config],
        linestyle="-",
        marker="o",
        label=f"{config} - Max Capacity",
    )
    # Dashed line for Max Reached
    plt.plot(
        config_data["x_label"],
        config_data["max_queue_length_reached"],
        color=colors[config],
        linestyle="--",
        marker="x",
        label=f"{config} - Max Reached",
    )
    # Dotted line for Avg Length
    plt.plot(
        config_data["x_label"],
        config_data["avg_queue_length"],
        color=colors[config],
        linestyle=":",
        marker="s",
        label=f"{config} - Avg Length",
    )

plt.xlabel("Configuration (Human + Kiosks)")
plt.ylabel("Queue Length")
plt.title("Queue Lengths across Configurations")
plt.xticks(rotation=45, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("queue_lengths.png")
plt.close()

# ---------------------------------------------------------
# Plot 2: Waiting Times
# ---------------------------------------------------------
plt.figure(figsize=(14, 8))
for config in configs:
    config_data = df[df["config_profile"] == config]
    # Solid line for Avg Wait Time
    plt.plot(
        config_data["x_label"],
        config_data["avg_wait_time_sec"],
        color=colors[config],
        linestyle="-",
        marker="o",
        label=f"{config} - Avg Wait Time",
    )
    # Dashed line for Max Wait Time
    plt.plot(
        config_data["x_label"],
        config_data["max_wait_time_sec"],
        color=colors[config],
        linestyle="--",
        marker="x",
        label=f"{config} - Max Wait Time",
    )

plt.xlabel("Configuration (Human + Kiosks)")
plt.ylabel("Waiting Time (seconds)")
plt.title("Waiting Times across Configurations")
plt.xticks(rotation=45, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("waiting_times.png")
plt.close()

# ---------------------------------------------------------
# Plot 3: Customers Served vs Not Served
# ---------------------------------------------------------
plt.figure(figsize=(14, 8))
for config in configs:
    config_data = df[df["config_profile"] == config]
    # Solid line for Served
    plt.plot(
        config_data["x_label"],
        config_data["customers_served"],
        color=colors[config],
        linestyle="-",
        marker="o",
        label=f"{config} - Served",
    )
    # Dashed line for Not Served
    plt.plot(
        config_data["x_label"],
        config_data["customers_not_served"],
        color=colors[config],
        linestyle="--",
        marker="x",
        label=f"{config} - Not Served",
    )

plt.xlabel("Configuration (Human + Kiosks)")
plt.ylabel("Number of Customers")
plt.title("Customers Served vs Not Served across Configurations")
plt.xticks(rotation=45, ha="right")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig("customers_served.png")
plt.close()
