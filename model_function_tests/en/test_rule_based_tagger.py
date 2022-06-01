import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Sporting', 'community', 'hack', 'had', '.']
TEST_POS = ['NOUN', 'NOUN', 'NOUN', 'DET', 'PUNCT']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    english_model = spacy.load("en_single_none_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = english_model(doc)
    expected_output = [
        ['A10+'],
        ['S5+c'],
        ['Q4.2/S2mf','Y2','K5.1'],
        ['A9+', 'Z5','A2.2','S4'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes


def test_dual_UPOS_contextual() -> None:
    english_model = spacy.load("en_dual_none_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = english_model(doc)
    expected_output = [
        ['Df/S5+c'],
        ['Df/S5+c'],
        ['Q4.2/S2mf','Y2','K5.1'],
        ['A9+', 'Z5','A2.2','S4'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        if token_index == 0 or token_index == 1:
            assert [(0, 2)] == token._.pymusas_mwe_indexes
        else:
            assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
