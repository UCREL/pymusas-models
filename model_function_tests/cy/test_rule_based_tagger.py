import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Adran', 'Iechyd', '.', 'Sefydliad', 'cyllidol', '.', '5']
TEST_TAGS = ['E', 'E', 'Atd', 'E', 'Ans', 'Atd', 'Rhi']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    welsh_model = spacy.load("cy_single_basiccorcencc2usas_contextual_none",
                             config={"components.pymusas_rule_based_tagger.pos_attribute": "tag_"})
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, tags=TEST_TAGS)
    output = welsh_model(doc)
    expected_output = [
        ['A1.1.1', 'B3/X1'],
        ['B2', 'X9.2'],
        ['PUNCT'],
        ['S5+c', 'S7.1+', 'H1c', 'S1.1.1', 'T2+'],
        ['I1'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    welsh_model = spacy.load("cy_dual_basiccorcencc2usas_contextual_none",
                             config={"components.pymusas_rule_based_tagger.pos_attribute": "tag_"})
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, tags=TEST_TAGS)
    output = welsh_model(doc)
    expected_output = [
        ['G1.1'],
        ['G1.1'],
        ['PUNCT'],
        ['S5+c', 'S7.1+', 'H1c', 'S1.1.1', 'T2+'],
        ['I1'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        if token_index == 0 or token_index == 1:
            assert [(0, 2)] == token._.pymusas_mwe_indexes
        else:
            assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
