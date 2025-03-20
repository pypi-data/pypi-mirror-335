import pandas as pd
from ts_features_sculptor import IntervalEventsMerge


df_main = pd.DataFrame({
    "time": [
        "2024-12-22 01:01:01",
        "2024-12-26 01:01:01",
        "2025-01-01 01:01:01",
        "2025-01-02 01:01:01",
        "2025-01-03 01:01:01",
        "2025-01-05 01:01:01",
        "2025-01-08 01:01:01",
        "2025-01-10 01:01:01",
        "2025-01-12 01:01:01",
        "2025-01-20 01:01:01",
    ],
    "value": [6.0, 5.1, 5.5, 4.4, 3.3, 2.2, 1.1, 2.2, 3.3, 4.4]
})
df_main["time"] = pd.to_datetime(df_main["time"])
df_main.sort_values(by="time", inplace=True)

df_events = pd.DataFrame({
    "start": [
        "2025-01-02 00:00:01",
        "2025-01-11 12:00:00"
    ],
    "end": [
        "2025-01-05 23:59:59",
        "2025-01-15 23:59:59"
    ],
    "intensity": [0.10, 0.15],
    "category": [2, 1],
    "priority": [2, 1]
})
df_events["start"] = pd.to_datetime(df_events["start"])
df_events["end"] = pd.to_datetime(df_events["end"])
df_events = df_events.sort_values(by=["start"])

transformer = IntervalEventsMerge(
    time_col="time",
    events_df=df_events,
    start_col="start",
    end_col="end",
    events_cols=["intensity", "category", "priority"],
    fillna_value=0.0,
    days_to_start_col="days_to_event_start",
    days_to_end_col="days_to_event_end",
    inside_events_flag_col="inside_event_flag",
    event_num_col="event_num"
)
df_result = transformer.transform(df_main)

print("События:")
print(df_events.to_string())
print("\nРезультат:")
print(df_result.to_string())
