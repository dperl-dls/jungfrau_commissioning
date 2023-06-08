from enum import Enum

from jungfrau_commissioning.utils.log import LOGGER


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
        case _:
            LOGGER.warn("Unrecognised gain mode!")
