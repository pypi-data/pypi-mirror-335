"""conftest.py provided fixtures to all tests in the directory."""

from typing import Any

import pytest
from pytest import MonkeyPatch


def pytest_addoption(parser: Any) -> None:  # TODO: correct type for parser.
    """Add checkpoint, and show_config options to pytest.

    Args:
        parser (Any): the parser for pytest
    """
    parser.addoption("--checkpoint", action="store_true", default=False)
    parser.addoption("--show_config", action="store_true", default=False)


@pytest.fixture(scope="session")
def group_path() -> str:
    """Gives all tests access to the shared group directory via a fixture.

    If we want a specific, separate, integration testing directory we can define in a similar way.

    Uses the session scope, invoking once per test session.

    Returns:
        str: the shared group directory
    """
    return "/group_path"


@pytest.fixture(autouse=True)
def set_test_environment(monkeypatch: MonkeyPatch) -> None:
    """Automatically sets environment variables for all tests.

    This ensures tests run consistently across users and machines.

    Uses the default pytest fixture scope, invoking automatically once per test function.

    Args:
        monkeypatch (MonkeyPatch): in-built pytest fixture for mocking/monkeypatching
    """
    monkeypatch.setenv("USER", "dummy_user")
    monkeypatch.setenv("HOST", "abci")
    monkeypatch.setenv("SGE_ACCOUNT", "gcd50678")
