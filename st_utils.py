from typing import Any

import pandas as pd

WEEK = "Week"
MONTH = "Month"
QUARTER = "Quarter"
YEAR = "Year"


def get_temporal_grouper(st_elt: Any, key: str | None = None) -> tuple[pd.Grouper, str]:
    label_freq_grouper: str = st_elt.selectbox(
        label="Group by",
        options=[WEEK, MONTH, QUARTER, YEAR],
        key=f"selectbox-{key}" if key else None,
    )

    pd_grouper = pd.Grouper(
        key="start_date",
        freq={WEEK: "W-SUN", MONTH: "M", QUARTER: "Q", YEAR: "Y"}[label_freq_grouper],
    )
    alt_timeunit = {
        WEEK: "yearweek",
        MONTH: "yearmonth",
        QUARTER: "yearquarter",
        YEAR: "year",
    }[label_freq_grouper]

    return pd_grouper, alt_timeunit
