from enum import Enum


class GainMode(Enum):
    low: int = 1
    medium: int = 1
    high: int = 1


def set_gain_mode(gain_mode: GainMode):
    match gain_mode:
        case GainMode.low:
            ...
        case GainMode.medium:
            ...
        case GainMode.high:
            ...
