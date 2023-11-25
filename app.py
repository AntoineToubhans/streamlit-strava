import datetime

import altair as alt
import pandas as pd
import streamlit as st

from constants import DATA_PATH
from st_utils import get_temporal_grouper
from zone_utils import get_speed_zone_label


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
    ).assign(speed_zone=lambda df: df.velocity_smooth.map(get_speed_zone_label))

    return activities, streams


def show_global_volume():
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


def show_zone_stats():
    pd_grouper, alt_timeunit = get_temporal_grouper(st_elt=st.sidebar, key="zone-stats")
    # %% 1. Process data
    zone_speed_streams_df = (
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
        .groupby([pd_grouper, "speed_zone"], as_index=False)
        .duration.sum()
    )

    # %% 2. Common alt parts
    year_rules = (
        alt.Chart(YEARS_DF)
        .mark_rule(opacity=0.5, strokeWidth=2)
        .encode(x=alt.X("year(date):T"), tooltip="year(date)")
    )

    year_rules_labels = year_rules.mark_text(
        opacity=0.7, align="left", dx=3, dy=3, baseline="line-top", fontSize=12
    ).encode(text="year(date):T", y=alt.value(0))

    brush = alt.selection_interval(encodings=["x"])
    legend_selection = alt.selection_point(fields=["speed_zone"], bind="legend")

    base = (
        alt.Chart(zone_speed_streams_df)
        .mark_bar(binSpacing=2)
        .encode(
            color=alt.condition(
                legend_selection, alt.Color("speed_zone:N"), alt.value("#aaa")
            ),
            opacity=alt.condition(legend_selection, alt.value(1), alt.value(0.2)),
        )
        .add_params(legend_selection)
    )

    # %% 3. Define charts
    abs_zone_bars = base.encode(
        x=alt.X(
            "start_date",
            timeUnit=alt_timeunit,
            type="temporal",
            axis=alt.Axis(labels=False),
            scale=alt.Scale(domain=brush),
        ).title(""),
        y=alt.Y("duration:Q").title("Time (s)"),
    ).transform_filter(legend_selection)

    normalized_zones_bars = base.encode(
        x=alt.X(
            "start_date",
            timeUnit=alt_timeunit,
            type="temporal",
            axis=alt.Axis(format="%d %b %y", labelOverlap=False, labelAngle=-45),
            scale=alt.Scale(domain=brush),
        ).title(""),
        y=alt.Y("duration:Q").stack("normalize").title("Time ratio (%)"),
    )

    distance_area = (
        alt.Chart(
            activities_df.filter(items=["start_date", "distance"])
            .groupby(pd_grouper)
            .sum()
            .assign(distance=lambda df: df.distance / 1000)  # in km
            .reset_index()
        )
        .mark_area(interpolate="natural")
        .encode(
            x=alt.X(
                "start_date",
                timeUnit=alt_timeunit,
                type="temporal",
                axis=alt.Axis(format="%d %b", labelOverlap=False, labelAngle=-45),
            ).title(""),
            y=alt.Y("sum(distance):Q").title("Distance (km)"),
        )
        .add_params(brush)
    )

    final_chart = (
        abs_zone_bars.properties(height=200, width=900)
        & normalized_zones_bars.properties(height=150, width=900)
        & (
            distance_area.properties(height=80, width=900)
            + year_rules
            + year_rules_labels
        )
    ).configure_legend(orient="top", direction="horizontal", title=None)

    st.altair_chart(final_chart, use_container_width=True)


def show_one_activity_stats():
    # --- per activity
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


YEARS_DF = pd.DataFrame(
    {
        "date": [datetime.datetime(year, 1, 1) for year in [2022, 2023, 2024]],
    }
)

st.set_page_config(layout="wide")
st.sidebar.title("Strava-data app")

activities_df, streams_df = load_data()

activities_stats_tab, zone_stats_tab, one_activity_stats_tab = st.tabs(
    ["All", "Zones", "One activity"]
)
with activities_stats_tab:
    show_global_volume()
with zone_stats_tab:
    show_zone_stats()
with one_activity_stats_tab:
    show_one_activity_stats()
