import inspect
from inspect import getmembers, isfunction
from typing import Callable

import IPython
from dodal.beamlines import i24
from dodal.utils import collect_factories
from traitlets.config import Config

from jungfrau_commissioning.plans import gain_mode_and_darks as gain_mode_plans
from jungfrau_commissioning.plans import rotation_scan_plan as rotation_scan_plans
from jungfrau_commissioning.plans import zebra as zebra_plans
from jungfrau_commissioning.utils.utils import text_colors as col

__all__ = ["main", "hlp", "list_devices"]

welcome_message = f"""
There are a bunch of available functions. Most of them are Bluesky plans which \
should be run in the Bluesky RunEngine using the syntax {col.CYAN}RE({col.GREEN}\
plan_name{col.CYAN}){col.ENDC}.
Some functions can poke devices directly to manipulate them. You can try running \
{col.CYAN}hlp({col.GREEN}function_name{col.CYAN}){col.ENDC} for possible information.
You can also grab device objects and manipulate them yourself. The PVs of the real \
device are associated with attributes on the Ophyd device object, so you can grab \
these and use their \
{col.CYAN}.set(){col.ENDC} method (for any attribute, returns an ophyd.status.Status), \
{col.CYAN}.put(){col.ENDC} (for single PVs, writes directly to channel access), \
{col.CYAN}.read(){col.ENDC} (returns a dict of reading statuses), and \
{col.CYAN}.get(){col.ENDC} (for single PVs, reads directly from channel access) \
methods if needed.

Devices are best accessed through functions in the {col.CYAN}i24{col.ENDC} module, for \
example, to get a handle on the vertical goniometer device, you can write:

    {col.BLUE}vgonio = i24.vgonio(){col.ENDC}

To list all the available plans, you can run:

    {col.BLUE}list_plans(){col.ENDC}

To list all the available devices in the {col.CYAN}i24{col.ENDC} module you can run:

    {col.BLUE}list_devices(){col.ENDC}

To run a basic default rotation scan, you can execute the following commands:

    {col.BLUE}params = RotationScanParameters.from_file("example_params.json"){col.ENDC}
    {col.BLUE}plan = get_rotation_scan_plan(params, []){col.ENDC} # <- at this stage, \
devices are initialised if they aren't already
    {col.BLUE}RE(plan){col.ENDC} # <- sends the plan to the RunEngine for execution
"""


def list_devices():
    for dev in collect_factories(i24):
        print(f"    {col.CYAN}i24.{dev}(){col.ENDC}")


def pretty_print_module_functions(mod, indent=0):
    for f in getmembers(mod, isfunction):
        print(" " * indent + f"{col.CYAN}{f[0]}(){col.ENDC}")


def list_plans():
    print(f"{col.BLUE}gain_mode_plans:{col.ENDC}")
    pretty_print_module_functions(gain_mode_plans, indent=4)
    print(f"{col.BLUE}zebra_plans:{col.ENDC}")
    pretty_print_module_functions(zebra_plans, indent=4)
    print(f"{col.BLUE}rotation_scan_plans:{col.ENDC}")
    pretty_print_module_functions(rotation_scan_plans, indent=4)


def hlp(arg: Callable | None = None):
    """When called with no arguments, displays a welcome message. Call it on a
    function to see documentation for it."""
    if arg is None:
        print(welcome_message)
    else:
        print(inspect.getdoc(arg))


setup: Config = Config()
setup.InteractiveShellApp.exec_files = ["setup_ipython.py"]


def main():
    # TODO CHECK FOR VENV
    IPython.start_ipython(colors="neutral", config=setup)


if __name__ == "__main__":
    main()
