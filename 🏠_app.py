import streamlit as st

from utils.data_cache import load_data_from_cache, update_cache
from utils.strava import get_strava_client, st_strava_authorization_button


st.set_page_config(layout="wide")

activities_df, streams_df = load_data_from_cache()

st.title("Strava Data App")

st_cols = st.columns([2, 2, 3, 3, 3])
st_cols[0].metric(label="Activities", value=len(activities_df))
st_cols[1].metric(label="Point of data", value=len(streams_df))
st_cols[2].metric(
    label="Last activity", value=activities_df.start_date.max().strftime("%d %b %y")
)
st_cols[3].metric(
    label="Total distance", value=f"{activities_df.distance.sum() / 1000:.2f} km"
)
st_cols[4].metric(
    label="Total time", value=f"{activities_df.moving_time.sum() / 3600:.2f} hours"
)
st.write("---")

# % --- Refresh data
st.write("### 🔄 Download activities from Strava")

strava_client = get_strava_client()
strava_user_is_logged_in = strava_client.access_token is not None

st_status_col, st_action_col = st.columns([3, 2])

with st_status_col:
    if strava_user_is_logged_in:
        st.success("Strava connected 🙂")
    else:
        st.error("Strava not connected 😟")

with st_action_col:
    if strava_user_is_logged_in:
        athlete = strava_client.get_athlete()
        st_action_col.markdown(
            f"""
<div style='display: inline;'>
    <img src={athlete.profile} style='width: 56px; border-radius: 50%; margin: 0 10px;'/>
    <span style='font-size: 22px; font-weight: bold;'>{athlete.firstname} {athlete.lastname}</span>
</div>
        """,
            unsafe_allow_html=True,
        )

    else:
        st_strava_authorization_button(
            label="Authorize Strava", redirect_uri="http://localhost:8501"
        )

if st.button(
    label="Download activities", disabled=not strava_user_is_logged_in, type="primary"
):
    update_cache()
