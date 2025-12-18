import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['måneder', 'ad', 'gangen', 'indrømmer', '.', '5']
TEST_POS = ['NOUN', 'ADP', 'NOUN', 'ADJ', 'PUNCT', 'NUM']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    danish_model = spacy.load("da_single_none_contextual_none")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = danish_model(doc)
    expected_output = [
        ['T1.3'],
        ['Z99'],
        ['H2'],
        ['Q2.2', 'B3', 'A1.8+', 'S7.4+/M1'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    danish_model = spacy.load("da_dual_none_contextual_none")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = danish_model(doc)
    expected_output = [
        ['T1.3'],
        ['T1.3'],
        ['T1.3'],
        ['Q2.2', 'B3', 'A1.8+', 'S7.4+/M1'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        if token_index in [0, 1, 2]:
            assert [(0, 3)] == token._.pymusas_mwe_indexes
        else:
            assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
