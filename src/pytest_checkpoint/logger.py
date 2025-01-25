from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from _pytest.logging import ColoredLevelFormatter, get_log_level_for_setting

if TYPE_CHECKING:
    from pytest import Config


def get_logger(config: Config, name: str) -> logging.Logger:
    level = get_log_level_for_setting(config, "log_cli_level")
    if level is None:
        level = logging.DEBUG if config.option.verbose > 0 else logging.INFO

    # TODO: Color does not work as expected.
    formatter = ColoredLevelFormatter(
        config.get_terminal_writer(), config.getini("log_cli_format"), datefmt=config.getini("log_cli_date_format")
    )
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger
