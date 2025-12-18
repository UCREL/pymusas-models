
import hashlib
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Tuple, cast

import pymusas
from pymusas.lexicon_collection import LexiconCollection, MWELexiconCollection
from pymusas.pos_mapper import (
    BASIC_CORCENCC_TO_USAS_CORE,
    UPOS_TO_USAS_CORE,
    USAS_CORE_TO_BASIC_CORCENCC,
    USAS_CORE_TO_UPOS,
)
from pymusas.rankers.lexicon_entry import ContextualRuleBasedRanker
from pymusas.spacy_api.taggers import neural, rule_based  # noqa: F401
from pymusas.taggers.rules.mwe import MWERule as PymusasMWERule
from pymusas.taggers.rules.rule import Rule as PymusasRule
from pymusas.taggers.rules.single_word import SingleWordRule as PymusasSingleWordRule
import spacy
import srsly
import typer
from wasabi import MarkdownRenderer

from pymusas_models.language_resource import (
    LanguageResources,
    ModelTypes,
    MWERule,
    NeuralModel,
    POSMapper,
    RuleModel,
    RuleRankers,
    RuleType,
    SingleRule,
)
from pymusas_models.package import generate_readme, package


REPO_DIRECTORY = Path(__file__, '..', '..').resolve()
PYMUSAS_LANG_TO_SPACY = {
    'cmn': 'zh',
    'nl': 'nl',
    'fr': 'fr',
    'it': 'it',
    'pt': 'pt',
    'es': 'es',
    'cy': 'xx',
    'id': 'id',
    'fi': 'fi',
    'en': 'en',
    'da': 'da',
    'xx': 'xx'
}
POS_MAPPER_TO_NAME = {
    'UPOS': 'upos2usas',
    'BasicCorCenCC': 'basiccorcencc2usas',
    None: 'none'
}
app = typer.Typer()
OPTION = typer.Option


def get_pymusas_version_bounds() -> str:
    """
    Returns the version bounds of the pymusas package as a string.
    
    The returned string is in the format ">=a,<b", where "a" is the current
    pymusas package version and "b" is the current pymusas package version
    plus one minor version number.

    For instance if the current version of pymusas is `0.3.3` then this would
    return `>=0.3.3,<0.4.0`.

    # Returns

    `str`
    """
    pymusas_version = pymusas.__version__
    pymusas_major, pymusas_minor, pymusas_patch = pymusas_version.split('.')
    pymusas_minor_int = int(pymusas_minor)
    pymusas_lower_bound = f"{pymusas_major}.{pymusas_minor}.{pymusas_patch}"
    pymusas_upper_bound = f"{pymusas_major}.{pymusas_minor_int + 1}.0"
    return f">={pymusas_lower_bound},<{pymusas_upper_bound}"


def create_notes(package_name: str) -> str:
    package_wheel_url = ("https://github.com/UCREL/pymusas-models/releases/"
                         f"download/{package_name}/{package_name}"
                         "-py3-none-any.whl")
    return (f"# Installation\n``` bash\npip install {package_wheel_url}\n```")


def create_description(language_name: str, package_name: str,
                       dist_file_names: Tuple[str, str],
                       tar_gz_checksum: str, wheel_checksum: str) -> str:
    
    def create_dist_download_shield(dist_name: str) -> str:
        shield_html = ('<a href="https://github.com/UCREL/pymusas-models/'
                       f'releases/download/{package_name}/{dist_name}">'
                       '<img src="https://img.shields.io/github/downloads/'
                       f'UCREL/pymusas-models/{package_name}/{dist_name}'
                       '?label=downloads&style=flat-square"/></a>')
        return shield_html
    
    dist_shield_0 = create_dist_download_shield(dist_file_names[0])
    dist_shield_1 = create_dist_download_shield(dist_file_names[1])
    
    description = (f'<p>\n{dist_shield_0}\n{dist_shield_1}\n</p>\n\n'
                   f'> **Checksum (SHA256) .tar.gz:** `{tar_gz_checksum}`\n\n'
                   f'> **Checksum (SHA256) .whl:** `{wheel_checksum}`\n\n'
                   f'{language_name} USAS semantic tagger')
    return description


