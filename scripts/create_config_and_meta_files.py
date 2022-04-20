import hashlib
import json
import math
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional, Tuple

import pymusas
from pymusas.spacy_api import lexicon_collection, pos_mapper, rankers  # noqa: F401
from pymusas.spacy_api.taggers import rule_based, rules  # noqa: F401
import spacy
from spacy.cli.package import package
import srsly

from pymusas_models.readme_generator import generate_readme


PYMUSAS_LANG_TO_SPACY = {
    'cmn': 'zh',
    'nl': 'nl',
    'fr': 'fr',
    'it': 'it',
    'pt': 'pt',
    'es': 'es',
    'cy': 'xx',
    'id': 'id'
}


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
    
    description = (f'# {package_name}\n'
                   f'<p>\n{dist_shield_0}\n{dist_shield_1}\n</p>\n\n'
                   f'> **Checksum (SHA256) .tar.gz:** `{tar_gz_checksum}`\n\n'
                   f'> **Checksum (SHA256) .whl:** `{wheel_checksum}`\n\n'
                   f'{language_name} USAS semantic tagger')
    return description


def add_model_specific_meta_data(model_directory: Path, language_name: str,
                                 package_name: str) -> None:
    model_meta_file = Path(model_directory, 'meta.json')
    if not model_meta_file.exists():
        file_err = (f'Could not find the model meta file {model_meta_file}.')
        raise FileNotFoundError(file_err)
    
    model_meta_data = srsly.read_json(model_meta_file)
    model_meta_data["spacy_version"] = "spacy>=3.0"
    
    dist_folder = Path(model_directory, 'dist')
    dist_files = list(dist_folder.iterdir())
    dist_file_names: List[str] = []
    if len(dist_files) > 2:
        number_dist_files_error = ('The dist folder within the model directory '
                                   'contains more than 2 files. The only two '
                                   'files should be a `.whl` and `.tar.gz`'
                                   f'. Files within the folder: {dist_files}'
                                   ' The path to the dist folder directory: '
                                   f'{dist_folder}')
        raise ValueError(number_dist_files_error)
    
    max_model_size = 0
    for dist_file in dist_files:
        non_spacy_lang_code_file_name = '_'.join(dist_file.name.split('_')[1:])
        non_spacy_lang_code_file_path = Path(dist_file.parent,
                                             non_spacy_lang_code_file_name)
        dist_file.rename(non_spacy_lang_code_file_path)
        dist_file = non_spacy_lang_code_file_path
        dist_size = dist_file.stat().st_size
        if dist_size > max_model_size:
            max_model_size = dist_size
        
        dist_file_hash = hashlib.sha256(dist_file.read_bytes()).hexdigest()
        dist_file_suffix = dist_file.suffix
        if dist_file_suffix == '.whl':
            model_meta_data["checksum_whl"] = dist_file_hash
        elif dist_file_suffix == '.gz':
            model_meta_data["checksum"] = dist_file_hash
        else:
            dist_file_error = ('All the files in the dist folder should either'
                               ' have a suffix of `.whl` or `.gz` and not '
                               f'{dist_file_suffix}. Files '
                               f'within the folder: {dist_files}. The path '
                               f'to the dist folder directory: {dist_folder}')
            raise ValueError(dist_file_error)
        dist_file_names.append(dist_file.name)

    model_size_mb = f'{float(max_model_size) / math.pow(2, 20):.2f}MB'
    model_meta_data["size"] = model_size_mb
    srsly.write_json(model_meta_file, model_meta_data)

    assert len(dist_file_names) == 2
    dist_file_name_tuple = (dist_file_names[0], dist_file_names[1])
    model_meta_data["description"] = create_description(language_name, package_name,
                                                        dist_file_name_tuple,
                                                        model_meta_data["checksum"],
                                                        model_meta_data["checksum_whl"])
    
    # Given the updated meta data we update the README.
    readme_file = Path(model_directory, 'README.md')
    with readme_file.open('w', encoding='utf-8') as readme_fp:
        readme_fp.write(generate_readme(model_meta_data))


def add_default_meta_data(spacy_meta: Dict[str, Any]) -> None:
    spacy_meta["author"] = "UCREL Research Centre"
    spacy_meta["email"] = "ucrel@lancaster.ac.uk"
    spacy_meta["url"] = "https://ucrel.github.io/pymusas/"
    spacy_meta["license"] = "CC BY-NC-SA 4.0"


