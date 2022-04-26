from pathlib import Path

from pytest_virtualenv import VirtualEnv
from typer.testing import CliRunner

from pymusas_models.__main__ import app


def test_create_and_install_models(tmp_path: Path,
                                   session_virtualenv: VirtualEnv) -> None:
    repo_directory = Path(__file__, '..', '..').resolve()
    requirements_file = str(Path(repo_directory, 'requirements.txt'))
    dev_requirements_file = str(Path(repo_directory, 'dev_requirements.txt'))
    session_virtualenv.install_package("'setuptools>=42' wheel",
                                       installer="pip")
    session_virtualenv.install_package(f"-r {requirements_file}",
                                       installer="pip")
    session_virtualenv.install_package(f"-r {dev_requirements_file}",
                                       installer="pip")
    session_virtualenv.install_package(f"{str(repo_directory)}", installer="pip")

    language_resource_file = Path(repo_directory, 'language_resources.json')
    runner = CliRunner()
    command_line_arguments = ["--models-directory", str(tmp_path),
                              "--language-resource-file",
                              str(language_resource_file)]
    runner_result = runner.invoke(app, command_line_arguments)
    assert 0 == runner_result.exit_code

    # Install all of the models
    for model_directory in tmp_path.iterdir():
        dist_directory = Path(model_directory, 'dist')
        if dist_directory.exists():
            for dist_file in dist_directory.iterdir():
                if dist_file.suffix == '.whl':
                    dist_file_path = str(dist_file.resolve())
                    session_virtualenv.install_package(f"{dist_file_path}",
                                                       installer="pip")