def add_model_specific_meta_data(model_directory: Path, language_name: str,
                                 package_name: str) -> None:
    '''
    All of this meta data is specific to each model, also it will only be
    used to generate the README and won't be accessible through the models
    `meta` attribute.

    meta data added:

    * More accurate `spacy_version`
    * SHA256 checksums for both the `.tar.gz` and `wheel` build files.
    * File size, in MB or GB, of the largest build file.
    * Description - see `create_description` function.
    * Notes - see `create_notes` function.
    '''
    model_meta_file = Path(model_directory, 'meta.json')
    if not model_meta_file.exists():  # pragma: no cover
        file_err = (f'Could not find the model meta file {model_meta_file}.')
        raise FileNotFoundError(file_err)
    
    model_meta_data = srsly.read_json(model_meta_file)
    
    dist_folder = Path(model_directory, 'dist')
    dist_files = list(dist_folder.iterdir())
    dist_file_names: List[str] = []
    if len(dist_files) > 2:  # pragma: no cover
        number_dist_files_error = ('The dist folder within the model directory '
                                   'contains more than 2 files. The only two '
                                   'files should be a `.whl` and `.tar.gz`'
                                   f'. Files within the folder: {dist_files}'
                                   ' The path to the dist folder directory: '
                                   f'{dist_folder}')
        raise ValueError(number_dist_files_error)
    
    max_model_size = 0
    for dist_file in dist_files:
        dist_size = dist_file.stat().st_size
        if dist_size > max_model_size:
            max_model_size = dist_size
        
        dist_file_hash = hashlib.sha256(dist_file.read_bytes()).hexdigest()
        dist_file_suffix = dist_file.suffix
        if dist_file_suffix == '.whl':
            model_meta_data["checksum_whl"] = dist_file_hash
        elif dist_file_suffix == '.gz':
            model_meta_data["checksum"] = dist_file_hash
        else:  # pragma: no cover
            dist_file_error = ('All the files in the dist folder should either'
                               ' have a suffix of `.whl` or `.gz` and not '
                               f'{dist_file_suffix}. Files '
                               f'within the folder: {dist_files}. The path '
                               f'to the dist folder directory: {dist_folder}')
            raise ValueError(dist_file_error)
        dist_file_names.append(dist_file.name)

    model_size_mb = float(max_model_size) / math.pow(2, 20)
    model_size_str = f'{model_size_mb:.2f}MB'
    model_meta_data["size"] = model_size_str
    model_meta_data["full_language_name"] = language_name
    srsly.write_json(model_meta_file, model_meta_data)

    assert len(dist_file_names) == 2
    dist_file_name_tuple = (dist_file_names[0], dist_file_names[1])
    model_meta_data["description"] = create_description(language_name, package_name,
                                                        dist_file_name_tuple,
                                                        model_meta_data["checksum"],
                                                        model_meta_data["checksum_whl"])
    model_meta_data["notes"] = create_notes(package_name)
    # Given the updated meta data we update the README.
    readme_file = Path(model_directory, 'README.md')
    with readme_file.open('w', encoding='utf-8') as readme_fp:
        readme_fp.write(generate_readme(model_meta_data))


def add_default_meta_data(spacy_meta: Dict[str, Any],
                          model_type: ModelTypes) -> None:
    '''
    Adds the following meta data to the `spacy_meta` object (all of these are
    used as meta data for the Python package), all of this meta data will be
    easily accessible through the models `meta` attribute:

    * author
    * email - authors email address
    * url - URL associated to the models/project/author
    * license
    * requirements

    # Parameters

    spacy_meta: `Dict[str, Any]`
        The meta data dictionary that has come from the existing spaCy pipeline.
        `spacy_pipeline.meta`. This meta data dictionary will be added too.

    model_type: `ModelTypes`
        The type of the model that the meta data is being added to.

    # Returns

    `None`
    '''
    spacy_meta["author"] = "UCREL Research Centre"
    spacy_meta["email"] = "ucrel@lancaster.ac.uk"
    spacy_meta["url"] = "https://ucrel.github.io/pymusas/"
    spacy_meta["license"] = "CC BY-NC-SA 4.0"

    pymusas_requirement = f"pymusas{get_pymusas_version_bounds()}"
    if model_type == ModelTypes.NEURAL:
        pymusas_requirement = f"pymusas[neural]{get_pymusas_version_bounds()}"
    spacy_meta["requirements"] = [pymusas_requirement]


