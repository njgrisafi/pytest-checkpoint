import json
from pathlib import Path

import pytest
from _pytest.pytester import Pytester, RunResult

from pytest_checkpoint.lap import Lap
from pytest_checkpoint.plugin import CheckpointPluginOpts, CollectBehavior

pytest_plugins = ["pytester"]


def verify_collect_behavior_result(
    result: RunResult, collect_behavior: CollectBehavior, expected_tests: int = 1
) -> None:
    if collect_behavior == CollectBehavior.DESELECT:
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED
        assert result.parseoutcomes()["deselected"] == expected_tests
    elif collect_behavior == CollectBehavior.SKIP:
        assert result.ret == pytest.ExitCode.OK
        assert result.parseoutcomes()["skipped"] == expected_tests
    else:
        raise ValueError(f"Unknown collect behavior: {collect_behavior}")


def test_simple_fail(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_failure="""
        def test_failure() -> None:
            assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_failure.py"
    )
    result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_failure.py::test_failure" in lap.failed
    assert len(lap.passed) == 0

    # Let's rerun the tests and make sure they run again
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_failure.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.failed.count("test_failure.py::test_failure") == 1


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_simple_pass(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_pass="""
        def test_pass() -> None:
            assert True
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_pass.py",
    )
    assert result.ret == pytest.ExitCode.OK
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_pass.py::test_pass" in lap.passed
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_pass.py",
    )
    verify_collect_behavior_result(result, collect_behavior)

    # Check that the lap file is still the same
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.passed.count("test_pass.py::test_pass") == 1
    assert len(lap.failed) == 0


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_xfail(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_xfail="""
        import pytest

        @pytest.mark.xfail
        def test_xfail() -> None:
            assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail.py",
    )
    assert result.ret == pytest.ExitCode.OK
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_xfail.py::test_xfail" in lap.passed
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail.py",
    )
    verify_collect_behavior_result(result, collect_behavior)

    # Check that the lap file is still the same
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.passed.count("test_xfail.py::test_xfail") == 1
    assert len(lap.failed) == 0


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_unittest_expected_failure(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_unittest_expected_failure="""
        import unittest

        @unittest.expectedFailure
        def test_unittest_expected_failure() -> None:
            assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure.py",
    )

    # Pytest will still fail unittest expected failures, however we should record it as a pass
    # It will pass if you run it with 'unittest.run'
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_unittest_expected_failure.py::test_unittest_expected_failure" in lap.passed
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure.py",
    )
    verify_collect_behavior_result(result, collect_behavior)

    # Check that the lap file is still the same
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.passed.count("test_unittest_expected_failure.py::test_unittest_expected_failure") == 1
    assert len(lap.failed) == 0


def test_setup_fail(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_setup_fail="""
        import pytest

        @pytest.fixture
        def fixture() -> None:
            assert False

        def test_setup_fail(fixture) -> None:
            pass
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_setup_fail.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_setup_fail.py::test_setup_fail" in lap.failed
    assert len(lap.passed) == 0

    # Let's rerun the tests and make sure they run again
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_setup_fail.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.failed.count("test_setup_fail.py::test_setup_fail") == 1


def test_unittest_setup_fail(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_unittest_setup_fail="""
        import unittest

        class TestSetupFail(unittest.TestCase):
            def setUp(self) -> None:
                assert False

            def test_setup_fail(self) -> None:
                assert True
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_unittest_setup_fail.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_unittest_setup_fail.py::TestSetupFail::test_setup_fail" in lap.failed
    assert len(lap.passed) == 0

    # Let's rerun the tests and make sure they run again
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_unittest_setup_fail.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.failed.count("test_unittest_setup_fail.py::TestSetupFail::test_setup_fail") == 1


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_xfail_setup_fail(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_xfail_setup_fail="""
        import pytest

        @pytest.fixture
        def fixture() -> None:
            assert False

        @pytest.mark.xfail
        def test_xfail_setup_fail(fixture) -> None:
            assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail_setup_fail.py",
    )
    assert result.ret == pytest.ExitCode.OK
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_xfail_setup_fail.py::test_xfail_setup_fail" in lap.passed
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail_setup_fail.py",
    )
    verify_collect_behavior_result(result, collect_behavior)


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_unittest_expected_failure_setup_fail(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_unittest_expected_failure_setup_fail="""
        import unittest

        class TestSetupFail(unittest.TestCase):
            def setUp(self) -> None:
                assert False

            @unittest.expectedFailure
            def test_setup_fail(self) -> None:
                assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure_setup_fail.py",
    )

    # Pytest will still fail unittest expected failures, however we should record it as a pass
    # It will pass if you run it with 'unittest.run'
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_unittest_expected_failure_setup_fail.py::TestSetupFail::test_setup_fail" in lap.passed
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure_setup_fail.py",
    )
    verify_collect_behavior_result(result, collect_behavior)


