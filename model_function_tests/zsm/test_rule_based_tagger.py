import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Esok', 'pukul', '5', 'dah', 'baik', '.']
TEST_POS = ['NOUN', 'NOUN', 'NUM', 'PART', 'ADJ', 'PUNCT']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_none_contextual() -> None:
    malay_model = spacy.load("zsm_single_none_contextual_none")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = malay_model(doc)
    expected_output = [
        ['T1.1.3'],
        ['X9.2+/S7.3', 'X9.2+/G3', 'S7.1+', 'E3-', 'A1.1.1', 'A5.1++', 'B1'],
        ['N1'],
        ['Z99'],
        ['S7.1+/S2.2m'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
