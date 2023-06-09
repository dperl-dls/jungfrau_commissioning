from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

import bluesky.plan_stubs as bps
import bluesky.preprocessors as bpp
from dodal.beamlines import i24
from dodal.devices.i24.jungfrau import JungfrauM1
from dodal.devices.i24.read_only_attenuator import ReadOnlyEnergyAndAttenuator
from dodal.devices.i24.vgonio import VGonio
from dodal.devices.zebra import RotationDirection, Zebra
from ophyd.device import Device
from ophyd.epics_motor import EpicsMotor

from jungfrau_commissioning.callbacks.nexus_writer import NexusFileHandlerCallback
from jungfrau_commissioning.plans.gain_mode_darks_plans import (
    GainMode,
    date_time_string,
    set_gain_mode,
)
from jungfrau_commissioning.plans.jungfrau_plans import (
    set_hardware_trigger,
    setup_detector,
    wait_for_writing,
)
from jungfrau_commissioning.plans.utility_plans import read_beam_parameters, read_x_y_z
from jungfrau_commissioning.plans.zebra_plans import (
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
        "jungfrau": i24.jungfrau(),
        "gonio": i24.vgonio(),
        "zebra": i24.zebra(),
        "beam_params": i24.beam_params(),
    }
    return devices


DIRECTION = RotationDirection.NEGATIVE
SHUTTER_OPENING_TIME = 0.5


def move_to_start_w_buffer(
    axis: EpicsMotor,
    start_angle: float,
    offset: float,
    wait: bool = True,
    direction: RotationDirection = DIRECTION,
):
    """Move an EpicsMotor 'axis' to angle 'start_angle', modified by an offset and
    against the direction of rotation."""
    # can move to start as fast as possible
    yield from bps.abs_set(axis.velocity, 90, wait=True)
    start_position = start_angle - (offset * direction)
    LOGGER.info(
        "moving to_start_w_buffer doing: start_angle-(offset*direction)"
        f" = {start_angle} - ({offset} * {direction}) = {start_position}"
    )

    yield from bps.abs_set(axis, start_position, group="move_to_start", wait=wait)


def move_to_end_w_buffer(
    axis: EpicsMotor,
    scan_width: float,
    offset: float,
    shutter_opening_degrees: float = 2.5,  # default for 100 deg/s
    wait: bool = True,
    direction: RotationDirection = DIRECTION,
):
    distance_to_move = (
        scan_width + shutter_opening_degrees + offset * 2 + 0.1
    ) * direction
    LOGGER.info(
        f"Given scan width of {scan_width}, acceleration offset of {offset}, direction"
        f" {direction}, apply a relative set to omega of: {distance_to_move}"
    )
    yield from bps.rel_set(axis, distance_to_move, group="move_to_end", wait=wait)


