from __future__ import annotations

import bluesky.plan_stubs as bps
from dodal.devices.i24.jungfrau import JungfrauM1, TriggerMode

from jungfrau_commissioning.utils.log import LOGGER


def set_hardware_trigger(jungfrau: JungfrauM1):
    LOGGER.info("setting hardware triggered mode")
    yield from bps.abs_set(jungfrau.trigger_mode, TriggerMode.HARDWARE.value)


def set_software_trigger(jungfrau: JungfrauM1):
    yield from bps.abs_set(jungfrau.trigger_mode, TriggerMode.SOFTWARE.value)


def wait_for_writing(jungfrau: JungfrauM1, timeout_s: float):
    # this is currently broken
    yield from bps.sleep(0.2)
    LOGGER.info("waiting for acquire_RBV")
    acquiring = 1
    while acquiring:
        acquiring = yield from bps.rd(jungfrau.acquire_rbv)
        yield from bps.sleep(0.3)
        LOGGER.info(f"{'still' if acquiring else 'stopped'} acquiring")
    LOGGER.info("acquire_RBV low, waiting for writing_RBV")
    time = 0.0
    still_writing = 1
    while time < timeout_s and still_writing:
        still_writing = yield from bps.rd(jungfrau.writing_rbv)
        LOGGER.info(f"{'still' if still_writing else 'stopped'} writing")
        yield from bps.sleep(0.3)
        time += 0.3
    if still_writing:
        raise TimeoutError(f"Acquire did not finish in {timeout_s} s")
    yield from bps.sleep(0.2)


def do_manual_acquisition(
    jungfrau: JungfrauM1,
    exp_time_s: float,
    acq_time_s: float,
    n_frames: int,
    timeout_times: float = 3,
):
    LOGGER.info("Setting up detector:")
    yield from setup_detector(jungfrau, exp_time_s, acq_time_s, n_frames, wait=True)
    yield from bps.abs_set(jungfrau.acquire_start, 1, wait=True)
    # yield from wait_for_writing(jungfrau, acq_time_s * n_frames * timeout_times)
    yield from bps.sleep(acq_time_s * n_frames * timeout_times)


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
        acquire_time_s,
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
    LOGGER.info("Checking and clearing errors...")
    err: str = yield from bps.rd(jungfrau.error_rbv)
    if err != "":
        LOGGER.info(f"    reporting error: {err}")
    yield from bps.abs_set(jungfrau.clear_error, 1, wait=True)
