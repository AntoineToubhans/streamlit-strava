import pandas as pd
import streamlit as st

st.title("Strava-data app")

activities_df = pd.read_csv("activities.csv", index_col=0, parse_dates=["start_date"])
streams_df = pd.read_csv("streams.csv", index_col=0)

label_freq_grouper = st.selectbox(label="Group by", options=["Week", "Month", "Year"])
freq_grouper = {"Week": "W-SUN", "Month": "M", "Year": "Y"}[label_freq_grouper]

distance_per_week = (
    activities_df
    .groupby(pd.Grouper(key="start_date", freq=freq_grouper))
    .distance.sum()
)
st.bar_chart(distance_per_week)
