# PyMUSAS-Models

<p align="center">
    <a href="https://github.com/UCREL/pymusas-models/actions/workflows/ci.yml">
            <img alt="CI" src="https://github.com/UCREL/pymusas-models/actions/workflows/ci.yml/badge.svg?branch=main&event=push"/>
    </a>
</p>

This repository contains all of the released [PyMUSAS](https://ucrel.github.io/pymusas/) models, and the following documentation:

* **Model introduction**, this is useful context to better understand the model naming conventions.
* **Model naming conventions**
* **Overview of the models**, useful for comparing the models.
* **Issues / bug reports / improving the models**
* **Development**

All of the models are released through [GitHub releases](https://github.com/UCREL/pymusas-models/releases) as `.whl` and `.tar.gz` files. Each model release contains detailed information about the model, more information than specified through the model naming convention, for example the lexicons used, URL to the lexicon, etc.

## Model introduction

All of the models are rule based taggers, and all output [USAS semantic categories](https://ucrel.lancs.ac.uk/usas/) on the token level. The rules rely on lexicon and lexical information to classify a token into semantic categories. The lexicon information comes from a lexicon, of which the lexicons used in these models all come from the [Multilingual USAS GitHub repository](https://github.com/UCREL/Multilingual-USAS). The lexical information used is the `text`, `lemma`, and `Part Of Speech (POS)` of the token, this information is then used to find the correct lexicon entry in the given lexicon(s). **Note** that not all lexical information is required, but the more information the more likely you will have a more accurate tagger.

If the model uses a Multi Word Expression (MWE) lexicon then the tagger can identify MWEs and their associated semantic categories. Furthermore, these lexicons can be more than just lookup tables they can contain a pattern matching syntax, of which more details of this can be found in these [notes](). In addition, the POS tagset used in these lexicons can differ from the tagset within the lexical information therefore POS mappers are used to map from the lexical POS tagset (lexical POS tagset is most likely determined by the POS tagger used on the text) to the lexicon POS tagset.

As a token or tokens, in MWE cases, can be matched to multiple lexicon entries the rule based tagger uses a ranking system to determine the best token match.

For more detailed information on the rule based tagger go to the following [PyMUSAS API documentation page]().

## Model naming conventions
 
We expect all model packages to follow the naming convention of `[lang]_[name]`, whereby `lang` is a [BCP 47 code](https://www.w3.org/International/articles/language-tags/) of the language, which is a similar convention as [spaCy uses](https://github.com/explosion/spacy-models#model-naming-conventions). The name is then split into:

* **rules** used:
    * `single`: Only a single word lexicon is used.
    * `dual`: Both a single and Multi Word Expression lexicons are used.
* **POS Mapping** used to map the POS tagset from the tagged text to the POS tagset used in the lexicons of the rule based tagger.
    * `upos2usas`: Maps from [UPOS](https://universaldependencies.org/u/pos/) tagged text to USAS core tagset of the lexicons.
    * `basiccorcencc2usas`: Maps [Basic CorCenCC](https://ucrel.github.io/pymusas/api/pos_mapper) tagged text to USAS core tagset of the lexicons.
    * `none`: No POS mapper was used.
* **ranker** the ranker used to determine the best lexicon entry match for the token.
    * `contextual`: Uses the `ContextualRuleBasedRanker`, which ranks based on heuristic rules and then finds the best lexicon match for each token taking into account all other tokens in the text. For more details on this ranker see the [ContextualRuleBasedRanker documentation]().

For example, `cy_single_basiccorcencc2usas_contextual` is a Welsh single word lexicon model that maps the tagged text POS labels from Basic CorCenCC tagset to the USAS core tagset to be compatible with the lexicons used in this rule based tagger and uses the `contextual` ranker.

### Model versioning

Similar to the the spaCy models, our model versioning reflects the compatibility with [PyMUSAS](https://github.com/ucrel/pymusas), as well as the model version. A model version `a.b.c` translates to:

* `a`: **PyMUSAS major version**. For example, `0` for PyMUSAS v0.x.x
* `b`: **PyMUSAS minor version**. For example, `2` for PyMUSAS v0.2.x
* `c`: **Model version**. Different model configurations, for example using different or updated lexicons.

## Overview of the models

| Language (BCP 47 language code) | Model Name | MWE | POS Mapper | Ranker | File Size |
| --- | --- | --- | --- | --- | --- |
| Mandarin Chinese (cmn) | cmn_dual_upos2usas_contextual | :heavy_check_mark: | UPOS 2 USAS | Contextual | 1.28MB |
| Mandarin Chinese (cmn) | cmn_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 1.00MB |
| Welsh (cy) | cy_dual_basiccorcencc2usas_contextual | :heavy_check_mark: | Basic CorCenCC 2 USAS | Contextual | 1.09MB |
| Welsh (cy) | cy_single_basiccorcencc2usas_contextual | :x: | Basic CorCenCC 2 USAS | Contextual | 1.09MB |
| Spanish, Castilian (es) | es_dual_upos2usas_contextual | :heavy_check_mark: | UPOS 2 USAS | Contextual | 0.20MB |
| Spanish, Castilian (es) | es_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 0.16MB |
| French (fr) | fr_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 0.08MB |
| Indonesian (id) | id_single_none_contextual | :x: | None | Contextual | 0.24MB |
| Italian (it) | it_dual_upos2usas_contextual | :heavy_check_mark: | UPOS 2 USAS | Contextual | 0.50MB |
| Italian (it) | it_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 0.42MB |
| Dutch, Flemish (nl) | nl_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 0.15MB |
| Portuguese (pt) | pt_dual_upos2usas_contextual | :heavy_check_mark: | UPOS 2 USAS | Contextual | 0.27MB |
| Portuguese (pt) | pt_single_upos2usas_contextual | :x: | UPOS 2 USAS | Contextual | 0.25MB |

* MWE -- :heavy_check_mark: means that the model supports identification and tagging of Multi Word Expressions.

## Issues / bug reports / improving the models

These models are **not statistical** they are **rule based**, however they are still error prone as not all rules will cover every situation and in some cases this is not possible. If you are finding a lot of mis-classified tokens please do file a report on the [PyMUSAS issue tracker](https://github.com/UCREL/pymusas/issues) so that we can try to improve the model. Thank you in advance for your support.

## Development

If you are contributing to this repository, please go to the [CONTRIBUTING.md](./CONTRIBUTING.md) file to learn more about how to contribute to this repository and in general learn more about this repository.

## Acknowledgements

The contents of this README is heavily based on the [spaCy models repository](https://github.com/explosion/spacy-models) README, many thanks for writing that great README.