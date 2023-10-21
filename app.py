import pandas as pd
import streamlit as st

from constants import DATA_PATH


@st.cache_data
def load_data():
    activities = pd.read_csv(
        DATA_PATH / "activities.csv", index_col=0, parse_dates=["start_date"]
    )

    streams = pd.concat(
        [
            pd.read_csv(DATA_PATH / f"{activity_id}.csv", index_col=0).assign(
                activity_id=activity_id
            )
            for activity_id in activities.id.unique()
        ]
    )

    return activities, streams


st.title("Strava-data app")


activities_df, streams_df = load_data()

label_freq_grouper = st.selectbox(label="Group by", options=["Week", "Month", "Year"])
freq_grouper = {"Week": "W-SUN", "Month": "M", "Year": "Y"}[label_freq_grouper]

grouped_distances = activities_df.groupby(
    pd.Grouper(key="start_date", freq=freq_grouper)
).distance.sum()
st.bar_chart(grouped_distances)

# ---- global, mean speed week
speed_by_week = (
    activities_df.filter(items=["start_date", "distance", "elapsed_time"])
    .groupby(pd.Grouper(key="start_date", freq="W-SUN"))
    .sum()
    .assign(average_speed_kmh=lambda df: df.distance / df.elapsed_time * 3.6)
)
st.bar_chart(speed_by_week, y="average_speed_kmh")

# --- per activity
selected_activity_idx = st.selectbox(
    label="Select an activity",
    options=activities_df.index,
    format_func=lambda idx: f"{activities_df.loc[idx, 'start_date']} - {activities_df.loc[idx, 'name']}",
)

selected_activity = activities_df.loc[selected_activity_idx]
selected_activity_streams = streams_df.loc[
    lambda df: df.activity_id == selected_activity.id
]

col_a, col_b = st.columns(2)

col_a.write("From activity")
col_b.write("From streams")

col_a.write(f"Distance: {selected_activity.distance}")
col_b.write(
    f"Distance (distance.max() - distance.min()): {selected_activity_streams.distance.max() - selected_activity_streams.distance.min()}"
)
col_b.write(
    f"Distance (velocity_smooth.sum()): {selected_activity_streams.velocity_smooth.sum()}"
)

ewm_span = st.slider(label="span", min_value=10, max_value=1000)

st.line_chart(
    selected_activity_streams.assign(
        y=lambda df: (df.velocity_smooth * 3.6).ewm(span=ewm_span).mean()
    ),
    x="distance",
    y="y",
)

st.write(selected_activity)
st.write(selected_activity_streams)
