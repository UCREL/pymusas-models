import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['24', 'horas', 'por', 'dia', '.', '5']
TEST_POS = ['NUM', 'NOUN', 'ADP', 'NOUN', 'PUNCT', 'NUM']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    portuguese_model = spacy.load("pt_single_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = portuguese_model(doc)
    expected_output = [
        ['N1'],
        ['T1'],
        ['A5.1+', 'S8+', 'M6', 'Z5'],
        ['T1.3'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    portuguese_model = spacy.load("pt_dual_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = portuguese_model(doc)
    expected_output = [
        ['T2+++'],
        ['T2+++'],
        ['T2+++'],
        ['T2+++'],
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
