from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from pytest_checkpoint.lap import Lap
from pytest_checkpoint.logger import get_logger

if TYPE_CHECKING:
    from pytest import Config, Item, Session, TestReport


class RunTestPhase(StrEnum):
    SETUP = "setup"
    CALL = "call"
    TEARDOWN = "teardown"


class CheckpointPluginOpts(StrEnum):
    LAP_OUT = "--lap-out"
    COLLECT_BEHAVIOR = "--collect-behavior"


class CollectBehavior(StrEnum):
    DESELECT = "deselect"
    SKIP = "skip"


class CheckpointPlugin:
    name = "pytest-checkpoint"

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = get_logger(config, self.name)
        self.lap_file = Path(config.getoption(CheckpointPluginOpts.LAP_OUT))
        self.collect_behavior = CollectBehavior(config.getoption(CheckpointPluginOpts.COLLECT_BEHAVIOR))
        self._lap: Lap | None = None

    @property
    def lap(self) -> Lap:
        if self._lap:
            return self._lap

        if self.lap_file.exists():
            # TODO: figure out a better way to do logging. Possibly do a report instead.
            # Write a line before logging
            self.config.get_terminal_writer().line()
            self.logger.debug("Restoring checkpoint from %s", self.lap_file)
            self._lap = Lap.decode(json.loads(self.lap_file.read_text()))
        else:
            self._lap = Lap()
        return self._lap

    def pytest_collection_modifyitems(self, session: Session, config: Config, items: list[Item]) -> None:
        """https://docs.pytest.org/en/stable/reference/reference.html#pytest.hookspec.pytest_collection_modifyitems

        Here we will record all the tests that are expected to run.

        Args:
            session (Session): The pytest session object.
        """
        deselected: set[Item] = set()
        for item in items:
            if item.nodeid in self.lap.passed:
                if self.collect_behavior == CollectBehavior.DESELECT:
                    self.logger.debug("Deselecting %s from checkpoint", item.nodeid)
                    deselected.add(item)
                    continue
                elif self.collect_behavior == CollectBehavior.SKIP:
                    self.logger.debug("Skipping %s from checkpoint", item.nodeid)
                    item.add_marker("skip")

        items[:] = [item for item in items if item not in deselected]
        config.hook.pytest_deselected(items=deselected)

    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_runtest_logreport

        We will inspect the report object to determine if the test passed, failed, or was skipped.

        It handles this for each phase of the test: setup, call, and teardown.

        Args:
            report (TestReport): The report about to be logged.
        """
        # Special case for unittest expected failures
        # This is not handled in the internal 'TestReport.from_item_and_call' method
        is_unittest_expected_failure = report.keywords.get("__unittest_expecting_failure__", 0) == 1

        if report.when == RunTestPhase.SETUP:
            if report.failed and is_unittest_expected_failure is False:
                self.lap.mark_failed(report.nodeid)
            elif report.skipped and (hasattr(report, "wasxfail") or is_unittest_expected_failure):
                # Edge case where setup failure happens on a xfail test.
                # In these cases we should mark the test as passed
                # After this we skip call and go to teardown
                self.lap.mark_passed(report.nodeid)

            return None

        if report.when == RunTestPhase.CALL:
            if report.skipped or report.passed:
                self.lap.mark_passed(report.nodeid)

            if report.failed and is_unittest_expected_failure is False:
                self.lap.mark_failed(report.nodeid)
            elif report.failed and is_unittest_expected_failure:
                self.lap.mark_passed(report.nodeid)

            return None

        if report.when == RunTestPhase.TEARDOWN:
            if report.failed and is_unittest_expected_failure is False:
                self.lap.mark_failed(report.nodeid)
            self._checkpoint()

    def _checkpoint(self) -> None:
        """Checkpoint your progress.

        This will write the lap info to the output file.
        """
        self.logger.debug("Creating checkpoint to %s", self.lap_file)
        self.lap_file.parent.mkdir(parents=True, exist_ok=True)
        self.lap_file.write_text(json.dumps(self.lap.encode()))
