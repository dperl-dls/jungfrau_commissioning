import logging
from pathlib import Path
from typing import List, Union

from dodal.log import LOGGER as dodal_logger
from dodal.log import set_up_logging_handlers as setup_dodal_logging

LOGGER = logging.getLogger("jungfrau_commissioning")
LOGGER.setLevel(logging.DEBUG)
LOGGER.parent = dodal_logger


def set_up_logging_handlers(
    logging_level: Union[str, None] = "DEBUG", dev_mode: bool = True
) -> List[logging.Handler]:
    """Set up the logging level and instances for user chosen level of logging.

    Mode defaults to production and can be switched to dev with the --dev flag on run.
    """
    handlers = setup_dodal_logging(
        logging_level, dev_mode, Path("/tmp/jungfrau_commissioning_logs/log.log")
    )

    return handlers
