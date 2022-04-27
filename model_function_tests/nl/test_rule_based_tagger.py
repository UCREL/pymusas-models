import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Een', 'bank', 'of', 'een', 'kredietinstelling', 'is', 'een', 'financieel', 'instituut', '.']
TEST_POS = ['DET', 'NOUN', 'CCONJ', 'DET', 'NOUN', 'AUX', 'DET', 'ADJ', 'NOUN', 'PUNCT']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    dutch_model = spacy.load("nl_single_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = dutch_model(doc)
    expected_output = [
        ['Z5'],
        ['Z99'],
        ['Z5'],
        ['Z5'],
        ['Z99'],
        ['Z99'],
        ['Z5'],
        ['I1'],
        ['P1/S5+c', 'X2.4/S5+c', 'S5+c', 'T2+'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
