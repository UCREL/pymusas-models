import pytest
import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Sporting', 'community', 'hack', 'had', '.', '49557282', '\t']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_small_neural() -> None:
    english_model = spacy.load("en_none_none_none_englishsmallbem")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES)
    output = english_model(doc)
    expected_output = [
        ['K5.1', 'G2.2', 'A6.2', 'S2', 'O4.2'],
        ['S5', 'S1.1.1', 'S2', 'K1', 'O2'],
        ['Y2', 'A1.1.1', 'O2', 'L2', 'S2'],
        ['S4', 'A2.2', 'A9', 'Z5', 'S6'],
        ['S2', 'O3', 'Z5', 'N3.2', 'Z2'],
        ['N1', 'T1.2', 'N3.2', 'T1.3', 'T3'],
        ['Z9']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


@pytest.mark.ci
def test_base_neural() -> None:
    english_model = spacy.load("en_none_none_none_englishbasebem")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES)
    output = english_model(doc)
    expected_output = [
        ['K5.1', 'G2.2', 'F1', 'A1.1.1', 'A9'],
        ['S5', 'A4.1', 'O2', 'P1', 'K5.1'],
        ['Y2', 'O2', 'S2', 'A1.1.1', 'Q4.2'],
        ['A9', 'Z5', 'S4', 'A2.2', 'S6'],
        ['Z5', 'A7', 'A15', 'Z8', 'I1'],
        ['N1', 'T1.2', 'T1.3', 'T3', 'N3.2'],
        ['Z9']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
