from typing import Callable

import IPython
from traitlets.config import Config

from jungfrau_commissioning.utils.utils import text_colors as col

__all__ = ["main", "hlp"]

welcome_message = f"""
There are a bunch of available functions. Most of them are Bluesky plans which
should be run using the syntax {col.CYAN}RE({col.GREEN}plan_name{col.CYAN}){col.ENDC}.
Some functions can poke devices directly to manipulate them. You can try running
{col.CYAN}hlp({col.GREEN}function_name{col.CYAN}){col.ENDC} for possible information.
"""


def hlp(arg: Callable | None = None):
    if arg is None:
        print(welcome_message)


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
