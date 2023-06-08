import inspect
from typing import Callable

import IPython
from dodal.beamlines import i24
from traitlets.config import Config

from jungfrau_commissioning.utils.utils import text_colors as col

__all__ = ["main", "hlp", "i24"]

welcome_message = f"""
There are a bunch of available functions. Most of them are Bluesky plans which
should be run in the Bluesky RunEngine using the syntax {col.CYAN}RE({col.GREEN}
plan_name{col.CYAN}){col.ENDC}.
Some functions can poke devices directly to manipulate them. You can try running
{col.CYAN}hlp({col.GREEN}function_name{col.CYAN}){col.ENDC} for possible information.

Devices are accessed by functions in the {col.CYAN}i24{col.ENDC} module, for example,
to get a handle on the vertical goniometer device, you can write:

    {col.BLUE}vgonio = i24.vgonio(){col.ENDC}
    
To list all the available devices in the {col.CYAN}i24{col.ENDC} module you can run

"""


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
