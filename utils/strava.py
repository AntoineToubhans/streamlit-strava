import time
from stravalib import Client as StravaClient
import streamlit as st

from constants import STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET


@st.cache_resource
def _get_strava_client() -> StravaClient:
    return StravaClient()


def get_strava_client() -> StravaClient:
    client = _get_strava_client()

    if not client.access_token:
        strava_code = st.query_params.get("code")
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
                st.query_params.clear()
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
