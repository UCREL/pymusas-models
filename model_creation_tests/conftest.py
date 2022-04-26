import os
from pathlib import Path
import shutil
import sys
from typing import Iterator, Optional, cast

from _pytest.config.argparsing import Parser
from _pytest.fixtures import SubRequest
import pytest
from pytest_fixture_config import Config, yield_requires_config
from pytest_virtualenv import VirtualEnv


class FixtureConfig(Config):
    __slots__ = ('virtualenv_executable')


# Default values for system resource locations - patch this to change defaults
# Can be a string or list of them
DEFAULT_VIRTUALENV_FIXTURE_EXECUTABLE = [sys.executable, '-m', 'virtualenv']


CONFIG = FixtureConfig(
    virtualenv_executable=os.getenv('VIRTUALENV_FIXTURE_EXECUTABLE', DEFAULT_VIRTUALENV_FIXTURE_EXECUTABLE),
)


def string_to_path(value: str) -> Path:
    return Path(value).resolve()


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--virtual-env-directory", action="store",
        help="",
        default=None,
        type=string_to_path
    )
    parser.addoption(
        "--overwrite", action="store_true",
        help=""
    )


@pytest.fixture(scope="session", autouse=True)
def overwrite(request: SubRequest) -> bool:
    return cast(bool,
                request.config.getoption("--overwrite"))


@pytest.fixture(scope="session", autouse=True)
def virtual_env_directory(request: SubRequest, overwrite: bool) -> Path:
    venv_directory = cast(Optional[Path],
                          request.config.getoption("--virtual-env-directory"))
    if venv_directory is None:
        raise ValueError("--virtual-env-directory command line option is empty.")
    if venv_directory.exists() and overwrite:
        shutil.rmtree(venv_directory)
    elif venv_directory.exists():
        raise FileExistsError("Expecting the virtual environment directory to"
                              f" be empty: {venv_directory}")
    venv_directory.mkdir(parents=True)
    return venv_directory


@pytest.fixture(scope='session', autouse=True)
@yield_requires_config(CONFIG, ['virtualenv_executable'])
def session_virtualenv(virtual_env_directory: Path
                       ) -> Iterator[VirtualEnv]:
    """ Function-scoped virtualenv in a temporary workspace.
        Methods
        -------
        run()                : run a command using this virtualenv's shell environment
        run_with_coverage()  : run a command in this virtualenv, collecting coverage
        install_package()    : install a package in this virtualenv
        installed_packages() : return a dict of installed packages
        Attributes
        ----------
        virtualenv (`path.path`)    : Path to this virtualenv's base directory
        python (`path.path`)        : Path to this virtualenv's Python executable
        pip (`path.path`)           : Path to this virtualenv's pip executable
        .. also inherits all attributes from the `workspace` fixture
    """
    venv = VirtualEnv(workspace=virtual_env_directory, name='venv',
                      delete_workspace=False)
    yield venv
    venv.teardown()
