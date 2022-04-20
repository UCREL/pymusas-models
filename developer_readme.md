# Development README

## Install

Can be installed on all operating systems and supports Python version >= 3.7, to install run:

``` bash
pip install -e .
```

## General folder structure

* `/pymusas_models` - contains helper modules that are used by scripts within the `/scripts` folder.
* `/scripts` - contains scripts that are used to create the PyMUSAS models.

### Running linters

This code base uses flake8 and mypy to ensure that the format of the code is consistent and contain type hints. The flake8 settings can be found in [.flake8](./.flake8) and the mypy settings within [pyproject.toml](./pyproject.toml). To run these linters:

``` bash
isort scripts pymusas_models
flake8
mypy
```

## Model deployment lifecycle

Each model is created using a spaCy [configuration](https://spacy.io/api/data-formats#config) and [meta](https://spacy.io/api/data-formats#meta) file, of which we can have more than one model for each language. These configuration and meta files are automatically created and stored for each model within their own model folder, which is named after the model using the model naming conventions specified in the main [README](./README.md#model-naming-conventions). These model folders are then stored within their relevant language folder, e.g. if it is Welsh model then it would be in the [./languages/cy/ folder.](./languages/cy/) Once the configuration and meta files are created the associated spaCy model is created and then uploaded to this repository as a [GitHub release](https://github.com/UCREL/pymusas-models/releases).

Below is a list of steps outlining the scripts that need to be ran to create these models with some extra detail on what each script does:

1. [scripts/create_config_and_meta_files.py](./scripts/create_config_and_meta_files.py). This script creates the configuration and meta files for each model using the model meta data we store on each language, within the [language_resources.json](./language_resources.json) file (for more information of the [language_resources.json](./language_resources.json) file see the [Language Resource Meta Data section](#language-resource-meta-data-section)).
2. 


## Language Resource Meta Data section

Language resource meta data is stored in the [language_resources.json file](./language_resources.json), it is used by the [scripts/create_config_and_meta_files.py](./scripts/create_config_and_meta_files.py) script to create the models and their associated meta data file. The structure of the JSON file is the following:

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

## Default Meta information

``` json
{
  "author": "UCREL Research Centre",
  "email": "ucrel@lancaster.ac.uk",
  "url": "https://ucrel.github.io/pymusas/",
  "license": "CC BY-NC-SA 4.0",
}
```

``` bash
spacy package ./tmp ./models
spacy package ./pt_tmp ./models
```