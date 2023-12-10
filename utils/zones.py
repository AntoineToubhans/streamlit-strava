from constants import VMA

SPEED_ZONE_1_2 = 0.61 * VMA  # Z1 = EF
SPEED_ZONE_2_3 = 0.75 * VMA  # Z2 = Footing
SPEED_ZONE_3_4 = 0.85 * VMA  # Z3 = Seuil Anaerobie
SPEED_ZONE_4_5 = 0.92 * VMA  # Z4 = AS 10
SPEED_ZONE_5_6 = 0.97 * VMA  # Z5 = VMA Longue
SPEED_ZONE_6_7 = 1.05 * VMA  # Z6 = VMA Moy / Z7 = VM Courte


def format_speed_ms_to_per_km_str(speed_in_ms: int | float) -> str:
    speed_in_sec_per_km = 1000 / speed_in_ms
    if speed_in_ms > 10 * 60 * 60:
        raise ValueError(f"Input speed > 1 hour per km")

    raw_minutes, raw_seconds = divmod(speed_in_sec_per_km, 60)
    minutes = int(raw_minutes)
    seconds = int(raw_seconds)

    return f"{minutes}:{seconds:02}"


SPEED_ZONE_1_2_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_1_2)
SPEED_ZONE_2_3_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_2_3)
SPEED_ZONE_3_4_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_3_4)
SPEED_ZONE_4_5_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_4_5)
SPEED_ZONE_5_6_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_5_6)
SPEED_ZONE_6_7_STR = format_speed_ms_to_per_km_str(SPEED_ZONE_6_7)


def get_speed_zone_label(speed_in_ms: int | float) -> str:
    match speed_in_ms:
        case speed_in_ms if speed_in_ms > SPEED_ZONE_6_7:
            return f"Z7 (> {SPEED_ZONE_6_7_STR})"
        case speed_in_ms if speed_in_ms > SPEED_ZONE_5_6:
            return f"Z6 ({SPEED_ZONE_5_6_STR}-{SPEED_ZONE_6_7_STR})"
        case speed_in_ms if speed_in_ms > SPEED_ZONE_4_5:
            return f"Z5 ({SPEED_ZONE_4_5_STR}-{SPEED_ZONE_5_6_STR})"
        case speed_in_ms if speed_in_ms > SPEED_ZONE_3_4:
            return f"Z4 ({SPEED_ZONE_3_4_STR}-{SPEED_ZONE_4_5_STR})"
        case speed_in_ms if speed_in_ms > SPEED_ZONE_2_3:
            return f"Z3 ({SPEED_ZONE_2_3_STR}-{SPEED_ZONE_3_4_STR})"
        case speed_in_ms if speed_in_ms > SPEED_ZONE_1_2:
            return f"Z2 ({SPEED_ZONE_1_2_STR}-{SPEED_ZONE_2_3_STR})"
        case _:
            return f"Z1 (<{SPEED_ZONE_1_2_STR})"
