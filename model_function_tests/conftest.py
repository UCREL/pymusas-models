from _pytest.config.argparsing import Parser
import pytest


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--github-ci", action="store_true",
        help="If the test is being ran within the GitHub actions CI"
    )


def pytest_configure(config):  # type: ignore
    config.addinivalue_line("markers", "ci: mark test as ci")


def pytest_collection_modifyitems(config, items):  # type: ignore
    if not config.getoption("--github-ci"):
        return
    skip_ci = pytest.mark.skip(reason="GitHub CI therefore skipping test, could not download model in disk capacity on runner")
    for item in items:
        if "ci" in item.keywords:
            item.add_marker(skip_ci)
