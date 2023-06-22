# flake8: noqa

# This file runs in the iPython session on startup

from pathlib import Path

from bluesky.run_engine import RunEngine
from dodal.beamlines import i24

from jungfrau_commissioning.__main__ import hlp, list_devices, list_plans
from jungfrau_commissioning.plans.gain_mode_darks_plans import *
from jungfrau_commissioning.plans.jungfrau_plans import *
from jungfrau_commissioning.plans.rotation_scan_plans import *
from jungfrau_commissioning.plans.zebra_plans import *
from jungfrau_commissioning.utils.log import set_up_logging_handlers
from jungfrau_commissioning.utils.utils import text_colors as col

DIRECTORY = "/dls/i24/data/2023/cm33852-3/jungfrau_commissioning/"


set_up_logging_handlers()
hlp()
print(f"Creating Bluesky RunEngine with name {col.CYAN}RE{col.ENDC}")
RE = RunEngine({})
print("System Ready!")
