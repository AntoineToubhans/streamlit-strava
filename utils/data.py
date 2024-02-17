from typing import Any

import pandas as pd
import streamlit as st

DAY = "Day"
WEEK = "Week"
MONTH = "Month"
QUARTER = "Quarter"
YEAR = "Year"


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
