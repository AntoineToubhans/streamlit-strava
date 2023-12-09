import time
import pandas as pd
from stravalib import Client as StravaClient
import streamlit as st

from constants import DATA_PATH, STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET
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


# %% ----- Stava utils
def _get_strava_code() -> str | None:
    strava_codes = st.experimental_get_query_params().get("code")
    if strava_codes is None or strava_codes == []:
        return None
    strava_code = strava_codes[0]
    if strava_code == "":
        return None
    return strava_code


@st.cache_resource
def _get_strava_client() -> StravaClient:
    return StravaClient()


def get_strava_client() -> StravaClient:
    client = _get_strava_client()

    if not client.access_token:
        strava_code = _get_strava_code()
        if strava_code:
            try:
                token_response = client.exchange_code_for_token(
                    client_id=STRAVA_CLIENT_ID,
                    client_secret=STRAVA_CLIENT_SECRET,
                    code=strava_code,
                )
                client.access_token = token_response["access_token"]
                client.refresh_token = token_response["refresh_token"]
                client.expires_at = token_response["expires_at"]
            except Exception:
                st.experimental_set_query_params(code="")
                st.rerun()
    else:
        if time.time() > client.expires_at:
            token_response = client.refresh_access_token(
                client_id=STRAVA_CLIENT_ID,
                client_secret=STRAVA_CLIENT_SECRET,
                refresh_token=client.refresh_token,
            )
            client.access_token = token_response["access_token"]
            client.refresh_token = token_response["refresh_token"]
            client.expires_at = token_response["expires_at"]

    return client


def st_strava_authorization_button(label: str, redirect_uri: str) -> None:
    client = _get_strava_client()

    strava_authorization_url = client.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri=redirect_uri,
    )

    st.markdown(
        f"""
    <a href='{strava_authorization_url}' target="_self">
        <button
            style='
                background-color: #fc5200;
                border: 1px solid #fc5200;
                color: #fff;
                border-radius: 4px;
                padding: 5px 10px;
                margin: 10px 0;
            '
        >
            {label}
        </button>
    </a>
        """,
        unsafe_allow_html=True,
    )
