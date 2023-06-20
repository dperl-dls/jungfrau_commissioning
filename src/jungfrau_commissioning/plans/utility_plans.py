from __future__ import annotations

import bluesky.plan_stubs as bps
from dodal.devices.i24.read_only_attenuator import ReadOnlyEnergyAndAttenuator
from dodal.devices.i24.vgonio import VGonio

from jungfrau_commissioning.utils.log import LOGGER


def rd_x_y_z(vgonio: VGonio):
    """Returns a tuple of current (x, y, z) read from EPICS"""
    x = yield from bps.rd(vgonio.x)
    y = yield from bps.rd(vgonio.yh)
    z = yield from bps.rd(vgonio.z)
    LOGGER.info(f"Read current x, yh, z: {(x, y, z)}")
    return (x, y, z)


def read_x_y_z(vgonio: VGonio):
    yield from bps.create(name="gonio xyz")  # gives name to event *descriptor* document
    yield from bps.read(vgonio.x)
    yield from bps.read(vgonio.yh)
    yield from bps.read(vgonio.z)
    yield from bps.save()


def rd_beam_parameters(ro_energ_atten: ReadOnlyEnergyAndAttenuator):
    """Returns a tuple of (transmission, wavelength, energy, intensity),
    read from EPICS"""
    transmission = yield from bps.rd(ro_energ_atten.transmission)
    wavelength = yield from bps.rd(ro_energ_atten.wavelength)
    energy = yield from bps.rd(ro_energ_atten.energy)
    intensity = yield from bps.rd(ro_energ_atten.intensity)
    LOGGER.info(
        f"Read current tranmission, wavelength, energy, attenuation: {(transmission,wavelength,energy,intensity,)}"  # noqa
    )
    return (
        transmission,
        wavelength,
        energy,
        intensity,
    )


def read_beam_parameters(ro_energ_atten: ReadOnlyEnergyAndAttenuator):
    """Returns a tuple of (transmission, wavelength, energy, intensity),
    read from EPICS"""

    yield from bps.create(
        name="beam params"
    )  # gives name to event *descriptor* document
    yield from bps.read(ro_energ_atten.transmission)
    yield from bps.read(ro_energ_atten.wavelength)
    yield from bps.read(ro_energ_atten.energy)
    yield from bps.read(ro_energ_atten.intensity)
    yield from bps.save()
