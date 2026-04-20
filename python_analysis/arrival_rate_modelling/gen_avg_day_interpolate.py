import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Load the data
df = pd.read_csv("arrival_data.csv")

# Ensure Total_Entries is numeric
df["Total_Entries"] = pd.to_numeric(df["Total_Entries"], errors="coerce")

# 2. Generate the complete range of time blocks between 10:00 and 19:00
full_time_range = (
    pd.date_range("10:00", "19:00", freq="10min").strftime("%H:%M").tolist()
)

# 3. Calculate average over weekdays using ORIGINAL data (no daily interpolation)
weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
weekday_df = df[df["Day"].isin(weekdays)]
avg_df = weekday_df.groupby("Time_Block")["Total_Entries"].mean().reset_index()

# 4. Interpolate ONLY the final average values
# Reindex to full time range to ensure all gaps are explicitly present as NaN
avg_df = avg_df.set_index("Time_Block").reindex(full_time_range)

# Linearly interpolate missing average values
avg_df["Total_Entries"] = avg_df["Total_Entries"].interpolate(method="linear")

# Handle any trailing/leading NaNs in case the bounds (10:00 or 19:00) were completely empty across all days
avg_df["Total_Entries"] = avg_df["Total_Entries"].bfill().ffill()

avg_df = avg_df.reset_index().rename(columns={"index": "Time_Block"})


# 5. Create time_slot format
def get_time_slot(start_time_str):
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

# Take the ceiling of the float values, then cast to integer
avg_df_csv["people_in"] = np.ceil(avg_df_csv["people_in"]).astype(int)

# Save to CSV
avg_df_csv.to_csv("average_day_arrivals_interpolated.csv", index=False)

# 6. Plotting the data
plt.figure(figsize=(14, 8))

# Plot raw, original daily data with gaps (not interpolated)
days = df["Day"].dropna().unique()
for day in days:
    day_data = df[df["Day"] == day].set_index("Time_Block").reindex(full_time_range)
    plt.plot(
        day_data.index,
        day_data["Total_Entries"],
        marker="o",
        markersize=3,
        label=day,
        alpha=0.6,
    )

# Plot the calculated AND interpolated weekday average
avg_data = avg_df.set_index("Time_Block")
plt.plot(
    avg_data.index,
    avg_data["Total_Entries"],
    color="black",
    linewidth=3,
    marker="s",
    markersize=5,
    label="Weekday Average (Interpolated)",
)

plt.xticks(full_time_range[::3], rotation=45)
plt.xlabel("Time Block")
plt.ylabel("People In / Total Entries")
plt.title("Entries over Time Blocks by Day (Only Average Interpolated)")
plt.legend()
plt.tight_layout()
plt.savefig("plot_interpolated.png")
