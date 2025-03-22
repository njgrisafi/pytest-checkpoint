from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from pytest_checkpoint.plugin import CheckpointPlugin, CheckpointPluginOpts, CollectBehavior

if TYPE_CHECKING:
    from pytest import Config, Parser


_DEFAULT_LAP_OUT = ".pytest_checkpoint/lap.json"


def pytest_addoption(parser: Parser) -> None:
    group = parser.getgroup(
        name=CheckpointPlugin.name,
        description=CheckpointPlugin.name,
    )
    group.addoption(
        CheckpointPluginOpts.LAP_OUT,
        action="store",
        default=_DEFAULT_LAP_OUT,
        help="Output file to store lap information for recording a checkpoint",
    )
    group.addoption(
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        action="store",
        default=CollectBehavior.DESELECT,
        # NOTE: In python 3.11, the choices argument is not supported for enums
        # We must convert it to a list of strings
        choices=list(CollectBehavior),
        help="This will determine how tests are collected when a checkpoint is restored",
    )


@pytest.hookimpl(trylast=True)
def pytest_configure(config: Config) -> None:
    config.pluginmanager.register(CheckpointPlugin(config), CheckpointPlugin.name)


__all__ = [
    "pytest_addoption",
    "pytest_configure",
]
