import json
from pathlib import Path

from pytest_virtualenv import VirtualEnv
from typer.testing import CliRunner

from pymusas_models.__main__ import app
from pymusas_models.language_resource import LanguageResources


def test_create_and_install_models(tmp_path: Path,
                                   session_virtualenv: VirtualEnv,
                                   github_ci: bool) -> None:
    repo_directory = Path(__file__, '..', '..').resolve()
    # requirements_file = str(Path(repo_directory, 'requirements.txt'))
    # dev_requirements_file = str(Path(repo_directory, 'dev_requirements.txt'))
    # session_virtualenv.install_package(f"-r {requirements_file}",
    #                                   installer="pip")
    # session_virtualenv.install_package(f"-r {dev_requirements_file}",
    #                                   installer="pip")
    # session_virtualenv.install_package(f"{str(repo_directory)}", installer="pip")

    language_resource_file = Path(repo_directory, 'language_resources.json')
    if github_ci:
        # These are the languages and English specific models that will be removed
        # from the GitHub CI tests, so that the runner does not run out of
        # disk space, see: https://github.com/UCREL/pymusas-models/issues/14
        languages_to_remove = ["xx"]
        english_models_to_remove = ["en_none_none_none_englishbasebem"]  # , "en_none_none_none_englishsmallbem"]

        github_ci_language_resource_file = Path(tmp_path, 'github_ci_language_resources.json')
        with language_resource_file.open('r', encoding='utf-8') as resource_file:
            resource_file_data = resource_file.read()
            LanguageResources.model_validate_json(resource_file_data)
            language_resource = json.loads(resource_file_data)

            all_languages = language_resource["language_resources"]
            for language_to_remove in languages_to_remove:
                del all_languages[language_to_remove]

            english_models = all_languages['en']["models"]

            for model_to_remove in english_models_to_remove:
                index_to_remove = None
                for index, model in enumerate(english_models):
                    if model["name"] == model_to_remove:
                        index_to_remove = index
                if index_to_remove is not None:
                    del english_models[index_to_remove]
                else:
                    raise ValueError(f'Could not find the English model {model_to_remove} to remove')
            with github_ci_language_resource_file.open('w', encoding="utf-8") as github_ci_resource_file:
                github_ci_resource_file.write(json.dumps(language_resource))
        language_resource_file = github_ci_language_resource_file
        
    runner = CliRunner()
    command_line_arguments = ["create-models",
                              "--models-directory",
                              str(tmp_path),
                              "--language-resource-file",
                              str(language_resource_file)]
    runner_result = runner.invoke(app, command_line_arguments)
    assert 0 == runner_result.exit_code

    # Instal torch separately to ensure it installs the CPU version which is
    # a smaller install
    session_virtualenv.install_package("torch", installer="pip", installer_command="install --index-url https://download.pytorch.org/whl/cpu")
    # Install all of the models
    for model_directory in tmp_path.iterdir():
        dist_directory = Path(model_directory, 'dist')
        if dist_directory.exists():
            for dist_file in dist_directory.iterdir():
                if dist_file.suffix == '.whl':
                    dist_file_path = str(dist_file.resolve())
                    session_virtualenv.install_package(f"{dist_file_path}",
                                                       installer="pip")
    # Required to run the functional tests
    session_virtualenv.install_package("pytest",
                                       installer='pip')
