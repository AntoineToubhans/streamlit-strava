from datetime import timedelta

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_cache import load_data_from_cache
from utils.data import (
    get_temporal_grouper,
    st_speed_range_selector,
    stop_if_no_activities,
)


DISTANCE_KM = "Distance (km)"
TIME_S = "Time (s)"
activities_df, streams_df = load_data_from_cache()
stop_if_no_activities(activities_df)

with st.sidebar:
    pd_grouper, alt_timeunit = get_temporal_grouper(key="zone-stats")
    selected_y_unit_label = st.selectbox(label="Y unit", options=[DISTANCE_KM, TIME_S])
    selected_y_unit = {
        TIME_S: "duration",
        DISTANCE_KM: "distance_km",
    }[selected_y_unit_label]
    max_speed, min_speed = st_speed_range_selector()


cumulated_at_speed_range_df = (
    streams_df.merge(
        activities_df.rename(columns={"id": "activity_id"}).filter(
            items=["activity_id", "start_date"]
        ),
        on="activity_id",
    )
    .loc[
        lambda df: (df.velocity_smooth >= min_speed) & (df.velocity_smooth <= max_speed)
    ]
    .assign(distance_km=lambda df: df.velocity_smooth / 1000, duration=1)
    .filter(items=["start_date", "distance_km", "duration"])
    .groupby([pd_grouper], as_index=False)
    .sum()
    .sort_values(by=selected_y_unit, ascending=False)
    .head(25)
    .assign(
        tooltip_duration=lambda df: df.duration.apply(
            lambda x: str(timedelta(seconds=x))
        ),
        tooltip_distance_km=lambda df: df.distance_km.apply(lambda x: f"{x:.2f} km"),
    )
)

chart_bar = (
    alt.Chart(cumulated_at_speed_range_df)
    .encode(
        x=alt.XError(
            selected_y_unit,
            type="quantitative",
            title=selected_y_unit,
        ),
        y=alt.Y(
            "start_date",
            type="ordinal",
            axis=alt.Axis(format="%d %b %Y", formatType="time"),
            sort=None,
        ).title(""),
        color="year(start_date):N",
        tooltip=f"tooltip_{selected_y_unit}",
    )
    .mark_bar(point=True)
)

chart_text = chart_bar.encode(text=f"tooltip_{selected_y_unit}").mark_text(
    align="left", dx=2
)
chart = (chart_bar + chart_text).properties(title="").configure_legend(title=None)

st.altair_chart(chart, use_container_width=True)
