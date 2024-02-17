import datetime

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_cache import load_data_from_cache
from utils.data import get_temporal_grouper, stop_if_no_activities


# %% 0. Load data
DISTANCE_KM = "Distance (km)"
TIME_S = "Time (s)"
TODAY = datetime.datetime.now().date()
TODAY_P_14 = TODAY + datetime.timedelta(days=14)

years_df = pd.DataFrame(
    {
        "date": [datetime.datetime(year, 1, 1) for year in [2022, 2023, 2024]],
    }
)


activities_df, streams_df = load_data_from_cache()
stop_if_no_activities(activities_df)

with st.sidebar:
    pd_grouper, alt_timeunit = get_temporal_grouper(key="zone-stats")
    selected_y_unit_label = st.selectbox(label="Y unit", options=[TIME_S, DISTANCE_KM])
    selected_y_unit = {
        TIME_S: "duration",
        DISTANCE_KM: "distance_km",
    }[selected_y_unit_label]


# %% 1. Process data
zone_speed_streams_df = (
    streams_df.merge(
        activities_df.rename(columns={"id": "activity_id"}).filter(
            items=["activity_id", "start_date"]
        ),
        on="activity_id",
    )
    .assign(distance_km=lambda df: df.velocity_smooth / 1000, duration=1)
    .filter(items=["start_date", "speed_zone", "distance_km", "duration"])
    .groupby([pd_grouper, "speed_zone"], as_index=False)
    .sum()
)

# %% 2. Common alt parts
year_rules = (
    alt.Chart(years_df)
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
y_axis = alt.Y(selected_y_unit, type="quantitative")

abs_zone_bars = base.encode(
    x=alt.X(
        "start_date",
        timeUnit=alt_timeunit,
        type="temporal",
        axis=alt.Axis(labels=False),
        scale=alt.Scale(domain=brush),
    ).title(""),
    y=y_axis.title(selected_y_unit_label),
).transform_filter(legend_selection)

normalized_zones_bars = base.encode(
    x=alt.X(
        "start_date",
        timeUnit=alt_timeunit,
        type="temporal",
        axis=alt.Axis(format="%d %b %y", labelOverlap=False, labelAngle=-45),
        scale=alt.Scale(domain=brush),
    ).title(""),
    y=y_axis.stack("normalize").title("Ratio (%)"),
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
            scale=alt.Scale(
                domainMax={
                    "year": TODAY_P_14.year,
                    "month": TODAY_P_14.month,
                    "date": TODAY_P_14.day,
                }
            ),
        ).title(""),
        y=alt.Y("sum(distance):Q").title("Distance (km)"),
    )
    .add_params(brush)
)

final_chart = (
    abs_zone_bars.properties(height=200, width=900)
    & normalized_zones_bars.properties(height=150, width=900)
    & (distance_area.properties(height=80, width=900) + year_rules + year_rules_labels)
).configure_legend(orient="top", direction="horizontal", title=None)

st.altair_chart(final_chart, use_container_width=True)
