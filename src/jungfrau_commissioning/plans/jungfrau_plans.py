from __future__ import annotations

import bluesky.plan_stubs as bps
from dodal.devices.i24.jungfrau import JungfrauM1

from jungfrau_commissioning.utils.log import LOGGER


def setup_detector(
    jungfrau: JungfrauM1,
    exposure_time_s: float,
    acquire_time_s: float,
    n_images: float,
    group="setup_detector",
    wait=True,
):
    yield from check_and_clear_errors(jungfrau)
    LOGGER.info(
        f"Setting exposure time: {exposure_time_s} s, "
        f"acquire period: {acquire_time_s} s, "
        f"frame_count: {n_images}."
    )
    yield from bps.abs_set(jungfrau.exposure_time_s, exposure_time_s, group=group)
    yield from bps.abs_set(
        jungfrau.acquire_period_s,
        acquire_time_s / 1e6,
        group=group,
    )
    yield from bps.abs_set(
        jungfrau.frame_count,
        n_images,
        group=group,
    )
    if wait:
        yield from bps.wait(group)


def check_and_clear_errors(jungfrau: JungfrauM1):
    LOGGER.info("Checking and clearing errors")
    err: str = bps.rd(jungfrau.error_rbv)
    LOGGER.info(f"    reporting error: {err}")
    yield from bps.abs_set(jungfrau.clear_error, 1, wait=True)
