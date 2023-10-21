import requests
import urllib3
import yaml

# %%
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# %%
AUTH_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"
STRAVA_PARAMS_FILE = "strava.yaml"

# %%
with open(STRAVA_PARAMS_FILE) as f:
    STRAVA_PARAMS = yaml.safe_load(f)

# %%
PAYLOAD = {
    "client_id": STRAVA_PARAMS["client_id"],
    "client_secret": STRAVA_PARAMS["client_secret"],
    "refresh_token": STRAVA_PARAMS["refresh_token"],
    "grant_type": "refresh_token",
    "f": "json",
}

# %%
print("Requesting Token...\n")
res = requests.post(AUTH_URL, data=PAYLOAD, verify=False)
access_token = res.json()["access_token"]
print("Access Token = {}\n".format(access_token))

# %%
header = {"Authorization": "Bearer " + access_token}
param = {"per_page": 200, "page": 1}
my_dataset = requests.get(ACTIVITIES_URL, headers=header, params=param).json()

# %%
print(my_dataset[0]["name"])
print(my_dataset[0]["map"]["summary_polyline"])
