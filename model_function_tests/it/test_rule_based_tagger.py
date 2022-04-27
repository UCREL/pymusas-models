import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['a', 'breve', 'durata', '.', '5']
TEST_POS = ['ADP', 'ADJ', 'NOUN', 'PUNCT', 'NUM']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    italian_model = spacy.load("it_single_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = italian_model(doc)
    expected_output = [
        ['Z5'],
        ['N5-', 'T1.3-', 'N3.7-', 'N3.3-', 'S1.2.4-', 'N3.8+@', 'F1%', 'N3.7-%'],
        ['T1.3'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    italian_model = spacy.load("it_dual_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = italian_model(doc)
    expected_output = [
        ['T1.3-'],
        ['T1.3-'],
        ['T1.3-'],
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
