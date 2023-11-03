from stravalib import Client
from tqdm import tqdm
import pandas as pd
import yaml

from constants import DATA_PATH, STRAVA_PARAMS_FILE


# %%
DATA_PATH.mkdir(exist_ok=True)


# %%
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
print(
    "\033[92m >\033[00m Go to the following url and get the code from the url in response"
)
print(80 * "=")
print(url)
print(80 * "=")
strava_code = input(" \033[92m >\033[00m Code ? ")

# %%
token_response = client.exchange_code_for_token(
    client_id=STRAVA_CLIENT_ID,
    client_secret=STRAVA_CLIENT_SECRET,
    code=strava_code,
)


# %% Get activities
STRAVA_RUN_SPORT_TYPE = "Run"
START_DATE = "2021-01-01T00:00:00Z"

activities = [
    activity
    for activity in client.get_activities(after=START_DATE, limit=None)
    if activity.sport_type == STRAVA_RUN_SPORT_TYPE
]

print(f"Collected {len(activities)} activities")


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
        for activity in activities
    ]
).to_csv(DATA_PATH / "activities.csv")


# %% Collect data streams and save to cache
STRAVA_STREAM_TYPES = ["time", "heartrate", "velocity_smooth"]

for activity in tqdm(activities, desc="Collecting streams"):
    activity_streams_file = DATA_PATH / f"{activity.id}.csv"

    if activity_streams_file.exists():  # file already in cache
        continue
    if activity.sport_type != STRAVA_RUN_SPORT_TYPE:  # not a running activity
        continue

    activity_streams = client.get_activity_streams(
        activity_id=activity.id,
        types=STRAVA_STREAM_TYPES,
    )

    pd.DataFrame(
        {
            key: activity_streams[key].data
            for key in ["distance", *STRAVA_STREAM_TYPES]
            if key in activity_streams.keys()
        }
    ).to_csv(activity_streams_file)
