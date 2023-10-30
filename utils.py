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
