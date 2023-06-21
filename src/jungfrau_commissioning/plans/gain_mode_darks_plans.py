from datetime import datetime
from enum import Enum
from pathlib import Path

from bluesky.plan_stubs import abs_set, rd, sleep
from dodal.devices.i24.jungfrau import JungfrauM1

from jungfrau_commissioning.plans.jungfrau_plans import (
    check_and_clear_errors,
    do_manual_acquisition,
    set_software_trigger,
)
from jungfrau_commissioning.utils.log import LOGGER


class GainMode(str, Enum):
    dynamic = "dynamic"
    forceswitchg1 = "forceswitchg1"
    forceswitchg2 = "forceswitchg2"


def date_time_string():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")


def set_gain_mode(
    jungfrau: JungfrauM1,
    gain_mode: GainMode,
    wait=True,
    check_for_errors=True,
    timeout_s=3,
):
    LOGGER.info(f"Setting gain mode {gain_mode.value}")
    yield from abs_set(jungfrau.gain_mode, gain_mode.value, wait=wait)
    time = 0.0
    current_gain_mode = ""
    while current_gain_mode != gain_mode.value and time < timeout_s:
        yield from sleep(0.1)
        current_gain_mode = yield from rd(jungfrau.gain_mode)
        time += 0.1
    if time > timeout_s:
        raise TimeoutError(f"Gain mode change unsuccessful in {timeout_s} seconds")
    if check_for_errors:
        yield from check_and_clear_errors(jungfrau)


def do_darks(
    jungfrau: JungfrauM1,
    directory: str = "/dls/i24/data/2023/cm33852-3/jungfrau_commissioning",
    check_for_errors=True,
):
    directory_prefix = Path(directory) / f"{date_time_string()}_darks"

    # TODO CHECK IF FILES EXIST

    yield from set_software_trigger(jungfrau)

    # Gain 0
    yield from set_gain_mode(
        jungfrau, GainMode.dynamic, check_for_errors=check_for_errors
    )
    yield from abs_set(jungfrau.file_directory, directory_prefix.as_posix(), wait=True)
    yield from abs_set(jungfrau.file_name, "G0", wait=True)
    yield from do_manual_acquisition(jungfrau, 0.001, 0.001, 1000)

    # Gain 1
    yield from set_gain_mode(
        jungfrau, GainMode.forceswitchg1, check_for_errors=check_for_errors
    )
    yield from abs_set(jungfrau.file_name, "G1", wait=True)
    yield from do_manual_acquisition(jungfrau, 0.001, 0.01, 1000)

    # Gain 2
    yield from set_gain_mode(
        jungfrau, GainMode.forceswitchg2, check_for_errors=check_for_errors
    )
    yield from abs_set(jungfrau.file_name, "G2", wait=True)
    yield from do_manual_acquisition(jungfrau, 0.001, 0.01, 1000)

    # Leave on dynamic after finishing
    yield from set_gain_mode(
        jungfrau, GainMode.dynamic, check_for_errors=check_for_errors
    )
