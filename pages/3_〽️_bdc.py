import datetime

import altair as alt
import pandas as pd
import streamlit as st

from utils.data import stop_if_no_activities
from utils.data_cache import load_data_from_cache

POSITIVE_COLOR = "darkseagreen"
NEGATIVE_COLOR = "indianred"
TARGET_COLOR = "orange"

AVAILABLE_TARGETS = {
    "2025": {
        "target_km": 4000,
        "start_date": datetime.date(2025, 1, 1),
        "end_date": datetime.date(2025, 12, 31),
        "exclude": [],
    },
    "2024": {
        "target_km": 2200,
        "start_date": datetime.date(2024, 1, 1),
        "end_date": datetime.date(2024, 12, 31),
        "exclude": [
            {
                "start_date": datetime.date(2024, 1, 29),
                "end_date": datetime.date(2024, 3, 1),
            },
            {
                "start_date": datetime.date(2024, 6, 1),
                "end_date": datetime.date(2024, 7, 1),
            },
        ],
    },
    "2023": {
        "target_km": 2600,
        "start_date": datetime.date(2023, 1, 1),
        "end_date": datetime.date(2023, 12, 31),
        "exclude": [
            {
                "start_date": datetime.date(2023, 7, 31),
                "end_date": datetime.date(2023, 8, 20),
            },
        ],
    },
}

activities_df, streams_df = load_data_from_cache()
stop_if_no_activities(activities_df)

with st.sidebar:
    target_label = st.selectbox(label="Select target", options=AVAILABLE_TARGETS.keys())

    target = AVAILABLE_TARGETS[target_label]
    start_date = target["start_date"]
    end_date = target["end_date"]
    target_km = target["target_km"]
    exclude_list = target["exclude"]

    st.write(
        f"""
- 🎯 {target_km} km    
- ⏰ from {start_date.strftime('%d %b %y')} to {end_date.strftime('%d %b %y')}
"""
    )

# %% Format data with pandas
date_range_index = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D",
)
date_range_serie = pd.Series(index=date_range_index, data=date_range_index).dt.date
is_day_active = pd.Series(index=date_range_index, data=True)
for exclusion_period in exclude_list:
    is_day_active = is_day_active & (
        (date_range_serie < exclusion_period["start_date"])
        | (date_range_serie > exclusion_period["end_date"])
    )
target_km_day = target_km / is_day_active.sum()

date_range_df = pd.DataFrame(index=date_range_index).assign(
    target_km_day=is_day_active * target_km_day
)

target_bdc_df = (
    date_range_df.join(
        activities_df.assign(start_date=lambda df: df.start_date.dt.date)
        .groupby("start_date")
        .distance.sum()
    )
    .reset_index(names="date")
    .assign(
        distance=lambda df: df.distance.fillna(0).mask(
            df["date"].dt.date > datetime.datetime.now().date()
        ),
        cum_distance=lambda df: df.distance.cumsum() / 1000,
        cum_target=lambda df: df.target_km_day.cumsum(),
        delta=lambda df: (df.cum_distance - df.cum_target),
        delta_color=lambda df: df.delta.map(
            lambda x: POSITIVE_COLOR if x >= 0 else NEGATIVE_COLOR
        ),
        tooltip_distance=lambda df: df.cum_distance.map(lambda x: f"{x:.2f} km"),
        tooltip_target=lambda df: df.cum_target.map(lambda x: f"{x:.2f} km"),
        tooltip_delta=lambda df: df.delta.map(lambda x: f"{x:.2f} km"),
        tooltip_percent_target=lambda df: df.cum_distance.map(
            lambda x: f"{x / target_km * 100:.2f} %"
        ),
    )
)

# %% Progress bar
total_km = target_bdc_df.distance.sum() / 1000
percentage_progress = total_km / target_km
status_emojy = (
    "✅"
    if percentage_progress >= 1
    else ("❌" if end_date < datetime.datetime.now().date() else "⏳")
)
st.progress(
    text=f"{status_emojy} {100 * percentage_progress:.2f}% ({total_km:.2f}km / {target_km:.2f}km)",
    value=min(1.0, percentage_progress),
)

# %% Graph
end_date_plus_1 = end_date + datetime.timedelta(days=1)
x_axis_domain = [
    {"year": start_date.year, "month": start_date.month, "date": start_date.day},
    {
        "year": end_date_plus_1.year,
        "month": end_date_plus_1.month,
        "date": end_date_plus_1.day,
    },
]
date_x_axis = alt.X(
    "date:T",
    scale=alt.Scale(domain=x_axis_domain),
    title="Date",
)

base = alt.Chart(target_bdc_df).encode(
    x=date_x_axis.title("").axis(labels=False, grid=True),
    tooltip=[
        alt.Tooltip("date:T", title="Date"),
        alt.Tooltip("tooltip_distance:N", title="Realized"),
        alt.Tooltip("tooltip_target:N", title="Planned"),
        alt.Tooltip("tooltip_delta:N", title="Δ"),
        alt.Tooltip("tooltip_percent_target:N", title="% Target"),
    ],
)

# %% Sub charts
realized_chart = base.mark_area(line=True, interpolate="linear").encode(
    y=alt.Y("cum_distance:Q").title("Distance (km)")
)

target_chart = base.mark_line(color=TARGET_COLOR).encode(
    y=alt.Y("cum_target:Q").title("")
)

delta_chart = base.mark_area(interpolate="linear").encode(
    x=date_x_axis.axis(labels=True, grid=True),
    y=alt.Y("delta:Q").title("Δ (km)"),
    fill=alt.Color("delta_color:N", scale=None),
)

# %% Vertical line selector
nearest = alt.selection_point(
    nearest=True,
    on="mouseover",
    fields=["date"],
    empty=False,
)
selectors = base.mark_point().encode(opacity=alt.value(0)).add_params(nearest)

vertical_line_rule = (
    base.mark_rule(strokeWidth=6)
    .encode(color=alt.Color("delta_color:N", scale=None))
    .transform_filter(nearest)
)

realized_circle = realized_chart.mark_circle(
    opacity=1, size=80, color="white"
).transform_filter(nearest)
realized_point = realized_chart.mark_point(
    opacity=1, size=80, strokeWidth=3
).transform_filter(nearest)
target_circle = target_chart.mark_circle(
    opacity=1, size=80, color="white"
).transform_filter(nearest)
target_point = target_chart.mark_point(
    color=TARGET_COLOR, opacity=1, size=80, strokeWidth=3
).transform_filter(nearest)

vertical_line_selection = (
    selectors
    + vertical_line_rule
    + realized_circle
    + realized_point
    + target_circle
    + target_point
)


# %% Final and rendering
top_chart = (realized_chart + target_chart + vertical_line_selection).properties(
    width=900, height=340
)
bottom_chart = (delta_chart + vertical_line_rule).properties(width=900, height=90)

final_chart = (
    (top_chart & bottom_chart)
    .interactive()
    .properties(title="Volume (km) Burn-up Chart")
)

st.altair_chart(final_chart, use_container_width=True)
