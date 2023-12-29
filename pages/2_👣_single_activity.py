import altair as alt
import streamlit as st

from utils.data_cache import load_data_from_cache

DISTANCE_KM = "Distance (km)"
TIME_S = "Time (s)"
N_POINTS = 500  # for sampling

activities_df, streams_df = load_data_from_cache()

with st.sidebar:
    selected_activity_idx = st.selectbox(
        label="Select an activity",
        options=activities_df.index[::-1],
        format_func=lambda idx: f"{activities_df.loc[idx, 'start_date'].strftime('%y-%m-%d')}/ {activities_df.loc[idx, 'name']} ({activities_df.loc[idx, 'distance']/1000:.2f}km)",
    )
    selected_x_unit_label = st.selectbox(
        label="X axis unit", options=[TIME_S, DISTANCE_KM]
    )
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
sampled_selected_activity_streams = selected_activity_streams.iloc[
    :: len(selected_activity_streams) // N_POINTS
]

st.write(
    f"""
### 🏃{selected_activity['name']} \
🕰️ {selected_activity.start_date.strftime('%d/%m/%Y %H:%M')} \
📏 {selected_activity.distance/1000:.2f} km
"""
)

x_axis = alt.X(selected_x_unit_col, type="quantitative", title="").axis(labels=False)

base = alt.Chart(sampled_selected_activity_streams).transform_window(
    rolling_mean_speed_kmh="mean(speed_kmh)",
    frame=[-smooth_span, 0],
)

# %% Line tooltip
nearest = alt.selection_point(
    nearest=True,
    on="mouseover",
    fields=[selected_x_unit_col],
    empty=False,
)

selectors = base.mark_point().encode(x=x_axis, opacity=alt.value(0)).add_params(nearest)


def add_vertical_line_tooltip(
    base_chart: alt.Chart, tooltip_text: alt.Text
) -> alt.Chart:
    points = base_chart.mark_point(size=100, color="gray", opacity=0.7).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    rules = (
        base.mark_rule(color="gray", opacity=0.7, strokeWidth=2)
        .encode(x=x_axis)
        .transform_filter(nearest)
    )
    text = rules.mark_text(align="left", dx=5, y=10).encode(
        text=tooltip_text,
    )

    return base_chart + selectors + points + rules + text


# %% Charts
speed_chart = add_vertical_line_tooltip(
    base_chart=base.mark_line().encode(
        x=x_axis,
        y=alt.Y(
            "rolling_mean_speed_kmh",
            type="quantitative",
        ).title("Speed (Km/h)"),
    ),
    tooltip_text=alt.Text("rolling_mean_speed_kmh:Q", format=".2f"),
)

heartrate_chart = add_vertical_line_tooltip(
    base_chart=base.mark_line().encode(
        x=x_axis,
        y=alt.Y(
            "heartrate", type="quantitative", scale=alt.Scale(domain=[90, 190])
        ).title("Heartrate (/min)"),
    ),
    tooltip_text=alt.Text("heartrate:Q"),
)

altitude_chart = add_vertical_line_tooltip(
    base_chart=base.mark_area(interpolate="natural", line=True).encode(
        x=x_axis.title(selected_x_unit_label).axis(labels=True),
        y=alt.Y("altitude", type="quantitative", title="Altitude (m)"),
    ),
    tooltip_text=alt.Text("altitude:Q"),
)

global_width = 900

chart = (
    speed_chart.properties(height=200, width=global_width)
    & heartrate_chart.properties(height=120, width=global_width)
    & altitude_chart.properties(height=120, width=global_width)
).interactive(bind_y=False)

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

st.write(
    f"N data points for activity (before sub-sampling): {len(selected_activity_streams)}"
)
st.write(
    f"N data points for activity (after sub-sampling): {len(sampled_selected_activity_streams)}"
)
st.write(selected_activity)