def create_pymusas_config(spacy_config: Dict[str, Any], single_lexicon_url: str,
                          model_pos_mapper: Optional[str],
                          mwe_lexicon_url: Optional[str] = None) -> None:
    
    def create_pos_mapper_dict(pos_mapper_registered_function: Optional[str]
                               ) -> Optional[Dict[str, str]]:
        if pos_mapper_registered_function is None:
            return None
        return {"@misc": pos_mapper_registered_function}
    
    single_lexicon_pos_mapper_registered_function: Optional[str] = None
    mwe_lexicon_pos_mapper_registered_function: Optional[str] = None
    default_punctuation_tags: Optional[List[str]] = None
    default_number_tags: Optional[List[str]] = None

    if model_pos_mapper == 'UPOS':
        single_lexicon_pos_mapper_registered_function = "pymusas.pos_mapper.UPOS_TO_USAS_COREv1"
        mwe_lexicon_pos_mapper_registered_function = "pymusas.pos_mapper.USAS_CORE_TO_UPOSv1"
        default_punctuation_tags = ["PUNCT"]
        default_number_tags = ["NUM"]
    elif model_pos_mapper == 'BasicCorCenCC':
        single_lexicon_pos_mapper_registered_function = "pymusas.pos_mapper.UPOS_TO_USAS_COREv1"
        mwe_lexicon_pos_mapper_registered_function = "pymusas.pos_mapper.USAS_CORE_TO_UPOSv1"
        default_punctuation_tags = ["Atd"]
        default_number_tags = ["Rhi"]
    elif model_pos_mapper is not None:
        raise ValueError('The pos mapper has to be either `UPOS`, '
                         f'`BasicCorCenCC` or `None`, but not {model_pos_mapper}.')

    single_pos_mapper = create_pos_mapper_dict(single_lexicon_pos_mapper_registered_function)
    mwe_pos_mapper = create_pos_mapper_dict(mwe_lexicon_pos_mapper_registered_function)

    single_lexicon_rule = {
        "@misc": "pymusas.taggers.rules.SingleWordRule.v1",
        "pos_mapper": single_pos_mapper,
        "lexicon_collection": {
            "@misc": "pymusas.LexiconCollection.from_tsv",
            "tsv_file_path": single_lexicon_url,
            "include_pos": True
        },
        "lemma_lexicon_collection": {
            "@misc": "pymusas.LexiconCollection.from_tsv",
            "tsv_file_path": single_lexicon_url,
            "include_pos": False
        }
    }
    mwe_lexicon_rule = {
        "@misc": "pymusas.taggers.rules.MWERule.v1",
        "pos_mapper": mwe_pos_mapper,
        "mwe_lexicon_lookup": {
            "@misc": "pymusas.MWELexiconCollection.from_tsv",
            "tsv_file_path": mwe_lexicon_url,
        }
    }

    lexicon_rules: Dict[str, Any] = {
        "@misc": "pymusas.taggers.rules.rule_list",
        "*": {
            "single": single_lexicon_rule
        }
    }
    if mwe_lexicon_url:
        lexicon_rules["*"]["mwe"] = mwe_lexicon_rule

    spacy_config["pymusas_rules"] = lexicon_rules
    
    if language_code == 'id':
        default_punctuation_tags = ["Z"]
        default_number_tags = ["CD"]

    spacy_config["initialize"]["components"]["pymusas_rule_based_tagger"] = {
        "ranker": {
            "@misc": "pymusas.rankers.ContextualRuleBasedRanker.v1",
            "rules": "${pymusas_rules}"
        },
        "default_punctuation_tags": default_punctuation_tags,
        "default_number_tags": default_number_tags,
        "rules": "${pymusas_rules}"
    }


if __name__ == '__main__':
    repo_directory = Path(__file__, '..', '..').resolve()
    language_resource_file = Path(repo_directory, 'language_resources.json')
    meta_data: Dict[str, Any] = {}
    with language_resource_file.open('r', encoding='utf-8') as _file:
        meta_data = json.load(_file)
    assert meta_data, f'The {language_resource_file} is empty.'

    for language_code, data in meta_data.items():
        resources: List[Dict[str, str]] = data['resources']
        single_lexicon_url = ''
        mwe_lexicon_url = ''
        for resource in resources:
            resource_data_type = resource['data type']
            if resource_data_type == 'single':
                single_lexicon_url = resource['url']
            elif resource_data_type == 'mwe':
                mwe_lexicon_url = resource['url']
            else:
                raise ValueError('Do not recognise this resource data type: '
                                 f'{resource_data_type} for language code: '
                                 f'{language_code}')
        
        model_information: Dict[str, Optional[str]] = data['model information']
        language_data: Dict[str, str] = data['language data']

        # Create the Single word lexicon only model first
        if not single_lexicon_url:
            raise ValueError('The `single` data type for language code: '
                             f'{language_code} is empty.')
        
        model_pos_mapper = model_information['POS mapper']
        
        pos_attribute = 'pos_'  # default
        if language_code == 'cy' or language_code == 'id':
            pos_attribute = 'tag_'
        pymusas_config = {"pos_attribute": pos_attribute}
        
        spacy_pipeline = spacy.blank(PYMUSAS_LANG_TO_SPACY[language_code])
        spacy_pipeline.add_pipe("pymusas_rule_based_tagger", config=pymusas_config)
        create_pymusas_config(spacy_pipeline.config, single_lexicon_url,
                              model_pos_mapper)
        try:
            spacy_pipeline.initialize()
            add_default_meta_data(spacy_pipeline.meta)
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                spacy_pipeline.to_disk(temp_dir_path)
                #
                model_name = f'{language_code}_single_{model_pos_mapper}_contextual'
                model_version = pymusas.__version__
                package_name = f'{model_name}-{model_version}'
                spacy_lang_code = PYMUSAS_LANG_TO_SPACY[language_code]
                # Create model
                models_directory = Path(repo_directory, 'models')
                models_directory.mkdir(parents=True, exist_ok=True)
                package(temp_dir_path, models_directory, create_sdist=True,
                        create_wheel=True, name=model_name,
                        version=model_version)
                
                model_directory = Path(models_directory,
                                       f'{spacy_lang_code}_{package_name}')
                
                add_model_specific_meta_data(model_directory,
                                             language_data['description'],
                                             package_name)
                break

        except Exception:
            line_break = "-" * 20
            error_msg = (f"\n{line_break}\n"
                         f"Error occurred for language code: {language_code}.\n\n"
                         "Configuration file of the spaCy pipeline being "
                         f"initialized: {json.dumps(spacy_pipeline.config, sort_keys=True, indent=4)}")
            print(error_msg)
            raise
