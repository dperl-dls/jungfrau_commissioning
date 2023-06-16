from unittest.mock import MagicMock, patch

import pytest

from jungfrau_commissioning.plans.rotation_scan_plans import get_rotation_scan_plan
from jungfrau_commissioning.utils.params import RotationScanParameters


@pytest.fixture
def fake_devices(fake_vgonio, fake_jungfrau, fake_zebra, fake_beam_params):
    devices = {
        "jungfrau": fake_jungfrau,
        "gonio": fake_vgonio,
        "zebra": fake_zebra,
        "beam_params": fake_beam_params,
    }
    return devices


@pytest.fixture
def fake_create_devices_function(fake_devices):
    return lambda: fake_devices


@patch(
    "jungfrau_commissioning.plans.rotation_scan_plans.NexusFileHandlerCallback",
)
def test_rotation_scan_get_plan(
    nexus_callback: MagicMock, fake_create_devices_function
):
    minimal_params = RotationScanParameters.from_file("example_params.json")
    with patch(
        "jungfrau_commissioning.plans.rotation_scan_plans.create_rotation_scan_devices",
        fake_create_devices_function,
    ):
        plan = get_rotation_scan_plan(minimal_params)
    assert plan is not None
    nexus_callback.assert_called_once()