MODEL_DIRECTORY_HELP = '''
A path to a directory whereby all of the PyMUSAS models will be stored
in their own separate folders within this directory.
'''
LANGUAGE_RESOURCE_FILE_HELP = '''
A path to a language resource meta data file, see the `CONTRIBUTING.md`
under section `Language Resource Meta Data` for details
on how the meta data should be structured. This meta data file specifies
what PyMUSAS models should be created based on the meta data contents.
'''
MODEL_VERSION_HELP = '''
The value of the model version. This is the `c` element as described in
`Model versioning` within the main README. The `a` and `b` element come from
the PyMUSAS version used.
'''


def get_pos_mapper(pos_mapper: POSMapper,
                   rule_type: RuleType
                   ) -> Dict[str, List[str]]:
    '''
    Given a POSMapper and a RuleType, return a dictionary which maps from
    a POS tagset to another whereby the mapping used is dependent on the POSMapper
    given and the direction of the mapping is determined by the RuleType.
    
    If RuleType is;
    `SINGLE`: It maps from the token's POS tagset to the POS tagset used in the
    lexicon.
    
    `MWE`: It maps from the POS tagset used in the lexicon to the token's POS
    tagset.

    If the POSMapper is `BASICCORCENCC2USAS` then the mapping is as follows:

    `SINGLE`. `BASIC_CORCENCC` -> `USAS_CORE`
    `MWE`. `USAS_CORE` -> `BASIC_CORCENCC`

    If the POSMapper is `UPOS2USAS` then the mapping is as follows:

    `SINGLE`. `UPOS` -> `USAS_CORE`
    `MWE`. `USAS_CORE` -> `UPOS`

    # Parameters
    
    pos_mapper: `POSMapper`
        The POSMapper to use when generating the mapping.
    rule_type: `RuleType`
        The type of rule that the mapping is for.

    # Returns
    
    `dict[str, list[str]]`
        

    # Raises
    
    `ValueError`
        If the POSMapper is not recognized.
    '''
    if pos_mapper == POSMapper.UPOS2USAS:
        if rule_type == RuleType.SINGLE:
            return UPOS_TO_USAS_CORE
        elif rule_type == RuleType.MWE:
            return USAS_CORE_TO_UPOS
    elif pos_mapper == POSMapper.BASICCORCENCC2USAS:
        if rule_type == RuleType.SINGLE:
            return BASIC_CORCENCC_TO_USAS_CORE
        elif rule_type == RuleType.MWE:
            return USAS_CORE_TO_BASIC_CORCENCC
    else:
        raise ValueError(f"Cannot find this pos mapper: {pos_mapper}")


