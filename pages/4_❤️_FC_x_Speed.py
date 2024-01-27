import streamlit as st
import altair as alt

from utils.data_cache import load_data_from_cache

activities_df, streams_df = load_data_from_cache()

st.warning("🚧WIP")

with st.sidebar:
    selected_activity_idx = st.selectbox(
        label="Select an activity",
        options=activities_df.index[::-1],
        format_func=lambda idx: f"{activities_df.loc[idx, 'start_date'].strftime('%y-%m-%d')}/ {activities_df.loc[idx, 'name']} ({activities_df.loc[idx, 'distance']/1000:.2f}km)",
    )
    rolling_window = st.slider(
        label="Smooth span", value=10, min_value=1, max_value=100
    )

selected_activity = activities_df.loc[selected_activity_idx]
selected_activity_streams = streams_df.loc[
    lambda df: df.activity_id == selected_activity.id
].assign(
    speed_ms=lambda df: df.velocity_smooth.rolling(
        window=rolling_window, center=True, min_periods=1
    ).mean(),
    speed_kmh=lambda df: df.speed_ms * 3.6,
)

st.write(len(selected_activity_streams))

slider = alt.binding_range(min=50, max=200, step=1)
threshold = alt.param(name="threshold", value=200, bind=slider)

detail_points = (
    alt.Chart(selected_activity_streams)
    .mark_circle()
    .encode(
        x=alt.X("heartrate:Q").title("Heart Rate (/min)"),
        y=alt.Y("speed_kmh:Q").title("Speed (km/h)"),
    )
    .transform_filter(alt.datum["heartrate"] >= threshold)
)

aggregated_points = (
    alt.Chart(selected_activity_streams)
    .mark_circle()
    .encode(
        x=alt.X("heartrate:Q").bin(maxbins=20),
        y=alt.Y("speed_kmh:Q").bin(maxbins=10),
        size=alt.Size("count():Q"),
    )
    .transform_filter(alt.datum["heartrate"] < threshold)
)

vertical_line = (
    alt.Chart()
    .mark_rule(color="black")
    .encode(
        strokeWidth=alt.StrokeWidth(value=6),
        x=alt.X(datum=alt.expr(threshold.name), type="quantitative"),
    )
)

chart = (
    (detail_points + aggregated_points + vertical_line)
    .add_params(threshold)
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)
