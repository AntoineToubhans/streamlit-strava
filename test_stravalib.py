from datetime import timedelta

from stravalib import Client
from tqdm import tqdm
import pandas as pd
import yaml

from constants import Z_1_2, Z_2_3, Z_3_4, Z_4_5, Z_5_6, Z_6_7


# %%
STRAVA_PARAMS_FILE = "strava.yaml"

with open(STRAVA_PARAMS_FILE) as f:
    STRAVA_PARAMS = yaml.safe_load(f)

STRAVA_CLIENT_ID = STRAVA_PARAMS["client_id"]
STRAVA_CLIENT_SECRET = STRAVA_PARAMS["client_secret"]


# %%
client = Client()

# %%
url = client.authorization_url(
    client_id=STRAVA_CLIENT_ID,
    redirect_uri="http://127.0.0.1:5000/authorization",
)

# %% go to url and get code from response
strava_code = "8ab826b5b898de93325c8badb2eef419faacd4e3"

token_response = client.exchange_code_for_token(
    client_id=STRAVA_CLIENT_ID,
    client_secret=STRAVA_CLIENT_SECRET,
    code=strava_code,
)

access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]  # You'll need this in 6 hours

# %%
current_athlete = client.get_athlete()

# %% ------------------------ Construire un gros df avec toutes mes datas
STRAVA_STREAM_TYPES = ["time", "heartrate", "velocity_smooth"]
STRAVA_RUN_SPORT_TYPE = "Run"
START_DATE = "2021-01-01T00:00:00Z"

activities = [
    activity
    for activity in client.get_activities(after=START_DATE, limit=None)
    if activity.sport_type == STRAVA_RUN_SPORT_TYPE
]

print(f"Collected {len(activities)} activities")

# %%
activities_df = pd.DataFrame(
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
            "name": activity.name,
            "start_date": activity.start_date,
        }
        for activity in activities
    ]
)

activities_df.to_csv("activities.csv")


# %%
def get_stream_df_from_strava_activity(activity):
    activity_streams = client.get_activity_streams(
        activity_id=activity.id, types=STRAVA_STREAM_TYPES
    )

    return pd.DataFrame(
        {
            key: activity_streams[key].data
            for key in ["distance", *STRAVA_STREAM_TYPES]
            if key in activity_streams.keys()
        }
    ).assign(activity_id=activity.id)


# Cache results to avoid stravalib.exc.RateLimit (max 100 requests every 15 minutes)
streams_cache = dict()

# %%
for activity in tqdm(activities, desc="Collecting streams"):
    if activity.id in streams_cache.keys():
        continue
    if activity.sport_type != STRAVA_RUN_SPORT_TYPE:
        continue
    streams_cache[activity.id] = get_stream_df_from_strava_activity(activity)

# %%
streams_df = pd.concat(streams_cache.values())
print(f"Collected {len(streams_df)} stream data points")

# %%
streams_df.to_csv("streams.csv")


# %%
frac_z1 = (streams_df.velocity_smooth <= Z_1_2).mean()
frac_z2 = (
    (streams_df.velocity_smooth >= Z_1_2) & (streams_df.velocity_smooth <= Z_2_3)
).mean()
frac_z3 = (
    (streams_df.velocity_smooth >= Z_2_3) & (streams_df.velocity_smooth <= Z_3_4)
).mean()
frac_z4 = (
    (streams_df.velocity_smooth >= Z_3_4) & (streams_df.velocity_smooth <= Z_4_5)
).mean()
frac_z5 = (
    (streams_df.velocity_smooth >= Z_4_5) & (streams_df.velocity_smooth <= Z_5_6)
).mean()
frac_z6 = (
    (streams_df.velocity_smooth >= Z_5_6) & (streams_df.velocity_smooth <= Z_6_7)
).mean()
frac_z7 = (streams_df.velocity_smooth > Z_6_7).mean()

print(f"Z1: {frac_z1 * 100: .2f} %")
print(f"Z1->Z2: ", timedelta(seconds=1000 / Z_1_2), "/ km")
print(f"Z2: {frac_z2 * 100: .2f} %")
print(f"Z2->Z3: ", timedelta(seconds=1000 / Z_2_3), "/ km")
print(f"Z3: {frac_z3 * 100: .2f} %")
print(f"Z3->Z4: ", timedelta(seconds=1000 / Z_3_4), "/ km")
print(f"Z4: {frac_z4 * 100: .2f} %")
print(f"Z4->Z5: ", timedelta(seconds=1000 / Z_4_5), "/ km")
print(f"Z5: {frac_z5 * 100: .2f} %")
print(f"Z5->Z6: ", timedelta(seconds=1000 / Z_5_6), "/ km")
print(f"Z6: {frac_z6 * 100: .2f} %")
print(f"Z6->Z7: ", timedelta(seconds=1000 / Z_6_7), "/ km")
print(f"Z7: {frac_z7 * 100: .2f} %")
