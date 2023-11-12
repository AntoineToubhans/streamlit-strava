from constants import Z_1_2, Z_2_3, Z_3_4, Z_4_5, Z_5_6, Z_6_7


def format_speed_ms_to_per_km_str(speed_in_ms: int | float) -> str:
    speed_in_sec_per_km = 1000 / speed_in_ms
    if speed_in_ms > 10 * 60 * 60:
        raise ValueError(f"Input speed > 1 hour per km")

    raw_minutes, raw_seconds = divmod(speed_in_sec_per_km, 60)
    minutes = int(raw_minutes)
    seconds = int(raw_seconds)

    return f"{minutes}:{seconds:02}"


Z_1_2_STR = format_speed_ms_to_per_km_str(Z_1_2)
Z_2_3_STR = format_speed_ms_to_per_km_str(Z_2_3)
Z_3_4_STR = format_speed_ms_to_per_km_str(Z_3_4)
Z_4_5_STR = format_speed_ms_to_per_km_str(Z_4_5)
Z_5_6_STR = format_speed_ms_to_per_km_str(Z_5_6)
Z_6_7_STR = format_speed_ms_to_per_km_str(Z_6_7)


def get_zone(speed_in_ms: int | float) -> str:
    match speed_in_ms:
        case speed_in_ms if speed_in_ms > Z_6_7:
            return f"Z7 (> {Z_6_7_STR})"
        case speed_in_ms if speed_in_ms > Z_5_6:
            return f"Z6 ({Z_5_6_STR}-{Z_6_7_STR})"
        case speed_in_ms if speed_in_ms > Z_4_5:
            return f"Z5 ({Z_4_5_STR}-{Z_5_6_STR})"
        case speed_in_ms if speed_in_ms > Z_3_4:
            return f"Z4 ({Z_3_4_STR}-{Z_4_5_STR})"
        case speed_in_ms if speed_in_ms > Z_2_3:
            return f"Z3 ({Z_2_3_STR}-{Z_3_4_STR})"
        case speed_in_ms if speed_in_ms > Z_1_2:
            return f"Z2 ({Z_1_2_STR}-{Z_2_3_STR})"
        case _:
            return f"Z1 (<{Z_1_2_STR})"
