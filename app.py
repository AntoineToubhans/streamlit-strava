import pandas as pd
import streamlit as st

from constants import DATA_PATH
from utils import get_zone


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
    ).assign(speed_zone=lambda df: df.velocity_smooth.map(get_zone))

    return activities, streams


def show_activities_stats(grouper: pd.Grouper):
    grouped_distances = (
        activities_df.filter(items=["start_date", "distance"]).groupby(grouper).sum()
    )
    st.bar_chart(grouped_distances, y="distance")

    # ---- global, mean speed week
    grouped_average_speed = (
        activities_df.filter(items=["start_date", "distance", "moving_time"])
        .groupby(grouper)
        .sum()
        .assign(average_speed_kmh=lambda df: df.distance / df.moving_time * 3.6)
    )
    st.bar_chart(grouped_average_speed, y="average_speed_kmh")


def show_zone_stats(grouper: pd.Grouper):
    zone_speed_streams_df = pd.pivot_table(
        data=(
            streams_df.merge(
                activities_df.rename(
                    columns={
                        "id": "activity_id",
                        "distance": "total_distance",
                    }
                ),
                on="activity_id",
            )
            .filter(items=["start_date", "speed_zone"])
            .assign(duration=1)
            .groupby([grouper, "speed_zone"], as_index=False)
            .duration.sum()
        ),
        values="duration",
        index="start_date",
        columns="speed_zone",
        aggfunc="sum",
    )

    st.bar_chart(zone_speed_streams_df)


def show_one_activity_stats():
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


st.sidebar.title("Strava-data app")
LABEL_FREQ_GROUPER = st.sidebar.selectbox(
    label="Group by", options=["Week", "Month", "Year"]
)
FREQ_GROUPER = {"Week": "W-SUN", "Month": "M", "Year": "Y"}[LABEL_FREQ_GROUPER]
GROUPER = pd.Grouper(key="start_date", freq=FREQ_GROUPER)

activities_df, streams_df = load_data()

activities_stats_tab, zone_stats_tab, one_activity_stats_tab = st.tabs(
    ["All", "Zones", "One activity"]
)
with activities_stats_tab:
    show_activities_stats(grouper=GROUPER)
with zone_stats_tab:
    show_zone_stats(grouper=GROUPER)
with one_activity_stats_tab:
    show_one_activity_stats()
