from datetime import datetime
from enum import Enum
from pathlib import Path

from bluesky.plan_stubs import abs_set, rd, sleep
from dodal.devices.i24.jungfrau import JungfrauM1

from jungfrau_commissioning.plans.jungfrau_plans import setup_detector
from jungfrau_commissioning.utils.log import LOGGER


class GainMode(str, Enum):
    dynamic = "dynamic"
    forceswitchg1 = "forceswitchg1"
    forceswitchg2 = "forceswitchg2"


def date_time_string():
    return datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%s")


def set_gain_mode(
    jungfrau: JungfrauM1, gain_mode: GainMode, wait=True, check_for_errors=True
):
    LOGGER.info(f"Setting gain mode {gain_mode.value}")
    yield from abs_set(jungfrau.gain_mode, gain_mode.value, wait=wait)
    if check_for_errors:
        err: str = rd(jungfrau.error_rbv)
        LOGGER.warn(f"JF reporting error: {err}")


def do_dark_acquisition(jungfrau: JungfrauM1, exp_time_s, acq_time_s, n_frames):
    LOGGER.info("Setting up detector:")
    # TODO SOMETHING WITH ZEBRA GOES HERE
    yield from setup_detector(jungfrau, exp_time_s, acq_time_s, n_frames, wait=True)
    yield from abs_set(jungfrau.acquire_start, 1)
    yield from sleep(exp_time_s * n_frames)


def do_darks(
    jungfrau: JungfrauM1,
    directory: str = "/tmp/",
    check_for_errors=True,
):
    directory_prefix = Path(directory) / f"{date_time_string()}_darks"

    # Gain 0
    yield from set_gain_mode(
        jungfrau, GainMode.dynamic, check_for_errors=check_for_errors
    )
    yield from abs_set(
        jungfrau.file_directory,
        (directory_prefix / "G0").as_posix(),
    )
    yield from do_dark_acquisition(jungfrau, 0.001, 0.001, 1000)

    # Gain 1
    yield from set_gain_mode(
        jungfrau, GainMode.forceswitchg1, check_for_errors=check_for_errors
    )
    yield from abs_set(
        jungfrau.file_directory,
        (directory_prefix / "G1").as_posix(),
    )
    yield from do_dark_acquisition(jungfrau, 0.001, 0.01, 1000)

    # Gain 2
    yield from set_gain_mode(
        jungfrau, GainMode.forceswitchg2, check_for_errors=check_for_errors
    )
    yield from abs_set(
        jungfrau.file_directory,
        (directory_prefix / "G2").as_posix(),
    )
    yield from do_dark_acquisition(jungfrau, 0.001, 0.01, 1000)
