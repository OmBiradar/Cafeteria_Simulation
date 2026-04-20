import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load the data (make sure the path points to your file)
df = pd.read_csv("arrival_data.csv")

# Ensure Total_Entries is numeric; missing values will become NaN
df["Total_Entries"] = pd.to_numeric(df["Total_Entries"], errors="coerce")

# 2. Calculate average over weekdays
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
weekday_df = df[df["Day"].isin(weekdays)]

# Group by Time_Block and calculate mean (pandas automatically ignores NaNs)
avg_df = weekday_df.groupby("Time_Block")["Total_Entries"].mean().reset_index()


# 3. Create time_slot format and save to CSV
def get_time_slot(start_time_str):
    """Converts '10:00' to '10:00 - 10:10'"""
    try:
        t = pd.to_datetime(start_time_str, format="%H:%M")
        t_end = t + pd.Timedelta(minutes=10)
        return f"{t.strftime('%H:%M')} - {t_end.strftime('%H:%M')}"
    except:
        return start_time_str


avg_df_csv = avg_df.copy()
avg_df_csv["time_slot"] = avg_df_csv["Time_Block"].apply(get_time_slot)
avg_df_csv = avg_df_csv[["time_slot", "Total_Entries"]].rename(
    columns={"Total_Entries": "people_in"}
)

# Use 'Int64' (capital I) to handle potential NaNs safely while acting as integer bounds
avg_df_csv["people_in"] = np.ceil(avg_df_csv["people_in"]).astype("Int64")

# Save to CSV
avg_df_csv.to_csv("average_day_arrivals_normal.csv", index=False)

# 4. Plotting the data
plt.figure(figsize=(14, 8))

# Sort the time blocks to ensure correct chronological order on the x-axis
time_blocks = sorted(df["Time_Block"].unique())

# Plot each individual day
days = df["Day"].dropna().unique()
for day in days:
    # Reindexing ensures that missing time blocks are filled with NaN,
    # breaking the line on the plot instead of connecting across gaps or plotting as 0.
    day_data = df[df["Day"] == day].set_index("Time_Block").reindex(time_blocks)
    plt.plot(
        day_data.index,
        day_data["Total_Entries"],
        marker="o",
        markersize=3,
        label=day,
        alpha=0.6,
    )

# Plot the calculated weekday average
avg_data = avg_df.set_index("Time_Block").reindex(time_blocks)
plt.plot(
    avg_data.index,
    avg_data["Total_Entries"],
    color="black",
    linewidth=3,
    marker="s",
    markersize=5,
    label="Weekday Average",
)

# Formatting the plot
# Subsampling x-ticks to prevent overlapping on the axis [::3] skips every 2 labels
plt.xticks(time_blocks[::3], rotation=45)
plt.xlabel("Time Block")
plt.ylabel("People In / Total Entries")
plt.title("Entries over Time Blocks by Day")
plt.legend()
plt.tight_layout()

# Save the plot
plt.savefig("plot_normal.png")
