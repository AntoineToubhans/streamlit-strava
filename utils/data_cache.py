import time
from pathlib import Path

import pandas as pd
import stravalib.model
from stqdm import stqdm
import streamlit as st

from constants import (
    DATA_PATH,
    DOWNLOAD_LIMIT,
    STRAVA_FIRST_ACTIVITY_START_DATE,
    STRAVA_RUN_SPORT_TYPES,
    STRAVA_STREAM_TYPES,
)
from utils.strava import get_strava_client
from utils.zones import get_speed_zone_label


ACTIVITIES_FILEPATH = DATA_PATH / "activities.csv"


@st.cache_data
def load_data_from_cache() -> tuple[pd.DataFrame, pd.DataFrame]:
    if not ACTIVITIES_FILEPATH.exists():
        return pd.DataFrame(), pd.DataFrame()

    activities = pd.read_csv(
        ACTIVITIES_FILEPATH, index_col=0, parse_dates=["start_date"]
    )

    if activities.empty:
        return activities, pd.DataFrame()

    streams = pd.concat(
        [
            pd.read_csv(DATA_PATH / f"{activity_id}.csv", index_col=0).assign(
                activity_id=activity_id
            )
            for activity_id in activities.id.unique()
        ]
    ).assign(speed_zone=lambda df: df.velocity_smooth.map(get_speed_zone_label))

    return activities, streams


def _get_streams_file(activity: stravalib.model.Activity) -> Path:
    return DATA_PATH / f"{activity.id}.csv"


def update_cache() -> None:
    DATA_PATH.mkdir(exist_ok=True)
    strava_client = get_strava_client()

    # 1. Get all activities
    st.info("Download activities from Strava ...")
    activities = [
        activity
        for activity in strava_client.get_activities(
            after=STRAVA_FIRST_ACTIVITY_START_DATE, limit=None
        )
        if activity.sport_type in STRAVA_RUN_SPORT_TYPES
    ]

    st.success(f"Found (total) {len(activities)} activities.")

    # 2. Download missing activity streams
    activities_to_be_downloaded, activities_already_in_cache = [], []
    for activity in activities:
        (activities_to_be_downloaded, activities_already_in_cache)[
            _get_streams_file(activity).exists()
        ].append(activity)

    st.info(f"{len(activities_already_in_cache)} already in cache.")

    if len(activities_to_be_downloaded) > DOWNLOAD_LIMIT:
        st.warning(
            f"Too much activities to be downloaded: it will download {DOWNLOAD_LIMIT} first, hit the download button later for the rest"
        )
        activities_to_be_downloaded = activities_to_be_downloaded[:DOWNLOAD_LIMIT]

    st.info(f"Downloading data for {len(activities_to_be_downloaded)} activities ...")

    # 2.1 Write stream csv files
    for activity in stqdm(activities_to_be_downloaded, desc="Collecting streams"):
        activity_streams = strava_client.get_activity_streams(
            activity_id=activity.id,
            types=STRAVA_STREAM_TYPES,
        )

        (
            pd.DataFrame(
                {
                    key: activity_streams[key].data
                    for key in ["distance", *STRAVA_STREAM_TYPES]
                    if key in activity_streams.keys()
                }
            )
            .pipe(
                lambda df: df.join(
                    df.latlng.apply(pd.Series).rename(
                        columns={0: "latitude", 1: "longitude"}
                    )
                )
            )
            .drop(columns=["latlng"])
            .to_csv(_get_streams_file(activity))
        )

    # 2.2 Write activities.csv file after, to keep file consistencies
    pd.DataFrame(
        [
            {
                "id": activity.id,
                "average_cadence": activity.average_cadence,
                "average_heartrate": activity.average_heartrate,
                "average_speed": activity.average_speed.num,
                "description": activity.description,
                "distance": activity.distance.num,
                "elapsed_time": activity.elapsed_time.seconds,
                "kudos_count": activity.kudos_count,
                "max_heartrate": activity.max_heartrate,
                "moving_time": activity.moving_time.seconds,
                "name": activity.name,
                "start_date": activity.start_date,
            }
            for activity in activities_already_in_cache + activities_to_be_downloaded
        ]
    ).to_csv(ACTIVITIES_FILEPATH)

    st.success(f"Downloaded data for {len(activities_to_be_downloaded)} activities.")

    # 3. Clear cache and rerun
    load_data_from_cache.clear()
    st.success("Cache updated! Reloading app in 3 seconds...")

    time.sleep(3)
    st.rerun()
