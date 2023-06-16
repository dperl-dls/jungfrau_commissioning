from unittest.mock import MagicMock

import pytest
from dodal.beamlines import i24
from dodal.devices.i24.jungfrau import JungfrauM1
from dodal.devices.i24.read_only_attenuator import ReadOnlyEnergyAndAttenuator
from dodal.devices.i24.vgonio import VGonio
from dodal.devices.zebra import Zebra
from ophyd.status import Status


@pytest.fixture
def fake_vgonio() -> VGonio:
    gon: VGonio = i24.vgonio(fake_with_ophyd_sim=True)
    gon.x.user_setpoint._use_limits = False
    gon.yh.user_setpoint._use_limits = False
    gon.z.user_setpoint._use_limits = False
    gon.omega.user_setpoint._use_limits = False
    return gon


@pytest.fixture
def fake_jungfrau() -> JungfrauM1:
    JF: JungfrauM1 = i24.jungfrau(fake_with_ophyd_sim=True)
    return JF


@pytest.fixture
def fake_beam_params() -> ReadOnlyEnergyAndAttenuator:
    BP: ReadOnlyEnergyAndAttenuator = i24.beam_params(fake_with_ophyd_sim=True)
    BP.transmission.sim_put(0.1)
    BP.energy.sim_put(20000)
    BP.wavelength.sim_put(0.65)
    BP.intensity.sim_put(9999999)
    return BP


@pytest.fixture
def fake_zebra() -> Zebra:
    zebra: Zebra = i24.zebra(fake_with_ophyd_sim=True)

    def arm_fail_disarm_side_effect(_):
        zebra.pc.armed.set(1)
        result = Status()
        result.set_finished()
        return result

    def disarm_fail_arm_side_effect(_):
        zebra.pc.armed.set(0)
        result = Status()
        result.set_finished()
        return result

    mock_arm_fail_disarm = MagicMock(side_effect=arm_fail_disarm_side_effect)
    mock_disarm_fail_arm = MagicMock(side_effect=disarm_fail_arm_side_effect)

    zebra.pc.arm_demand.set = mock_arm_fail_disarm
    zebra.pc.disarm_demand.set = mock_disarm_fail_arm

    return zebra