@bpp.set_run_key_decorator("rotation_scan_main")
@bpp.run_decorator(md={"subplan_name": "rotation_scan_main"})
def rotation_scan_plan(
    params: RotationScanParameters,
    jungfrau: JungfrauM1,
    gonio: VGonio,
    zebra: Zebra,
    beam_params: ReadOnlyEnergyAndAttenuator,
    directory: Path = Path(
        "/dls/i24/data/2023/cm33852-3/jungfrau_commissioning",
    ),
):
    """A plan to collect diffraction images from a sample continuously rotating about
    a fixed axis - for now this axis is limited to omega."""

    start_angle = params.omega_start_deg
    scan_width = params.scan_width_deg
    image_width = params.image_width_deg
    exposure_time = params.exposure_time_s

    speed_for_rotation_deg_s = image_width / exposure_time
    LOGGER.info(f"calculated speed: {speed_for_rotation_deg_s} deg/s")

    acceleration_offset = 0.15 * speed_for_rotation_deg_s
    LOGGER.info(
        f"calculated rotation offset for acceleration: at {speed_for_rotation_deg_s} "
        f"deg/s, to take 0.15s = {acceleration_offset}"
    )

    shutter_opening_degrees = speed_for_rotation_deg_s * params.shutter_opening_time_s
    LOGGER.info(
        f"calculated degrees rotation needed for shutter: {shutter_opening_degrees} deg"
        f" for {params.shutter_opening_time_s} at {speed_for_rotation_deg_s} deg/s"
    )

    LOGGER.info("setting up jungfrau")

    yield from set_hardware_trigger(jungfrau)
    yield from bps.abs_set(jungfrau.trigger_count, 1)
    yield from setup_detector(
        jungfrau,
        params.exposure_time_s,
        params.acquire_time_s,
        params.get_num_images(),
        wait=True,
    )
    yield from set_gain_mode(jungfrau, GainMode.dynamic)
    yield from bps.abs_set(jungfrau.file_directory, directory.as_posix(), wait=True)
    yield from bps.abs_set(jungfrau.file_name, params.nexus_filename, wait=True)
    LOGGER.info("Setting Acquire to arm detector")
    yield from bps.abs_set(jungfrau.acquire_start, 1)
    yield from bps.sleep(2)

    LOGGER.info("reading current x, y, z and beam parameters")
    # these readings should be recieved by the nexus callback
    yield from read_x_y_z(gonio)
    yield from read_beam_parameters(beam_params)

    LOGGER.info(f"moving omega to beginning, start_angle={start_angle}")
    yield from move_to_start_w_buffer(gonio.omega, start_angle, acceleration_offset)

    LOGGER.info(
        f"setting up zebra w: start_angle={start_angle}, scan_width={scan_width}"
    )
    yield from setup_zebra_for_rotation(
        zebra,
        start_angle=start_angle,
        scan_width=scan_width,
        direction=params.rotation_direction,
        shutter_opening_deg=shutter_opening_degrees,
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
    yield from bps.abs_set(
        gonio.omega.velocity, speed_for_rotation_deg_s, group="set_speed", wait=True
    )
    yield from arm_zebra(zebra)

    LOGGER.info(
        f"{'increase' if DIRECTION > 0 else 'decrease'} omega through {scan_width}"
        "modified by adjustments for shutter speed and acceleration."
    )
    yield from move_to_end_w_buffer(
        gonio.omega,
        scan_width,
        acceleration_offset,
        shutter_opening_degrees,
        wait=False,
    )
    timeout_factor = max(15, 15 * 0.001 / params.acquire_time_s)
    timeout_s = 1 + params.acquire_time_s * params.get_num_images() * timeout_factor
    LOGGER.info(
        f"Waiting for acquisition and writing to complete with a timeout of {timeout_s} s"  # noqa
    )
    # wait for writing
    yield from wait_for_writing(jungfrau, timeout_s)
    yield from bps.wait()
    LOGGER.info("Resetting omega velocity to 100 deg/s")
    yield from bps.abs_set(gonio.omega.velocity, 100, wait=True)


def cleanup_plan(zebra: Zebra, group="cleanup"):
    yield from bps.abs_set(zebra.inputs.soft_in_1, 0, group=group)
    yield from disarm_zebra(zebra)
    yield from bps.wait("cleanup")


def get_rotation_scan_plan(params: RotationScanParameters):
    """Call this to get back a plan generator function with attached callbacks and the \
    given parameters.
    Args:
        params: dict obtained by reading a json file conforming to the pydantic \
            schema in ./src/jungfrau_commissioning/utils/params.py.
            see "example_params.json" for an example."""
    devices = create_rotation_scan_devices()

    params = deepcopy(
        params
    )  # stop us from accidentally resusing this and nesting directories
    params.nexus_filename += f"_scan_{int(params.scan_width_deg)}deg"
    directory = (
        Path(params.storage_directory) / f"{date_time_string()}_{params.nexus_filename}"
    )
    os.makedirs(directory.as_posix())
    params.storage_directory = directory.as_posix()
    # save the params for the run with the data
    with open((directory / "experiment_params.json").as_posix(), "w") as f:
        f.write(params.json(indent=2))

    nexus_writing_callback = NexusFileHandlerCallback()

    def rotation_scan_plan_with_stage_and_cleanup(
        params: RotationScanParameters,
    ):
        @bpp.subs_decorator([nexus_writing_callback])
        @bpp.set_run_key_decorator("rotation_scan_with_cleanup")
        @bpp.run_decorator(
            md={
                "subplan_name": "rotation_scan_with_cleanup",
                "rotation_scan_params": params.json(),
            }
        )
        @bpp.finalize_decorator(lambda: cleanup_plan(devices["zebra"]))
        def rotation_with_cleanup_and_stage(params):
            yield from rotation_scan_plan(params, **devices, directory=directory)

        yield from rotation_with_cleanup_and_stage(params)

    return rotation_scan_plan_with_stage_and_cleanup(params)
