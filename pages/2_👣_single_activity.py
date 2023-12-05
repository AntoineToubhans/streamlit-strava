import streamlit as st

from data_utils import load_data


activities_df, streams_df = load_data()

selected_activity_idx = st.selectbox(
    label="Select an activity",
    options=activities_df.index,
    format_func=lambda idx: f"{activities_df.loc[idx, 'start_date']} - {activities_df.loc[idx, 'distance']/1000:.2f}km - {activities_df.loc[idx, 'name']}",
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
