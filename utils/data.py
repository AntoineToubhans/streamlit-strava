import datetime
from typing import Any

import pandas as pd
import streamlit as st

DAY = "Day"
WEEK = "Week"
MONTH = "Month"
QUARTER = "Quarter"
YEAR = "Year"

MAX_SPEED_RANGE = datetime.time(minute=2, second=30)
MIN_SPEED_RANGE = datetime.time(minute=8, second=0)


def stop_if_no_activities(activities_df: pd.DataFrame) -> None:
    if activities_df.empty:
        st.warning("No activity found. Download new activities from the 🏠 home page.")
        st.stop()


def get_temporal_grouper(key: str | None = None) -> tuple[pd.Grouper, str]:
    label_freq_grouper: str = st.selectbox(
        label="Frequency",
        options=[DAY, WEEK, MONTH, QUARTER, YEAR],
        key=f"selectbox-{key}" if key else None,
        index=1,  # default is WEEK
    )

    pd_grouper = pd.Grouper(
        key="start_date",
        freq={DAY: "D", WEEK: "W-SUN", MONTH: "M", QUARTER: "Q", YEAR: "Y"}[
            label_freq_grouper
        ],
    )
    alt_timeunit = {
        DAY: "yearmonthdate",
        WEEK: "yearweek",
        MONTH: "yearmonth",
        QUARTER: "yearquarter",
        YEAR: "year",
    }[label_freq_grouper]

    return pd_grouper, alt_timeunit


def st_speed_range_selector(key: str | None = None) -> tuple[float, float]:
    """Returns speed in m.s-1"""
    max_speed_range, min_speed_range = st.slider(
        "Speed Range",
        min_value=MAX_SPEED_RANGE,
        max_value=MIN_SPEED_RANGE,
        value=(MAX_SPEED_RANGE, MIN_SPEED_RANGE),
        format="mm:ss",
        step=datetime.timedelta(seconds=1),
        key=f"slider-{key}" if key else None,
    )

    return (
        1000 / (max_speed_range.minute * 60 + max_speed_range.second),
        1000 / (min_speed_range.minute * 60 + min_speed_range.second),
    )
