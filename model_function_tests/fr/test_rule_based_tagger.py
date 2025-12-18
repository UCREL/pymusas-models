import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Une', 'banque', 'est', 'une', 'institution', 'financière', '.', '5']
TEST_POS = ['DET', 'NOUN', 'AUX', 'DET', 'NOUN', 'ADJ', 'PUNCT', 'NUM']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    french_model = spacy.load("fr_single_upos2usas_contextual_none")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = french_model(doc)
    expected_output = [
        ['Z5'],
        ['I1.1', 'X2.6+', 'M1', 'I1/H1', 'I1.1/I2.1c', 'W3/M4', 'A9+/H1', 'O2', 'M6'],
        ['M6'],
        ['Z5'],
        ['S5+c', 'S7.1+', 'H1c', 'S1.1.1', 'T2+'],
        ['Z99'],
        ['PUNCT'],
        ['N1']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
