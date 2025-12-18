import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Sporting', 'community', 'hack', 'had', '.', '49557282', '\t']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_small_neural() -> None:
    multi_ling_model = spacy.load("xx_none_none_none_multilingualsmallbem")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES)
    output = multi_ling_model(doc)
    expected_output = [
        ['K5.1', 'A6.2', 'Z3', 'G2.2', 'S5'],
        ['S5', 'K5.1', 'A10', 'Z3', 'X2.1'],
        ['Y2', 'O2', 'A1.1.2', 'A1.1.1', 'F1'],
        ['A9', 'Z5', 'S4', 'A2.2', 'S6'],
        ['Z5', 'K5.1', 'Z3', 'T1.3', 'N1'],
        ['T1.3', 'N1', 'T3', 'T1.2', 'N3.2'],
        ['Z9']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_base_neural() -> None:
    multi_ling_model = spacy.load("xx_none_none_none_multilingualbasebem")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES)
    output = multi_ling_model(doc)
    expected_output = [
        ['K5.1', 'G2.2', 'Z3', 'O4.2', 'A1.1.1'],
        ['S5', 'S1.1.1', 'G1.1', 'O2', 'S2'],
        ['S2', 'O2', 'Y2', 'F1', 'B1'],
        ['A9', 'S4', 'Z5', 'A2.2', 'S1.1.1'],
        ['Z5', 'Z1', 'Z3', 'Z2', 'S2'],
        ['N1', 'T3', 'N3.2', 'T1.3', 'T1.2'],
        ['Z9']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
