import inspect
from typing import Callable

import IPython
from dodal.beamlines import i24
from dodal.utils import collect_factories
from traitlets.config import Config

from jungfrau_commissioning.utils.utils import text_colors as col

__all__ = ["main", "hlp", "i24", "list_devices"]

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

To list all the available devices in the {col.CYAN}i24{col.ENDC} module you can run:

    {col.BLUE}list_devices(){col.ENDC}

To list all the available plans in this package you can run:

    {col.BLUE}list_plans(){col.ENDC}

"""


def list_devices():
    for dev in collect_factories(i24):
        print(f"    {col.CYAN}i24.{dev}(){col.ENDC}")


def hlp(arg: Callable | None = None):
    """When called with no arguments, displays a welcome message. Call it on a
    function to see documentation for it."""
    if arg is None:
        print(welcome_message)
    else:
        print(inspect.getdoc(arg))


setup: Config = Config()
setup.InteractiveShellApp.exec_lines = [
    "from jungfrau_commissioning.__main__ import *",
    "hlp()",
    "print('System Ready!')",
]


def main():
    # TODO CHECK FOR VENV
    IPython.start_ipython(colors="neutral", config=setup)


if __name__ == "__main__":
    main()
