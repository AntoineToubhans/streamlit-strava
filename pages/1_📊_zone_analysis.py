import datetime

import altair as alt
import pandas as pd
import streamlit as st

from utils.data_cache import load_data_from_cache
from utils.data import get_temporal_grouper


# %% 0. Load data
years_df = pd.DataFrame(
    {
        "date": [datetime.datetime(year, 1, 1) for year in [2022, 2023, 2024]],
    }
)


activities_df, streams_df = load_data_from_cache()

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
    & (distance_area.properties(height=80, width=900) + year_rules + year_rules_labels)
).configure_legend(orient="top", direction="horizontal", title=None)

st.altair_chart(final_chart, use_container_width=True)
