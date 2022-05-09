# Contributing

## Install

Can be installed on all operating systems and supports Python version >= 3.7, to install run:

``` bash
pip install -e .[tests]
```

For a `zsh` shell, which is the default shell for the new Macs you will need to escape with `\` the brackets:

``` bash
pip install -e .\[tests\]
```

### Running linters

This code base uses flake8 and mypy to ensure that the format of the code is consistent and contain type hints. The flake8 settings can be found in [setup.cfg](./setup.cfg) and the mypy settings within [pyproject.toml](./pyproject.toml). To run these linters:

``` bash
isort pymusas_models model_function_tests model_creation_tests
flake8
mypy
```

## General folder structure

* `/pymusas_models` - contains the code that creates all of the PyMUSAS models.
* `/model_creation_tests`
* `/model_function_tests` - The tests are divided up by language, using each language's [BCP 47 language code](https://www.w3.org/International/articles/language-tags/), and then model (currently we only have one model the `rule based tagger`).
    * `/model_function_tests/fr`
        * `/model_function_tests/fr/test_rule_based_tagger.py`
    * `/model_function_tests/it`
        * `/model_function_tests/it/test_rule_based_tagger.py`
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

* `./models/cmn_dual_upos2usas_contextual-0.3.0`
* `./models/cmn_single_upos2usas_contextual-0.3.0`
* `./models/cy_dual_basiccorcencc2usas_contextual-0.3.0`
* other model folders

After the models have been created you will have to manually create a [GitHub release](https://github.com/UCREL/pymusas-models/releases) per model. In doing this per model:

1. The tag of the release should be the model name, e.g. `cmn_dual_upos2usas_contextual-0.3.0`
2. The branch, select the `main` branch (this is the default branch).
3. The title same as the tag e.g. `cmn_dual_upos2usas_contextual-0.3.0`
4. The description should be the README of the model.
5. Attach both the `.tar.gz` and `.whl` files from the model's `dist` folder.
6. Click `Publish release`

### Advance model deployment options

If you want to specify the version of model, e.g. the `c` part of model version as described in [the model versioning section within the main README](./README.md#model-versioning) use the `--model-version` command line option (**default value "0"**).

In addition to specify the version of `spaCy` that the model will be compatible with use the `--spacy-version` command line option (**default value ">=3.0"**).

Below we show how both of these command line options can be used:

``` bash
python pymusas_models/__main__.py create-models \
--models-directory ./models \
--language-resource-file ./language_resources.json \
--model-version 1 \
--spacy-version ">=3.0"
```

This will create the following folders, assuming we are using PyMUSAS version `0.3.0`:

* `./models/cmn_dual_upos2usas_contextual-0.3.1`
* `./models/cmn_single_upos2usas_contextual-0.3.1`
* `./models/cy_dual_basiccorcencc2usas_contextual-0.3.1`
* other model folders

Of which all of these models will enforce a spaCy version `>=3.0`.

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

As the tests are both: 
* Testing that the models can be created and installed via `pip` locally.
* Once created and installed the models function as expected. 

This has resulted in two test folders, as shown in [General Folder Structure](#general-folder-structure), `/model_function_tests` and `/model_creation_tests`. The `/model_creation_tests` tests the first bullet point and `/model_function_tests` tests the second bullet point.

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


## Language Resource Meta Data

Language resource meta data is stored in the [language_resources.json file](./language_resources.json), it is used by the entry points to the main package, `pymusas_models`, to create the models. The structure of the JSON file is the following:

``` JSON
{
    "Language one BCP 47 code": {
        "resources":[
            {
                "data type": "single", 
                "url": "PERMANENT URL TO RESOURCE"
            }, 
            {
                "data type": "mwe", 
                "url": "PERMANENT URL TO RESOURCE"
            }
        ],
        "model information": {
            "POS mapper": "POS TAGSET"
        },
        "language data": {
            "description": "LANANGUAGE NAME",
            "macrolanguage": "Macrolanguage code",
            "script": "ISO 15924 script code"
        }
    },
    "Language Two BCP 47 code" : {
        "resources":[
            {
                "data type": "single", 
                "url": "PERMANENT URL TO RESOURCE"
            }
        ],
        "model information": {
            "POS mapper": null
        },
        "language data":{
            "description": "LANANGUAGE NAME",
            "macrolanguage": "Macrolanguage code",
            "script": "ISO 15924 script code"
        }
        
    },
    ...
}
```

* The [BCP 47 code](https://www.w3.org/International/articles/language-tags/) of the language, the [BCP47 language subtag lookup tool](https://r12a.github.io/app-subtags/) is a great tool to use to find a BCP 47 code for a language.
  * `resources` - this is a list of resource files that are associated with the given language. There is no limit on the number of resources files associated with a language.
    * `data type` value can be 1 of 2 values:
      1. `single` - The `url` value has to be of the **single word lexicon** [file format](https://github.com/UCREL/Multilingual-USAS#single-word-lexicon-file-format).
      2. `mwe` - The `url` value has to be of the **Multi Word Expression lexicon** [file format](https://github.com/UCREL/Multilingual-USAS#multi-word-expression-mwe-lexicon-file-format).
    * `url` - permanent URL link to the associated resource.
  * `model information` - this is data that helps to create the model given the resources and the assumed NLP models, e.g. POS tagger, that will be used with the PyMUSAS model.
    * `POS mapper` - A mapper from that maps from the POS tagset of the tagged text to the POS tagset used in the lexicons. The mappers used are those from within the [PyMUSAS mappers module.](https://ucrel.github.io/pymusas/api/pos_mapper) We currently assume that each resource associated with the model uses the same POS tagset in the lexicon, this is a limitation of this model creation framework rather than the PyMUSAS package itself.
  * `language data` - this is data that is associated with the `BCP 47` language code. To some degree this is redundant as we can look this data up through the `BCP 47` code, however we thought it is better to have it in the meta data for easy lookup. All of this data can be easily found through looking up the `BCP 47` language code in the [BCP47 language subtag lookup tool](https://r12a.github.io/app-subtags/)
    * `description` - The `description` of the language code.
    * `macrolanguage` - The macrolanguage tag, **note** if this does not exist then give the [primary language tag](https://www.w3.org/International/articles/language-tags/#language), which could be the same as the whole `BCP 47` code. The `macrolanguage` tag could be useful in future for grouping languages.
    * `script` - The [ISO 15924 script code](https://www.w3.org/International/articles/language-tags/#script) of the language code. The `BCP 47` code by default does not always include the script of the language as the default script for that language is assumed, therefore this data is here to make the default more explicit.

Below is an extract of the [./language_resources.json](./language_resources.json), to give as an example of this JSON structure:

``` JSON
{
    "cmn": {
        "resources":[
            {
                "data type": "single", 
                "url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/69477221c3feaf8ab2c2033abf430e5c4ae1d5ce/Chinese/semantic_lexicon_chi.tsv"
            }, 
            {
                "data type": "mwe", 
                "url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/69477221c3feaf8ab2c2033abf430e5c4ae1d5ce/Chinese/mwe-chi.tsv"
            }
        ],
        "model information": {
            "POS mapper": "UPOS"
        },
        "language data": {
            "description": "Mandarin Chinese",
            "macrolanguage": "zh",
            "script": "Hani"
        }
    },
    "nl" : {
        "resources":[
            {
                "data type": "single", 
                "url": "https://raw.githubusercontent.com/UCREL/Multilingual-USAS/69477221c3feaf8ab2c2033abf430e5c4ae1d5ce/Dutch/semantic_lexicon_dut.tsv"
            }
        ],
        "model information": {
            "POS mapper": "UPOS"
        },
        "language data":{
            "description": "Dutch, Flemish",
            "macrolanguage": "nl",
            "script": "Latn"
        }
        
    },
    ...
}
```