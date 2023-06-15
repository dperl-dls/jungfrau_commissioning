from __future__ import annotations

from pathlib import Path

from artemis.external_interaction.nexus.write_nexus import NexusWriter
from bluesky.callbacks import CallbackBase
from nexgen.nxs_utils import Attenuator, Axis, Beam, Detector, Goniometer, Source
from nexgen.nxs_utils.Detector import JungfrauDetector
from scanspec.core import Path as ScanPath
from scanspec.specs import Line

from jungfrau_commissioning.utils.log import LOGGER
from jungfrau_commissioning.utils.params import RotationScanParameters


def create_detector_parameters(params: RotationScanParameters) -> Detector:
    """Returns the detector information in a format that nexgen wants.

    Args:
        detector_params (DetectorParams): The detector params as Artemis stores them.

    Returns:
        Detector: Detector description for nexgen.
    """
    jf_params = JungfrauDetector(
        "Jungfrau 1M",
        (1024, 1024),
        "Si",
        999999999,  # Overload TODO
        0,
    )

    detector_axes = [
        Axis(
            "det_z",
            ".",
            "translation",
            (0.0, 0.0, 1.0),
            100,  # TODO get distance
        )
    ]
    # Eiger parameters, axes, beam_center, exp_time, [fast, slow]
    return Detector(
        jf_params,
        detector_axes,
        [0, 0],  # Beam centre TODO
        params.exposure_time_s,
        [(-1.0, 0.0, 0.0), (0.0, -1.0, 0.0)],
    )


def create_I24_VGonio_axes(
    params: RotationScanParameters,
    scan_points: dict,
    x_y_z_increments: tuple[float, float, float] = (0.0, 0.0, 0.0),
):
    gonio_axes = [
        Axis("omega", ".", "rotation", (-1.0, 0.0, 0.0), params.omega_start_deg),
        Axis(
            name="sam_z",
            depends="omega",
            transformation_type="translation",
            vector=(0.0, 0.0, 1.0),
            start_pos=0.0,
            increment=x_y_z_increments[2],
        ),
        Axis(
            name="sam_y",
            depends="sam_z",
            transformation_type="translation",
            vector=(0.0, 1.0, 0.0),
            start_pos=0.0,
            increment=x_y_z_increments[1],
        ),
        Axis(
            name="sam_x",
            depends="sam_y",
            transformation_type="translation",
            vector=(1.0, 0.0, 0.0),
            start_pos=0.0,
            increment=x_y_z_increments[0],
        ),
        Axis("chi", "sam_x", "rotation", (0.006, -0.0264, 0.9996), 0.0),
        Axis("phi", "chi", "rotation", (-1, -0.0025, -0.0056), 0.0),
    ]
    return Goniometer(gonio_axes, scan_points)


class JFRotationNexusWriter(NexusWriter):
    def __init__(
        self,
        parameters: RotationScanParameters,
        wavelength: float,
        flux: float,
        transmission: float,
    ) -> None:
        self.detector = create_detector_parameters(parameters)
        self.beam, self.attenuator = (
            Beam(wavelength, flux),
            Attenuator(transmission),
        )
        self.source = Source("I24")
        self.directory = Path(parameters.storage_directory)
        self.filename = parameters.nexus_filename
        self.start_index = 0
        self.full_num_of_images = parameters.get_num_images()
        self.nexus_file = self.directory / f"{parameters.nexus_filename}.nxs"
        self.master_file = self.directory / f"{parameters.nexus_filename}_master.h5"

        scan_spec = Line(
            axis="omega",
            start=parameters.omega_start_deg,
            stop=(parameters.scan_width_deg + parameters.omega_start_deg),
            num=parameters.get_num_images(),
        )
        scan_path = ScanPath(scan_spec.calculate())
        self.scan_points: dict = scan_path.consume().midpoints
        self.goniometer = create_I24_VGonio_axes(parameters, self.scan_points)

    def _get_data_shape_for_vds(self) -> tuple[int, ...]:
        nexus_detector_params: JungfrauDetector = self.detector.detector_params
        return (self.full_num_of_images, *nexus_detector_params.image_size)


class NexusFileHandlerCallback(CallbackBase):
    """Callback class to handle the creation of Nexus files based on experiment \
    parameters. Initialises on recieving a 'start' document for the \
    'rotation_scan_with_cleanup' sub plan, which must also contain the run parameters, \
    as metadata under the 'rotation_scan_params' key.

    To use, subscribe the Bluesky RunEngine to an instance of this class.
    E.g.:
        nexus_file_handler_callback = NexusFileHandlerCallback(parameters)
        RE.subscribe(nexus_file_handler_callback)
    Or decorate a plan using bluesky.preprocessors.subs_decorator.

    See: https://blueskyproject.io/bluesky/callbacks.html#ways-to-invoke-callbacks

    """

    nexus_writer: JFRotationNexusWriter

    def start(self, doc: dict):
        if doc.get("subplan_name") == "rotation_scan_with_cleanup":
            LOGGER.info(
                "Nexus writer recieved start document with experiment parameters."
            )
            json_params = doc.get("rotation_scan_params")
            assert json_params is not None
            self.parameters = RotationScanParameters(**json_params)
            self.run_start_uid = doc.get("uid")

    def stop(self, doc: dict):
        if (
            self.run_start_uid is not None
            and doc.get("run_start") == self.run_start_uid
        ):
            LOGGER.info("Updating Nexus file timestamps.")
            assert (
                self.nexus_writer is not None
            ), "Failed to update Nexus file timestamp, writer was not initialised."
            self.nexus_writer.update_nexus_file_timestamp()
