import altair as alt
import streamlit as st

from utils.data_cache import load_data_from_cache
from utils.data import get_temporal_grouper


activities_df, streams_df = load_data_from_cache()
pd_grouper, _ = get_temporal_grouper(st_elt=st.sidebar, key="global-volume")

data = (
    activities_df.filter(items=["start_date", "distance"])
    .groupby(pd_grouper)
    .sum()
    .reset_index()
)
bar = (
    alt.Chart(data)
    .mark_bar()
    .encode(
        x="start_date:T",
        y="distance:Q",
    )
)
line = (
    alt.Chart(data)
    .mark_line(color="red")
    .transform_window(
        rolling_mean="mean(distance)",
        frame=[-9, 0],
    )
    .encode(
        x="start_date:T",
        y="rolling_mean:Q",
    )
)
st.altair_chart(bar + line, use_container_width=True)

grouped_distances = (
    activities_df.filter(items=["start_date", "distance"]).groupby(pd_grouper).sum()
)
st.bar_chart(grouped_distances, y="distance")

# ---- global, mean speed week
grouped_average_speed = (
    activities_df.filter(items=["start_date", "distance", "moving_time"])
    .groupby(pd_grouper)
    .sum()
    .assign(average_speed_kmh=lambda df: df.distance / df.moving_time * 3.6)
)
st.bar_chart(grouped_average_speed, y="average_speed_kmh")
