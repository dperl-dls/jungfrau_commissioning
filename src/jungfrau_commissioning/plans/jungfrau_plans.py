from __future__ import annotations

import bluesky.plan_stubs as bps
from dodal.devices.i24.jungfrau import JungfrauM1

from jungfrau_commissioning.utils.log import LOGGER


def setup_detector(
    jungfrau: JungfrauM1,
    exposure_time_s: float,
    acquire_time_us: float,
    group="setup_detector",
    wait=True,
):
    yield from check_and_clear_errors(jungfrau)
    LOGGER.info(
        f"Setting exposure time: {exposure_time_s} s, "
        f"acquire period: {acquire_time_us} us"
    )
    yield from bps.abs_set(jungfrau.exposure_time_s, exposure_time_s, group=group)
    yield from bps.abs_set(
        jungfrau.acquire_period_s,
        acquire_time_us / 1e6,
        group=group,
    )


def check_and_clear_errors(jungfrau: JungfrauM1):
    LOGGER.info("Checking and clearing errors")
    err: str = bps.rd(jungfrau.error_rbv)
    LOGGER.info(f"    reporting error: {err}")
    yield from bps.abs_set(jungfrau.ClearError, 1, wait=True)
