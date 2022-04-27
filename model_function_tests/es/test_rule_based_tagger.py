import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['dormirse', 'en', 'los', 'laureles', '.', '5']
TEST_POS = ['X', 'ADP', 'DET', 'NOUN', 'PUNCT', 'NUM']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    spanish_model = spacy.load("es_single_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = spanish_model(doc)
    expected_output = [
        ['Z99'],
        ['Z5', 'N3'],
        ['Z5'],
        ['Z99'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    spanish_model = spacy.load("es_dual_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = spanish_model(doc)
    expected_output = [
        ['X5', 'E2'],
        ['X5', 'E2'],
        ['X5', 'E2'],
        ['X5', 'E2'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        if token_index in [0, 1, 2, 3]:
            assert [(0, 4)] == token._.pymusas_mwe_indexes
        else:
            assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
