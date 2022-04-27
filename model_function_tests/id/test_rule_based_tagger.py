import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Bank', 'adalah', 'sebuah', 'lembaga', 'intermediasi', 'yang', '.']
TEST_TAGS = ['NNP', 'VB', 'NND', 'NN', 'NN', 'SC', 'Z']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    indonesian_model = spacy.load("id_single_none_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, tags=TEST_TAGS)
    output = indonesian_model(doc)
    expected_output = [
        ['Z99'],
        ['Z99'],
        ['Z99'],
        ['Z99'],
        ['Z99'],
        ['Z5'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
