from pathlib import Path
import yaml

# ------ Data
DATA_PATH = Path("./cache")
STRAVA_PARAMS_FILE = "strava.yaml"

with open(STRAVA_PARAMS_FILE) as f:
    STRAVA_PARAMS = yaml.safe_load(f)

STRAVA_CLIENT_ID = STRAVA_PARAMS["client_id"]
STRAVA_CLIENT_SECRET = STRAVA_PARAMS["client_secret"]


# ------ Running
VMA_KMH = 18.5  # km/h
VMA = VMA_KMH * 1000 / 3600
