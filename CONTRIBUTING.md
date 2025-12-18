# Contributing

## Setup

You can either use the dev container with your favourite editor, e.g. VSCode. Or you can create your setup locally below we demonstrate both.

In both cases they share the same tools, of which these tools are:
* [uv](https://docs.astral.sh/uv/) for Python packaging and development
* [make](https://www.gnu.org/software/make/) (OPTIONAL) for automation of tasks, not strictly required but makes life easier.

### Dev Container

A [dev container](https://containers.dev/) uses a docker container to create the required development environment, the Dockerfile we use for this dev container can be found at [./.devcontainer/Dockerfile](./.devcontainer/Dockerfile). To run it locally it requires docker to be installed, you can also run it in a cloud based code editor, for a list of supported editors/cloud editors see [the following webpage.](https://containers.dev/supporting)

To run for the first time on a local VSCode editor (a slightly more detailed and better guide on the [VSCode website](https://code.visualstudio.com/docs/devcontainers/tutorial)):
1. Ensure docker is running.
2. Ensure the VSCode [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension is installed in your VSCode editor.
3. Open the command pallete `CMD + SHIFT + P` and then select `Dev Containers: Rebuild and Reopen in Container`

You should now have everything you need to develop, `uv`, and `make`, for VSCode various extensions like `Pylance`, etc.

If you have any trouble see the [VSCode website.](https://code.visualstudio.com/docs/devcontainers/tutorial).

### Local

To run locally first ensure you have the following tools installted locally:
* [uv](https://docs.astral.sh/uv/getting-started/installation/) for Python packaging and development.
* [make](https://www.gnu.org/software/make/) (OPTIONAL) for automation of tasks, not strictly required but makes life easier.
  * Ubuntu: `apt-get install make`
  * Mac: [Xcode command line tools](https://mac.install.guide/commandlinetools/4) includes `make` else you can use [brew.](https://formulae.brew.sh/formula/make)
  * Windows: Various solutions proposed in this [blog post](https://earthly.dev/blog/makefiles-on-windows/) on how to install on Windows, inclduing `Cygwin`, and `Windows Subsystem for Linux`.

When developing on the project you will want to install the Python package locally in editable format with all the extra requirements, this can be done like so:

```bash
uv sync
```

## Running linters

This code base uses isort, flake8 and mypy to ensure that the format of the code is consistent and contain type hints. ISort and mypy settings can be found within [./pyproject.toml](./pyproject.toml) and the flake8 settings can be found in [./.flake8](./.flake8). To run these linters:

``` bash
make lint
```

## Setting a different default python version

The default or recommended Python version is shown in [.python-version](./.python-version, currently `3.12`, this can be changed using the [uv command](https://docs.astral.sh/uv/reference/cli/#uv-python-pin):

``` bash
uv python pin
# uv python pin 3.13
```

## General folder structure

* `/pymusas_models` - contains the code that creates all of the PyMUSAS models.
* `/model_release.py` - Releases the models, that have been created locally, to GitHub as a [GitHub release](https://github.com/UCREL/pymusas-models/releases) per model. 
* `/model_creation_tests`
* `/model_function_tests` - The tests are divided up by language, using each language's [BCP 47 language code](https://www.w3.org/International/articles/language-tags/), and then model (either `rule based tagger` or `neural tagger`).
    * `/model_function_tests/fr`
        * `/model_function_tests/fr/test_rule_based_tagger.py`
    * `/model_function_tests/it`
        * `/model_function_tests/it/test_rule_based_tagger.py`
    * `/model_function_tests/en`
        * `/model_function_tests/en/test_neural_tagger.py`
        * `/model_function_tests/en/test_rule_based_tagger.py`
    * other language codes
* `/model_creation_tests/test_create_and_install_models.py` - This creates and installs the models used within `tests` and in doing so tests that this part of the code base works. **Note** that we install the models to a temporary Python virtual environment.

The testing structure of `/model_function_tests` has been heavily influenced by how [spaCy tests their models](https://github.com/explosion/spacy-models/tree/master/tests#writing-tests).


## Model deployment lifecycle

Each model is created using a spaCy [configuration](https://spacy.io/api/data-formats#config) and [meta](https://spacy.io/api/data-formats#meta) file, of which we can have more than one model for each language. These configuration and meta files are automatically created using the Command Line Interface (CLI) to `pymusas_models` and then used to create the PyMUSAS spaCy models with their relevant installation data (distribution files, README, meta data, etc). This process is done per model and all model data is stored in their own model folder, named based off the [model naming convention](./README.md#model-naming-conventions) specified in the main README, within the directory you have specified to store this data in. Each of these spaCy model folders contain the relevant information to create a [GitHub release](https://github.com/UCREL/pymusas-models/releases) for that model.

The CLI knows which models to create and how to create them by utilising the given meta data stored in the [language_resources.json](./language_resources.json) file (for more information of the [language_resources.json](./language_resources.json) file see the [Language Resource Meta Data section](#language-resource-meta-data)).

To create all of the models and store them in the folder `./models` run the following:

``` bash
python pymusas_models/__main__.py create-models --models-directory ./models --language-resource-file ./language_resources.json
```

This will create the following folders:

* `./models/cmn_dual_upos2usas_contextual_none-0.3.0`
* `./models/cmn_single_upos2usas_contextual_none-0.3.0`
* `./models/cy_dual_basiccorcencc2usas_contextual_none-0.3.0`
* other model folders

### Releasing the models to GitHub

To automate the release of the models we have created we are going to use the [GitHub REST API](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api). This REST API has a rate limit of 5000 calls per hour when you are running it as an authenticated client, for [details on authentication](https://docs.github.com/en/rest/guides/getting-started-with-the-rest-api#authentication). As we are creating releases we need to have a Personal Access Token (PAT) for authentication with `public_repo` scope, the PAT can be created at the following [link](https://github.com/settings/tokens/new), we named our PAT `pymusas-models`.

Once you have created your PAT add it to the following file `GITHUB_TOKEN.json` **this file should never be added to the repository as it will contain your PAT which is sensitive information.** The PAT should be added to the JSON file like so:

``` json
{"PAT": "YOUR PAT TOKEN"}
```

Now, assuming all of the models you would like to release are in the `./models` directory, we can release the model to GitHub using the [model_release.py](./model_release.py) script like so:

``` bash
python model_release.py
```

Once ran successfully it will state the rate limit you had and have left on the GitHub REST API, like below:

``` bash
Current rate limit: {'limit': 5000, 'used': 74, 'remaining': 4926, 'reset': 1652299539}




Rate limit after model releases: {'limit': 5000, 'used': 76, 'remaining': 4924, 'reset': 1652299539}
```

In addition you should see the models you wanted to release to GitHub now on GitHub within the [releases section](https://github.com/UCREL/pymusas-models/releases).

#### Potential Errors

Some errors that can occur when running the [model_release.py](./model_release.py) script:

* The model you want to release has already been released. If this occurs and is a mistake then delete the model from the `./models` folder. If this is not a mistake then you may need to change the model version of the model (`c` element as described in the [`Model Versioning` section from the main README](./README.md#model-versioning)) as each model that is released has to have a unique model name.
* The model did not upload correctly.

Once you have corrected the error re-run the [model_release.py](./model_release.py) script.


### Advance model deployment options

If you want to specify the version of model, e.g. the `c` part of model version as described in [the model versioning section within the main README](./README.md#model-versioning) use the `--model-version` command line option (**default value "0"**).

In addition to specify the version of `spaCy` that the model will be compatible with use the `--spacy-version` command line option (**default value ">=3.0,<4.0"**). This spaCy version is overridden per language if the language resource file for a given language specifies a `spacy version`. See `python pymusas_models/__main__.py create-models --help` for more details.

Below we show how both of these command line options can be used:

``` bash
python pymusas_models/__main__.py create-models \
--models-directory ./models \
--language-resource-file ./language_resources.json \
--model-version 1
```

This will create the following folders, assuming we are using PyMUSAS version `0.3.0`:

* `./models/cmn_dual_upos2usas_contextual_none-0.3.1`
* `./models/cmn_single_upos2usas_contextual_none-0.3.1`
* `./models/cy_dual_basiccorcencc2usas_contextual_none-0.3.1`
* other model folders

## Creating the overview of the models table

To create the [overview of the models table from the main README](./README.md#overview-of-the-models):

1. If you have not already done so create all of the models (if you have done this please skip this step):
``` bash
python pymusas_models/__main__.py create-models --models-directory ./models --language-resource-file ./language_resources.json
```
2. Run the following which will print out the Markdown overview of the models table, which can then be copied into the main README:
``` bash
python pymusas_models/__main__.py overview-of-models --models-directory ./models
``` 


## Running tests

The tests are testing both: 
* That the models can be created and installed via `pip` locally.
* Once created and installed the models function as expected. 

This has resulted in two test folders, as shown in [General Folder Structure](#general-folder-structure); `/model_function_tests` and `/model_creation_tests`

The `/model_creation_tests` tests the first bullet point and `/model_function_tests` tests the second bullet point.

More details about these tests can be found below including how to run them individually or together;

### Model creation tests

As the `/model_function_tests` require the installed models that are created from `/model_creation_tests` the `/model_creation_tests` tests are ran first whereby the models created will be installed to a virtual environment that will be saved to `./temp_venv` **NOTE** `./temp_venv` is assumed to not exist, an error will occur if the directory does exist, unless you specify the `--overwrite` flag which will first delete the directory if it exists and then re-create.

<details>
    <summary>Linux/Mac</summary>

``` bash
pytest --virtual-env-directory=./temp_venv ./model_creation_tests
```

Using the overwrite flag, which will first delete `./temp_venv` if it exists:

``` bash
pytest --virtual-env-directory=./temp_venv --overwrite ./model_creation_tests
```

This last command can be ran as a `make` command:

``` bash
make model-creation-tests
```

**Note Mac users**, I have found that `make` might not work if using the `make` command version that comes as default with your Mac (version 3.81), but the `make` command you can install through Conda (version 4.2.1) will work.

</details>

<details>
    <summary>Windows</summary>

``` powershell
pytest --virtual-env-directory=.\temp_venv .\model_creation_tests
```

Using the overwrite flag, which will first delete `.\temp_venv` if it exists:

``` powershell
pytest --virtual-env-directory=.\temp_venv --overwrite .\model_creation_tests
```

</details>

### Model function tests

By separating these tests into two different test folders it allows the virtual environment to be cached, which allows the second set of tests, `/model_function_tests`, to be ran as many times as you like without having to re-create the virtual environment.


<details>
    <summary>Linux/Mac</summary>

``` bash
source ./temp_venv/venv/bin/activate # Used to activate the virtual environment
pytest ./model_function_tests
deactivate
```

</details>

<details>
    <summary>Windows</summary>

``` powershell
.\temp_venv\venv\Scripts\Activate.ps1 # Used to activate the virtual environment
pytest .\model_function_tests
deactivate
```

</details>



### All tests

<details>
    <summary>Linux/Mac</summary>

There is a make command that will run all tests:

``` bash
make run-all-tests
```

**Note Mac users**, I have found that `make` might not work if using the `make` command version that comes as default with your Mac (version 3.81), but the `make` command you can install through Conda (version 4.2.1) will work.

</details>

<details>
    <summary>Windows</summary>

To run all tests:

``` powershell
pytest --virtual-env-directory=.\temp_venv --overwrite .\model_creation_tests
.\temp_venv\venv\Scripts\Activate.ps1 # Used to activate the virtual environment
pytest .\model_function_tests
deactivate
```

</details>

### Tests on the GitHub Actions CI

The tests run on a subset of the models created on the GitHub actions CI, this is due to disk space restrictions on the GitHub actions runners, see this issue [https://github.com/UCREL/pymusas-models/issues/14](https://github.com/UCREL/pymusas-models/issues/14). To note the models we do not run on are:

* All `xx` multilingual models.
* English base neural model.

To run the tests locally in the way they are run on the GitHub actions CI:

``` bash
rm -rf ./temp_venv
uv run -m pytest -vvv --virtual-env-directory=./temp_venv --overwrite --github-ci ./model_creation_tests
source ./temp_venv/venv/bin/activate
pytest --github-ci ./model_function_tests
deactivate
```

## Language Resource Meta Data

Language resource meta data is stored in the [language_resources.json file](./language_resources.json), it is used by the entry points to the main package, `pymusas_models`, to create the models. The structure of the JSON file is the following, and is validated using the `LanguageResources` Pydantic Base Model class within [pymusas_models/language_resource.py](pymusas_models/language_resource.py):

``` JSON
{
    "language_resources": {
        "Language one BCP 47 code": {
            "spacy_version": ">=3.0,<4.0",
            "models": [
                {
                    "name": "NAME OF MODEL",
                    "model_type": "pymusas_rule_based_tagger",
                    "resources":{
                        "ranker": "RANKER NAME",
                        "rules": [
                            {
                                "rule_type": "single",
                                "pos_mapper": "POS MAPPER NAME OR NONE",
                                "lexicon_url": "PERMANENT URL TO LEXICON",
                                "with_pos": true
                            },
                            {
                                "rule_type": "mwe",
                                "pos_mapper": null,
                                "lexicon_url": ""
                            }
                        ],
                        "default_punctuation_tags": ["PUNCT"],
                        "default_number_tags": ["NUM"]
                    },
                    "config": {
                        "pos_attribute": "tag_"
                    }
                },
                {
                    "name": "xx_none_none_none_multilingualsmallbem",
                    "model_type": "pymusas_neural_tagger",
                    "pretrained_model_name_or_path": "ucrelnlp/PyMUSAS-Neural-Multilingual-Small-BEM",
                    "config": {
                        "tokenizer_kwargs": {
                            "add_prefix_space": true
                        }
                    }
                }
            ],
            "language data": {
                "description": "LANANGUAGE NAME",
                "macrolanguage": "Macrolanguage code",
                "script": "ISO 15924 script code"
            }
        },
    ...
    }
}
```

* The [BCP 47 code](https://www.w3.org/International/articles/language-tags/) of the language, the [BCP47 language subtag lookup tool](https://r12a.github.io/app-subtags/) is a great tool to use to find a BCP 47 code for a language.
  * `spacy version` - **Optional** this key is only required if the version of spaCy required has to be more specific than the default which is `">=3.0,<4.0`. The version of spaCy required, this should be a String and follow the standard Python pip install syntax of the [version specifier](https://pip.pypa.io/en/stable/cli/pip_install/#requirement-specifiers), e.g. `>=3.3`.
  * `models` - a list of models that are associated with this language. Each model is represented as a dictionary, of which we support two model types `pymusas_rule_based_tagger` and `pymusas_neural_tagger` of which these reflect the models available in pymusas ([neural](hhttps://ucrel.github.io/pymusas/api/spacy_api/taggers/neural) and [rule_based](https://ucrel.github.io/pymusas/api/spacy_api/taggers/rule_based)).
    * `pymusas_rule_based_tagger`:
        * `name` - a unique model name that follows the [model naming convention](./README.md#model-naming-conventions)
        * `model_type` - this should be `pymusas_rule_based_tagger` this was chosen as it follows the spaCy component name of the tagger in [pymusas](https://ucrel.github.io/pymusas/api/spacy_api/taggers/rule_based#rulebasedtagger.class_attributes).
        * `resources` - The keys and values in this dictionary follows the arguments that the rule based tagger accepts within it's [initialize method.](https://ucrel.github.io/pymusas/api/spacy_api/taggers/rule_based#initialize)
            * `ranker` - The name of the ranker, in this case it can only be `contextual` as this is the only supported ranker.
            * `default_punctuation_tags` - list of POS tags that represent punctuation. Can be `null`.
            * `default_number_tags` - The POS tags that represent numbers. Can be `null`.
            * `rules` - A list of rules to apply to the sequence of tokens. This has to be a list of dictionaries representing either [Single](https://ucrel.github.io/pymusas/api/taggers/rules/single_word) or [MWE](https://ucrel.github.io/pymusas/api/taggers/rules/mwe) rules.
                * `rule_type` - `single` or `mwe`
                * `pos_mapper` - this is the mapping for linking the POS tags of the token's to the lexicon's. It can either be `null` for no mapping, `upos2usas` for UPOS to USAS or `basiccorcencc2usas` for Basic CorCenCC to USAS.
                * `lexicon_url` - URL to the lexicon to use. This should be a permanent URL, e.g. if the URL is to a GitHub repository the URL should be to a specific commit rather to the HEAD of the main branch.
                * `with_pos` - Only for `single` rules, whether the lexicon has POS tags or not.
        * `config` - The keys and values in this dictionary follows the arguments that the rule based tagger accepts within it's [__init__ method](https://ucrel.github.io/pymusas/api/spacy_api/taggers/rule_based#rulebasedtagger):
            * `pymusas_tags_token_attr` - The name of the attribute to assign the predicted tags too under the Token._ class.
            * `pymusas_mwe_indexes_attr` - The name of the attribute to assign the start and end token index of the associated MWE too under the Token._ class.
            * `pos_attribute` - The name of the attribute that the Part Of Speech (POS) tag is assigned too within the Token class.
            * `lemma_attribute` - The name of the attribute that the lemma is assigned too within the Token class. 
    * `pymusas_neural_tagger`:
        * `name` - a unique model name that follows the [model naming convention](./README.md#model-naming-conventions)
        * `model_type` - this should be `pymusas_neural_tagger` this was chosen as it follows the spaCy component name of the tagger in [pymusas](https://ucrel.github.io/pymusas/api/spacy_api/taggers/neural#neuraltagger.class_attributes).
        * `resources` - The keys and values in this dictionary follows the arguments that the neural tagger accepts within it's [initialize method.](https://ucrel.github.io/pymusas/api/spacy_api/taggers/neural#initialize)
            * `pretrained_model_name_or_path` - The string ID or path of the pretrained neural Word Sense Disambiguation (WSD) model to load.
        * `config` - The keys and values in this dictionary follows the arguments that the neural tagger accepts within it's [__init__ method](https://ucrel.github.io/pymusas/api/spacy_api/taggers/neural#neuraltagger):
            * `pymusas_tags_token_attr` - The name of the attribute to assign the predicted tags too under the Token._ class.
            * `pymusas_mwe_indexes_attr` - The name of the attribute to assign the start and end token index of the associated MWE too under the Token._ class.
            * `top_n` - The number of tags to predict. If -1 all tags will be predicted. If 0 or less than 0 will raise a ValueError.
            * `device` - The device to load the model, wsd_model, on. e.g. 'cpu'.
            * `tokenizer_kwargs` - Keyword arguments to pass to the tokenizer's transformers.AutoTokenizer.from_pretrained method.
  * `language data` - this is data that is associated with the `BCP 47` language code. To some degree this is redundant as we can look this data up through the `BCP 47` code, however we thought it is better to have it in the meta data for easy lookup. All of this data can be easily found through looking up the `BCP 47` language code in the [BCP47 language subtag lookup tool](https://r12a.github.io/app-subtags/)
    * `description` - The `description` of the language code.
    * `macrolanguage` - The macrolanguage tag, **note** if this does not exist then give the [primary language tag](https://www.w3.org/International/articles/language-tags/#language), which could be the same as the whole `BCP 47` code. The `macrolanguage` tag could be useful in future for grouping languages.
    * `script` - The [ISO 15924 script code](https://www.w3.org/International/articles/language-tags/#script) of the language code. The `BCP 47` code by default does not always include the script of the language as the default script for that language is assumed, therefore this data is here to make the default more explicit.

Below is an extract of the [./language_resources.json](./language_resources.json), to give as an example of this JSON structure:

``` JSON
{   "language_resources": 
    {
        "cmn": 
        {
            "models": [
                {
                    "name": "cmn_single_upos2usas_contextual_none",
                    "model_type": "pymusas_rule_based_tagger",
                    "resources":{
                        "ranker": "contextual",
                        "rules": [
                            {
                                "rule_type": "single",
                                "pos_mapper": "upos2usas",
                                "lexicon_url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/7ccc8baaea36f3fd249e77671db5638c1cba6136/Chinese/semantic_lexicon_chi.tsv",
                                "with_pos": true
                            }
                        ],
                        "default_punctuation_tags": ["PUNCT"],
                        "default_number_tags": ["NUM"]
                    }
                },
                {
                    "name": "cmn_dual_upos2usas_contextual_none",
                    "model_type": "pymusas_rule_based_tagger",
                    "resources":{
                        "ranker": "contextual",
                        "rules": [
                            {
                                "rule_type": "single",
                                "pos_mapper": "upos2usas",
                                "lexicon_url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/7ccc8baaea36f3fd249e77671db5638c1cba6136/Chinese/semantic_lexicon_chi.tsv",
                                "with_pos": true
                            },
                            {
                                "rule_type": "mwe",
                                "pos_mapper": "upos2usas",
                                "lexicon_url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/7ccc8baaea36f3fd249e77671db5638c1cba6136/Chinese/mwe-chi.tsv"
                            }
                        ],
                        "default_punctuation_tags": ["PUNCT"],
                        "default_number_tags": ["NUM"]
                    }
                }
            ],
            "language_data": {
                "description": "Mandarin Chinese",
                "macrolanguage": "zh",
                "script": "Hani"
            }
        },
        ...
        "xx":
        {
            "models":[
                {
                    "name": "xx_none_none_none_multilingualsmallbem",
                    "model_type": "pymusas_neural_tagger",
                    "pretrained_model_name_or_path": "ucrelnlp/PyMUSAS-Neural-Multilingual-Small-BEM",
                    "config": {
                        "tokenizer_kwargs": {
                            "add_prefix_space": true
                        }
                    }
                },
                {
                    "name": "xx_none_none_none_multilingualbasebem",
                    "model_type": "pymusas_neural_tagger",
                    "pretrained_model_name_or_path": "ucrelnlp/PyMUSAS-Neural-Multilingual-Base-BEM",
                    "config": {
                        "tokenizer_kwargs": {
                            "add_prefix_space": true
                        }
                    }
                }
            ],
            "language_data":{
                "description": "Multilingual",
                "macrolanguage": "xx",
                "script": "xx"
            }
        }
    }
}
```