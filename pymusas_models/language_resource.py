from enum import Enum
from typing import Annotated, Any

from pydantic import BaseModel, PlainValidator


class ModelTypes(str, Enum):
    RULE = "pymusas_rule_based_tagger"
    NEURAL = "pymusas_neural_tagger"


class RuleRankers(str, Enum):
    CONTEXTUAL = "contextual"


class RuleType(str, Enum):
    SINGLE = "single"
    MWE = "mwe"


class POSMapper(str, Enum):
    UPOS2USAS = "upos2usas"
    BASICCORCENCC2USAS = "basiccorcencc2usas"


class Model(BaseModel):
    name: str
    model_type: ModelTypes


class Rule(BaseModel):
    rule_type: RuleType


class SingleRule(Rule):
    rule_type: RuleType = RuleType.SINGLE
    pos_mapper: POSMapper | None
    lexicon_url: str
    with_pos: bool


class MWERule(Rule):
    rule_type: RuleType = RuleType.MWE
    pos_mapper: POSMapper | None
    lexicon_url: str


def get_rule_type(rules: list[Any]) -> list[SingleRule | MWERule]:
    validate_rule_types: list[SingleRule | MWERule] = []

    for rule in rules:
        if rule["rule_type"] == RuleType.SINGLE.value:
            validate_rule_types.append(SingleRule.model_validate(rule))
        elif rule["rule_type"] == RuleType.MWE.value:
            validate_rule_types.append(MWERule.model_validate(rule))
        else:
            raise ValueError(f"Invalid rule type: {rule['rule_type']} for rule: {rule}")

    return validate_rule_types


class RuleResources(BaseModel):
    ranker: RuleRankers
    rules: Annotated[list[Rule], PlainValidator(get_rule_type)]
    default_punctuation_tags: list[str] | None = None
    default_number_tags: list[str] | None = None


class RuleConfig(BaseModel):
    pymusas_tags_token_attr: str = 'pymusas_tags'
    pymusas_mwe_indexes_attr: str = 'pymusas_mwe_indexes'
    pos_attribute: str = 'pos_'
    lemma_attribute: str = 'lemma_'


class NeuralConfig(BaseModel):
    pymusas_tags_token_attr: str = 'pymusas_tags'
    pymusas_mwe_indexes_attr: str = 'pymusas_mwe_indexes'
    top_n: int = 5
    device: str = 'cpu'
    tokenizer_kwargs: dict[str, Any] | None = None


class RuleModel(Model):
    model_type: ModelTypes = ModelTypes.RULE
    resources: RuleResources
    config: RuleConfig = RuleConfig()


class NeuralModel(Model):
    model_type: ModelTypes = ModelTypes.NEURAL
    pretrained_model_name_or_path: str
    config: NeuralConfig = NeuralConfig()


class LanguageData(BaseModel):
    description: str
    macrolanguage: str
    script: str


def get_model_type(models: list[Any]) -> list[RuleModel | NeuralModel]:
    validate_model_types: list[RuleModel | NeuralModel] = []

    for model in models:
        if model["model_type"] == ModelTypes.RULE.value:
            validate_model_types.append(RuleModel.model_validate(model))
        elif model["model_type"] == ModelTypes.NEURAL.value:
            validate_model_types.append(NeuralModel.model_validate(model))
        else:
            raise ValueError(f"Invalid model type: {model['model_type']} for model: {model}")

    return validate_model_types


class LanguageResource(BaseModel):
    language_data: LanguageData
    models: Annotated[list[Model], PlainValidator(get_model_type)]
    spacy_version: str = ">=3.0,<4.0"


class LanguageResources(BaseModel):
    language_resources: dict[str, LanguageResource]
