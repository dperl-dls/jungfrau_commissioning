# flake8: noqa

# This file runs in the iPython session on startup

from bluesky.run_engine import RunEngine
from dodal.beamlines import i24

from jungfrau_commissioning.__main__ import hlp, list_devices, list_plans
from jungfrau_commissioning.plans import gain_mode_and_darks as gain_mode_plans
from jungfrau_commissioning.plans import rotation_scan_plan as rotaion_scan_plans
from jungfrau_commissioning.plans import zebra as zebra_plans
from jungfrau_commissioning.plans.zebra import *
from jungfrau_commissioning.utils.log import set_up_logging_handlers
from jungfrau_commissioning.utils.utils import text_colors as col

set_up_logging_handlers()
hlp()
print(f"Creating Bluesky RunEngine with name {col.CYAN}RE{col.ENDC}")
RE = RunEngine({})
print("System Ready!")
