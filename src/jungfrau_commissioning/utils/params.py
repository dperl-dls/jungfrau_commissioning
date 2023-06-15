import json

from dodal.devices.motors import XYZLimitBundle
from dodal.devices.zebra import RotationDirection
from pydantic import BaseModel, validator


class RotationScanParameters(BaseModel):
    """
    Holder class for the parameters of a rotation data collection.
    """

    rotation_axis: str = "omega"
    scan_width_deg: float = 360.0
    image_width_deg: float = 0.1
    omega_start_deg: float = 0.0
    exposure_time_s: float = 0.01
    detector_acquire_time_us: float = 10.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rotation_direction: RotationDirection = RotationDirection.NEGATIVE
    offset_deg: float = 1.0
    shutter_opening_time_s: float = 0.6

    class Config:
        json_encoders = {
            RotationDirection: lambda x: x.name,
        }

    @validator("rotation_direction", pre=True)
    def _parse_direction(cls, rotation_direction: str | int):
        return RotationDirection[rotation_direction]

    @classmethod
    def from_file(cls, filename: str):
        with open(filename) as f:
            raw = json.load(f)
        return cls(**raw)

    def print(self):
        print(self.json(indent=2))

    def xyz_are_valid(self, limits: XYZLimitBundle) -> bool:
        """
        Validates scan location in x, y, and z

        :param limits: The motor limits against which to validate
                       the parameters
        :return: True if the scan is valid
        """
        if not limits.x.is_within(self.x):
            return False
        if not limits.y.is_within(self.y):
            return False
        if not limits.z.is_within(self.z):
            return False
        return True

    def get_num_images(self):
        return int(self.scan_width_deg / self.image_width_deg)
