import streamlit as st

from data_utils import load_data


st.set_page_config(layout="wide")

activities_df, streams_df = load_data()

st.title("Strava Data App")

st.success(f"Successfully loaded data")
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
