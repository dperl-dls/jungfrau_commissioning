from __future__ import annotations

import bluesky.plan_stubs as bps
from dodal.devices.i24.read_only_attenuator import ReadOnlyEnergyAndAttenuator
from dodal.devices.i24.vgonio import VGonio

from jungfrau_commissioning.utils.log import LOGGER


def get_x_y_z(vgonio: VGonio):
    """Returns a tuple of current (x, y, z) read from EPICS"""
    x = yield from bps.rd(vgonio.x)
    y = yield from bps.rd(vgonio.yh)
    z = yield from bps.rd(vgonio.z)
    LOGGER.info(f"Read current x, yh, z: {(x,y,z)}")
    return (x, y, z)


def get_beam_parameters(ro_energ_atten: ReadOnlyEnergyAndAttenuator):
    """Returns a tuple of (transmission, wavelength, energy, intensity),
    read from EPICS"""
    transmission = yield from bps.rd(ro_energ_atten.transmission)
    wavelength = yield from bps.rd(ro_energ_atten.wavelength)
    energy = yield from bps.rd(ro_energ_atten.energy)
    intensity = yield from bps.rd(ro_energ_atten.intensity)
    LOGGER.info(f"Read current x, yh, z: {(transmission,wavelength,energy,intensity,)}")
    return (
        transmission,
        wavelength,
        energy,
        intensity,
    )
