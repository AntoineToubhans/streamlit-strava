from pathlib import Path

# ------ Data
DATA_PATH = Path("./cache")
STRAVA_PARAMS_FILE = "strava.yaml"


# ------ Running
VMA_KMH = 18.5  # km/h
VMA = VMA_KMH * 1000 / 3600
SEUIL_AEROBIE = 0.78 * VMA
SEUIL_ANAEROBIE = 0.87 * VMA
Z_1_2 = 0.61 * VMA  # Z1 = EF
Z_2_3 = 0.75 * VMA  # Z2 = Footing
Z_3_4 = 0.85 * VMA  # Z3 = Seuil Anaerobie
Z_4_5 = 0.92 * VMA  # Z4 = AS 10
Z_5_6 = 0.97 * VMA  # Z5 = VMA Longue
Z_6_7 = 1.05 * VMA  # Z6 = VMA Moy / Z7 = VM Courte
