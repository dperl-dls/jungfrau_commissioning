from unittest.mock import MagicMock, patch

from bluesky.run_engine import RunEngine

from jungfrau_commissioning.plans.rotation_scan_plans import get_rotation_scan_plan
from jungfrau_commissioning.utils.params import RotationScanParameters


@patch(
    "bluesky.plan_stubs.wait",
)
@patch(
    "jungfrau_commissioning.plans.rotation_scan_plans.NexusFileHandlerCallback",
)
def test_rotation_scan_plan_nexus_callback(
    nexus_callback: MagicMock,
    bps_wait: MagicMock,
    fake_create_devices_function,
    RE: RunEngine,
):
    minimal_params = RotationScanParameters.from_file("example_params.json")
    with patch(
        "jungfrau_commissioning.plans.rotation_scan_plans.create_rotation_scan_devices",
        fake_create_devices_function,
    ):
        plan = get_rotation_scan_plan(minimal_params)

    RE(plan)

    callback_instance: MagicMock = nexus_callback.return_value
    callback_calls = callback_instance.call_args_list
    assert len(callback_calls) == 4
    call_1 = callback_calls[0]
    assert call_1.args[0] == "start"
    assert call_1.args[1]["subplan_name"] == "rotation_scan_with_cleanup"
    assert "rotation_scan_params" in call_1.args[1]
    assert "position" in call_1.args[1]
    assert "beam_params" in call_1.args[1]