@app.command("create-models")
def create_models(models_directory: Path = OPTION(Path(REPO_DIRECTORY, 'models'),
                                                  help=MODEL_DIRECTORY_HELP,
                                                  exists=False, file_okay=False,
                                                  dir_okay=True, resolve_path=True),
                  language_resource_file: Path = OPTION(Path(REPO_DIRECTORY, 'language_resources.json'),
                                                        help=LANGUAGE_RESOURCE_FILE_HELP,
                                                        exists=True, file_okay=True,
                                                        dir_okay=False, writable=False,
                                                        readable=True, resolve_path=True),
                  model_version: str = OPTION('0', help=MODEL_VERSION_HELP)
                  ) -> None:
    '''
    Creates all of the PyMUSAS models, based on the meta data within the
    `language_resource_file`, and stores all of these models within the given
    `models_directory`.
    '''

    meta_data: str = ""
    with language_resource_file.open('r', encoding='utf-8') as _file:
        meta_data = _file.read()
    assert meta_data, f'The {language_resource_file} is empty.'
    language_data = LanguageResources.model_validate_json(meta_data)

    for language_code, language_resource in language_data.language_resources.items():
        spacy_version = language_resource.spacy_version
        for model in language_resource.models:
            model_name = model.name

            spacy_pipeline = spacy.blank(PYMUSAS_LANG_TO_SPACY[language_code])
            
            model_type = model.model_type
            if model_type == ModelTypes.RULE:
                model = cast(RuleModel, model)

                model_config = model.config
                rule_tagger = cast(rule_based.RuleBasedTagger,
                                   spacy_pipeline.add_pipe(model_type.value,
                                                           config=model_config.model_dump()))
                
                model_rules = model.resources.rules
                
                pymusas_rules: list[PymusasRule] = []
                for rule in model_rules:
                    rule_type = rule.rule_type
                    pos_mapper_data: None | Dict[str, List[str]] = None
                    if rule_type == RuleType.SINGLE:
                        rule = cast(SingleRule, rule)
                        pos_mapper = rule.pos_mapper
                        if pos_mapper is not None:
                            pos_mapper_data = get_pos_mapper(pos_mapper, rule_type)
                        lemma_lexicon = LexiconCollection.from_tsv(rule.lexicon_url, include_pos=False)
                        lexicon_collection = {}
                        if rule.with_pos:
                            lexicon_collection = LexiconCollection.from_tsv(rule.lexicon_url, include_pos=True)
                        pymusas_single_rule = PymusasSingleWordRule(lexicon_collection, lemma_lexicon, pos_mapper=pos_mapper_data)
                        pymusas_rules.append(pymusas_single_rule)
                    elif rule_type == RuleType.MWE:
                        rule = cast(MWERule, rule)
                        pos_mapper = rule.pos_mapper
                        if pos_mapper is not None:
                            pos_mapper_data = get_pos_mapper(pos_mapper, rule_type)
                        mwe_lexicon_collection = MWELexiconCollection.from_tsv(rule.lexicon_url)
                        pymusas_mwe_rule = PymusasMWERule(mwe_lexicon_collection, pos_mapper=pos_mapper_data)
                        pymusas_rules.append(pymusas_mwe_rule)
                    else:  # pragma: no cover
                        raise ValueError(f"Cannot find this rule type: {rule_type} for {model_name}")
                    
                if not pymusas_rules:
                    raise ValueError(f"Cannot find any rules for: {model_name}")
                    
                pymusas_ranker: None | ContextualRuleBasedRanker = None
                if model.resources.ranker == RuleRankers.CONTEXTUAL:
                    pymusas_ranker = ContextualRuleBasedRanker(*ContextualRuleBasedRanker.get_construction_arguments(pymusas_rules))
                
                if pymusas_ranker is None:
                    raise ValueError(f"Ranker found: {model.resources.ranker} "
                                     f"the only rankers supported are {list(RuleRankers)} "
                                     f"for: {model_name}")
                rule_tagger.initialize(rules=pymusas_rules,
                                       ranker=pymusas_ranker,
                                       default_punctuation_tags=model.resources.default_punctuation_tags,
                                       default_number_tags=model.resources.default_number_tags)
            elif model_type == ModelTypes.NEURAL:
                model = cast(NeuralModel, model)
                neural_tagger = cast(neural.NeuralTagger,
                                     spacy_pipeline.add_pipe(model_type.value,
                                                             config=model.config.model_dump()))
                neural_tagger.initialize(pretrained_model_name_or_path=model.pretrained_model_name_or_path)
            else:
                raise ValueError(f"Cannot find this model type: {model_type} for: {model_name}")

            add_default_meta_data(spacy_pipeline.meta, model_type)
            spacy_pipeline.meta['spacy_version'] = spacy_version

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                spacy_pipeline.to_disk(temp_dir_path)

                full_model_version_list = pymusas.__version__.split('.')[:2]
                full_model_version_list.append(model_version)
                full_model_version = '.'.join(full_model_version_list)
                package_name = f'{model_name}-{full_model_version}'
                
                # Create model
                models_directory.mkdir(parents=True, exist_ok=True)
                package(temp_dir_path, models_directory,
                        create_sdist=True,
                        create_wheel=True, name=model_name,
                        version=full_model_version)
                model_directory = Path(models_directory, f'{package_name}')
                add_model_specific_meta_data(model_directory,
                                             language_resource.language_data.description,
                                             package_name)