def test_teardown_fail(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_teardown_failure="""
        import pytest

        @pytest.fixture
        def fixture() -> None:
            yield
            assert False

        def test_teardown_failure(fixture) -> None:
            pass
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_teardown_failure.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_teardown_failure.py::test_teardown_failure" in lap.failed
    assert len(lap.passed) == 0

    # Let's rerun the tests and make sure they run again
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_teardown_failure.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.failed.count("test_teardown_failure.py::test_teardown_failure") == 1


def test_unittest_teardown_fail(pytester: Pytester) -> None:
    pytester.makepyfile(
        test_unittest_teardown_failure="""
        import unittest

        class TestTeardownFailure(unittest.TestCase):
            def tearDown(self) -> None:
                assert False

            def test_teardown_failure(self) -> None:
                assert True
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_unittest_teardown_failure.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_unittest_teardown_failure.py::TestTeardownFailure::test_teardown_failure" in lap.failed
    assert len(lap.passed) == 0

    # Let's rerun the tests and make sure they run again
    result = pytester.runpytest(
        "-p pytest_checkpoint", CheckpointPluginOpts.LAP_OUT, "lap-test.json", "test_unittest_teardown_failure.py"
    )
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert lap.failed.count("test_unittest_teardown_failure.py::TestTeardownFailure::test_teardown_failure") == 1


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_xfail_teardown_fail(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_xfail_teardown_failure="""
        import pytest

        @pytest.fixture
        def fixture() -> None:
            yield
            assert False

        @pytest.mark.xfail
        def test_xfail_teardown_failure(fixture) -> None:
            assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail_teardown_failure.py",
    )
    assert result.ret == pytest.ExitCode.OK
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert "test_xfail_teardown_failure.py::test_xfail_teardown_failure" in lap.passed

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_xfail_teardown_failure.py",
    )
    verify_collect_behavior_result(result, collect_behavior)


@pytest.mark.parametrize("collect_behavior", [CollectBehavior.DESELECT, CollectBehavior.SKIP])
def test_unittest_expected_failure_teardown_fail(pytester: Pytester, collect_behavior: CollectBehavior) -> None:
    pytester.makepyfile(
        test_unittest_expected_failure_teardown_failure="""
        import unittest

        class TestTeardownFailure(unittest.TestCase):
            def tearDown(self) -> None:
                assert False

            @unittest.expectedFailure
            def test_teardown_failure(self) -> None:
                assert False
        """
    )
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure_teardown_failure.py",
    )

    # Pytest will still fail unittest expected failures, however we should record it as a pass
    # It will pass if you run it with 'unittest.run'
    assert result.ret == pytest.ExitCode.TESTS_FAILED
    lap_out = Path(pytester.path).joinpath("lap-test.json")
    assert lap_out.exists()
    lap = Lap.decode(json.loads(lap_out.read_text()))
    assert (
        "test_unittest_expected_failure_teardown_failure.py::TestTeardownFailure::test_teardown_failure" in lap.passed
    )
    assert len(lap.failed) == 0

    # Let's rerun the tests and make sure the collect behavior is as expected
    result = pytester.runpytest(
        "-p pytest_checkpoint",
        CheckpointPluginOpts.LAP_OUT,
        "lap-test.json",
        CheckpointPluginOpts.COLLECT_BEHAVIOR,
        collect_behavior,
        "test_unittest_expected_failure_teardown_failure.py",
    )
    verify_collect_behavior_result(result, collect_behavior)
