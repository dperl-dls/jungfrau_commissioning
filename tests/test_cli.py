import subprocess
import sys

from jungfrau_commissioning import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "jungfrau_commissioning", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
