from __future__ import annotations

from typing import Any, Callable

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from dodal.beamlines import i24
from dodal.devices.eiger import EigerDetector
from dodal.devices.i24.i24_vgonio import VGonio
from dodal.devices.zebra import RotationDirection, Zebra
from ophyd.device import Device
from ophyd.epics_motor import EpicsMotor

from jungfrau_commissioning.plans.zebra import (
    arm_zebra,
    disarm_zebra,
    setup_zebra_for_rotation,
)
from jungfrau_commissioning.utils.log import LOGGER
from jungfrau_commissioning.utils.params import RotationScanParameters


def create_rotation_scan_devices() -> dict[str, Device]:
    """Ensures necessary devices have been instantiated and returns a dict with
    references to them"""
    devices = {
        "eiger": i24.eiger(wait_for_connection=False),
        "gonio": i24.vgonio(),
        "zebra": i24.zebra(),
    }
    return devices


DIRECTION = RotationDirection.NEGATIVE
OFFSET = 1
SHUTTER_OPENING_TIME = 0.5


def cleanup_after_rotation(
    zebra: Zebra,
    group="cleanup_senv",
):
    yield from bps.abs_set(zebra.inputs.soft_in_1, 0, group=group)


def move_to_start_w_buffer(axis: EpicsMotor, start_angle):
    """Move an EpicsMotor 'axis' to angle 'start_angle', modified by an offset and
    against the direction of rotation."""
    # can move to start as fast as possible
    yield from bps.abs_set(axis.velocity, 90, wait=True)
    start_position = start_angle - (OFFSET * DIRECTION)
    LOGGER.info(
        "moving to_start_w_buffer doing: start_angle-(offset*direction)"
        f" = {start_angle} - ({OFFSET} * {DIRECTION} = {start_position}"
    )

    yield from bps.abs_set(axis, start_position, group="move_to_start")


def move_to_end_w_buffer(axis: EpicsMotor, scan_width: float, wait: float = True):
    distance_to_move = (scan_width + 0.1 + OFFSET) * DIRECTION
    LOGGER.info(
        f"Given scan width of {scan_width}, offset of {OFFSET}, direction"
        f" {DIRECTION}, apply a relative set to omega of: {distance_to_move}"
    )
    yield from bps.rel_set(axis, distance_to_move, group="move_to_end", wait=wait)


def set_speed(axis: EpicsMotor, image_width, exposure_time, wait=True):
    speed_for_rotation = image_width / exposure_time
    yield from bps.abs_set(
        axis.velocity, speed_for_rotation, group="set_speed", wait=wait
    )


@bpp.set_run_key_decorator("rotation_scan_main")
@bpp.run_decorator(md={"subplan_name": "rotation_scan_main"})
def rotation_scan_plan(
    params: RotationScanParameters,
    eiger: EigerDetector,
    gonio: VGonio,
    zebra: Zebra,
):
    """A plan to collect diffraction images from a sample continuously rotating about
    a fixed axis - for now this axis is limited to omega."""

    start_angle = params.omega_start_deg
    scan_width = params.scan_width_deg
    image_width = params.image_width_deg
    exposure_time = params.exposure_time_s

    LOGGER.info("setting up and staging eiger")

    LOGGER.info(f"moving omega to beginning, start_angle={start_angle}")
    yield from move_to_start_w_buffer(gonio.omega, start_angle)

    LOGGER.info(
        f"setting up zebra w: start_angle={start_angle}, scan_width={scan_width}"
    )
    yield from setup_zebra_for_rotation(
        zebra,
        start_angle=start_angle,
        scan_width=scan_width,
        direction=DIRECTION,
        shutter_time_and_velocity=(
            SHUTTER_OPENING_TIME,
            image_width / exposure_time,
        ),
        group="setup_zebra",
    )

    LOGGER.info("wait for any previous moves...")
    # wait for all the setup tasks at once
    yield from bps.wait("setup_senv")
    yield from bps.wait("move_to_start")
    yield from bps.wait("setup_zebra")

    LOGGER.info(
        f"setting rotation speed for image_width, exposure_time"
        f" {image_width, exposure_time} to {image_width/exposure_time}"
    )
    yield from set_speed(gonio.omega, image_width, exposure_time, wait=True)

    yield from arm_zebra(zebra)

    LOGGER.info(f"{'increase' if DIRECTION > 0 else 'decrease'} omega by {scan_width}")
    yield from move_to_end_w_buffer(gonio.omega, scan_width)


def cleanup_plan(eiger, zebra, gonio):
    yield from cleanup_after_rotation(zebra)
    yield from bpp.finalize_wrapper(disarm_zebra(zebra), bps.wait("cleanup_senv"))


def get_rotation_scan_plan(params: dict[str, Any], subscriptions: list[Callable]):
    """Call this to get back a plan generator function with attached callbacks and the \
    given parameters.
    Args:
        params: dict obtained by reading a json file conforming to the pydantic \
            schema in ./src/jungfrau_commissioning/utils/params.py.
            see "example_params.json" for an example.
        subscriptions: list of callback functions to attach - probably just \
            [nexus_writer_callback]"""  # TODO params
    devices = create_rotation_scan_devices()

    @bpp.subs_decorator(list(subscriptions))
    def rotation_scan_plan_with_stage_and_cleanup(
        params: RotationScanParameters,
    ):
        # TODO SETUP DETECTOR
        # devices["eiger"].set_detector_parameters(params.artemis_params.detector_params)

        # @bpp.stage_decorator([devices["eiger"]])
        @bpp.set_run_key_decorator("rotation_scan_with_cleanup")
        @bpp.run_decorator(md={"subplan_name": "rotation_scan_with_cleanup"})
        @bpp.finalize_decorator(lambda: cleanup_plan(**devices))
        def rotation_with_cleanup_and_stage(params):
            yield from rotation_scan_plan(params, **devices)

        yield from rotation_with_cleanup_and_stage(params)

    return rotation_scan_plan_with_stage_and_cleanup(params)
