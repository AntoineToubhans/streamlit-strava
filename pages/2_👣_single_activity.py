import altair as alt
import streamlit as st

from utils.data_cache import load_data_from_cache

DISTANCE_KM = "Distance (km)"
TIME_S = "Time (s)"

activities_df, streams_df = load_data_from_cache()

with st.sidebar:
    selected_activity_idx = st.selectbox(
        label="Select an activity",
        options=activities_df.index[::-1],
        format_func=lambda idx: f"{activities_df.loc[idx, 'start_date'].strftime('%y-%m-%d')}/ {activities_df.loc[idx, 'name']} ({activities_df.loc[idx, 'distance']/1000:.2f}km)",
    )
    selected_x_unit_label = st.selectbox(label="Y unit", options=[TIME_S, DISTANCE_KM])
    selected_x_unit_col = {
        TIME_S: "time",
        DISTANCE_KM: "distance_km",
    }[selected_x_unit_label]

    smooth_span = st.slider(label="Smooth span", value=10, min_value=1, max_value=100)


selected_activity = activities_df.loc[selected_activity_idx]
selected_activity_streams = streams_df.loc[
    lambda df: df.activity_id == selected_activity.id
].assign(
    distance_km=lambda df: df.distance / 1000,
    speed_kmh=lambda df: df.velocity_smooth * 3.6,
)

base = (
    alt.Chart(selected_activity_streams)
    .transform_window(
        rolling_mean_speed_kmh="mean(speed_kmh)",
        rolling_mean_heartrate="mean(heartrate)",
        frame=[-smooth_span, 0],
    )
    .encode(
        x=alt.X(selected_x_unit_col, type="quantitative").title(selected_x_unit_label)
    )
)

speed_chart = base.mark_line().encode(
    y=alt.Y(
        "rolling_mean_speed_kmh", type="quantitative", scale=alt.Scale(domain=[0, 25])
    ).title("Speed (Km/h)")
)

heartrate_chart = base.mark_line().encode(
    y=alt.Y(
        "rolling_mean_heartrate", type="quantitative", scale=alt.Scale(domain=[90, 190])
    ).title("Heartrate (/min)")
)

chart = (
    (
        speed_chart.properties(height=200, width=900)
        & heartrate_chart.properties(height=200, width=900)
    )
    .interactive(bind_y=False)
    .resolve_scale(y="independent")
)

st.altair_chart(chart, use_container_width=True)


st.write("---")
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
