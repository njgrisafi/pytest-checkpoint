from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Lap:
    passed: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)

    def mark_passed(self, test: str) -> None:
        """Call this when a test has passed so we can record it in the lap.

        Args:
            test (str): The test name that passed.
        """
        if test in self.passed:
            return

        self.passed.append(test)
        if test in self.failed:
            self.failed.remove(test)

    def mark_failed(self, test: str) -> None:
        """Call this when a test has failed so we can record it in the lap.

        Args:
            test (str): The test name that failed.
        """
        if test in self.failed:
            return

        self.failed.append(test)
        if test in self.passed:
            self.passed.remove(test)

    def is_recorded(self, test: str) -> bool:
        """Check if a test has been recorded in the lap.

        Args:
            test (str): The test name to check.

        Returns:
            bool: True if the test has been recorded, False otherwise.
        """
        return test in self.passed or test in self.failed

    def encode(self) -> dict[str, list[str]]:
        """Encode the lap data into a dictionary.

        Returns:
            dict: The lap data encoded into a dictionary.
        """
        return {
            "passed": self.passed,
            "failed": self.failed,
        }

    @classmethod
    def decode(cls, data: dict[str, list[str]]) -> Lap:
        """Decode a dictionary into a Lap object.

        Args:
            data (dict): The dictionary to decode.

        Returns:
            Lap: The Lap object decoded from the dictionary.
        """
        return cls(
            passed=data["passed"],
            failed=data["failed"],
        )
