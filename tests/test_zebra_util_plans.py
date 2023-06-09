from unittest.mock import MagicMock, patch

import pytest
from bluesky.run_engine import RunEngine
from dodal.beamlines import i03
from dodal.devices.zebra import I24Axes, Zebra
from ophyd.status import Status

from jungfrau_commissioning.plans.zebra_plans import (
    arm_zebra,
    disarm_zebra,
    setup_zebra_for_rotation,
)


@pytest.fixture
def RE():
    return RunEngine({})


@pytest.fixture
def zebra():
    return i03.zebra(fake_with_ophyd_sim=True)


@patch("bluesky.plan_stubs.wait")
def test_zebra_set_up_for_rotation(bps_wait, RE, zebra: Zebra):
    RE(setup_zebra_for_rotation(zebra, wait=True))
    assert zebra.pc.gate_trigger.get(as_string=True) == I24Axes.OMEGA.value
    assert zebra.pc.gate_width.get() == pytest.approx(360, 0.01)
    with pytest.raises(ValueError):
        RE(setup_zebra_for_rotation(zebra, direction=25))


def test_zebra_arm_disarm(
    RE,
    zebra: Zebra,
):
    def arm_fail_disarm_side_effect(_):
        zebra.pc.armed.set(1)
        done = Status()
        done.set_finished()
        return done

    def disarm_fail_arm_side_effect(_):
        zebra.pc.armed.set(0)
        done = Status()
        done.set_finished()
        return done

    mock_arm_fail_disarm = MagicMock(side_effect=arm_fail_disarm_side_effect)
    mock_disarm_fail_arm = MagicMock(side_effect=disarm_fail_arm_side_effect)

    zebra.pc.arm_demand.set = mock_arm_fail_disarm
    zebra.pc.disarm_demand.set = mock_disarm_fail_arm

    zebra.pc.armed.set(0)
    RE(arm_zebra(zebra, 0.5))
    assert zebra.pc.is_armed()
    zebra.pc.armed.set(1)
    RE(disarm_zebra(zebra, 0.5))
    assert not zebra.pc.is_armed()

    zebra.pc.arm_demand.set = mock_disarm_fail_arm
    zebra.pc.disarm_demand.set = mock_arm_fail_disarm

    with pytest.raises(TimeoutError):
        zebra.pc.armed.set(0)
        RE(arm_zebra(zebra, 0.2))
    with pytest.raises(TimeoutError):
        zebra.pc.armed.set(1)
        RE(disarm_zebra(zebra, 0.2))