EXISTING_MODEL_DIRECTORY_HELP = '''
A path to a directory that is storing the PyMUSAS models.
'''


@app.command("overview-of-models")
def overview_of_models(models_directory: Path = OPTION(Path(REPO_DIRECTORY, 'models'),
                                                       help=EXISTING_MODEL_DIRECTORY_HELP,
                                                       exists=True, file_okay=False,
                                                       dir_okay=True, resolve_path=True)) -> None:
    '''
    Prints to stdout a Markdown table whereby each row is a PyMUSAS model that
    is a available/released. Every row contains the following information
    about the relevant PyMUSAS model:

    1. Language (BCP 47 language code)
    2. Model name.
    3. MWE
    4. POS Mapper
    5. Ranker
    6. Neural Model
    7. File Size
    '''
    md = MarkdownRenderer()
    headers = ["Language (BCP 47 language code)", "Model Name",
               "MWE", "POS Mapper", "Ranker", "Neural Model", "File Size"]
    table_data: List[List[str]] = []

    models_directories = sorted(models_directory.iterdir(),
                                key=lambda x: (x.name.split('_')[0],
                                               x.name.split('_')[1]))
    
    neural_model_mapper = {
        "englishsmallbem": "[ucrelnlp/PyMUSAS-Neural-English-Small-BEM](https://huggingface.co/ucrelnlp/PyMUSAS-Neural-English-Small-BEM)",
        "englishbasebem": "[ucrelnlp/PyMUSAS-Neural-English-Base-BEM](https://huggingface.co/ucrelnlp/PyMUSAS-Neural-English-Base-BEM)",
        "multilingualsmallbem": "[ucrelnlp/PyMUSAS-Neural-Multilingual-Small-BEM](https://huggingface.co/ucrelnlp/PyMUSAS-Neural-Multilingual-Small-BEM)",
        "multilingualbasebem": "[ucrelnlp/PyMUSAS-Neural-Multilingual-Base-BEM](https://huggingface.co/ucrelnlp/PyMUSAS-Neural-Multilingual-Base-BEM)"
    }

    for model_direcotry in models_directories:
        meta_data_file = Path(model_direcotry, 'meta.json')
        model_meta_data = srsly.read_json(meta_data_file)
        
        model_name = model_meta_data["name"]
        
        language_name = model_meta_data["full_language_name"]
        bcp_47_code = model_name.split("_")[0]
        language_code = f'{language_name} ({bcp_47_code})'
        
        mwe = ':x:'
        if 'dual' in model_name:
            mwe = ':heavy_check_mark:'
        
        model_pos_mapper = 'None'
        if 'upos2usas' in model_name:
            model_pos_mapper = 'UPOS 2 USAS'
        elif 'basiccorcencc2usas' in model_name:
            model_pos_mapper = 'Basic CorCenCC 2 USAS'
        
        ranker = model_name.split('_')[-2]
        if ranker == 'none':
            ranker = ':x:'
        else:
            ranker = ranker.capitalize()

        neural_model = model_name.split('_')[-1]
        if neural_model == 'none':
            neural_model = ':x:'
        else:
            model_pos_mapper = ':x:'
            neural_model = neural_model_mapper[neural_model]
        file_size = model_meta_data['size']

        table_data.append([language_code, model_name, mwe,
                           model_pos_mapper, ranker, neural_model, file_size])

    md.add(md.table(table_data, headers))
    print(md.text)


if __name__ == '__main__':
    app(prog_name="pymusas-models")  # pragma: no cover
