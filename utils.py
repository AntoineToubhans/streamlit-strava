from constants import Z_1_2, Z_2_3, Z_3_4, Z_4_5, Z_5_6, Z_6_7


def get_zone(speed_in_ms: int | float) -> str:
    match speed_in_ms:
        case speed_in_ms if speed_in_ms > Z_6_7:
            return "Z7"
        case speed_in_ms if speed_in_ms > Z_5_6:
            return "Z6"
        case speed_in_ms if speed_in_ms > Z_4_5:
            return "Z5"
        case speed_in_ms if speed_in_ms > Z_3_4:
            return "Z4"
        case speed_in_ms if speed_in_ms > Z_2_3:
            return "Z3"
        case speed_in_ms if speed_in_ms > Z_1_2:
            return "Z2"
        case _:
            return "Z1"


def format_speed_ms_to_per_km_str(speed_in_ms: int | float) -> str:
    speed_in_sec_per_km = 1000 / speed_in_ms
    if speed_in_ms > 10 * 60 * 60:
        raise ValueError(f"Input speed > 1 hour per km")

    raw_minutes, raw_seconds = divmod(speed_in_sec_per_km, 60)
    minutes = int(raw_minutes)
    seconds = int(raw_seconds)

    return f"{minutes}:{seconds:02}"
