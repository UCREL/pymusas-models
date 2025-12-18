import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['Pankki', 'on', 'instituutio', ',', 'joka', 'tarjoaa', 'finanssipalveluita', ',', 'erityisesti', 'maksuliikenteen', 'hoitoa', 'ja', 'luotonantoa', '.']
TEST_POS = ['NOUN', 'AUX', 'NOUN', 'PUNCT', 'PRON', 'VERB', 'NOUN', 'PUNCT', 'ADV', 'NOUN', 'NOUN', 'CCONJ', 'NOUN', 'PUNCT']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    finnish_model = spacy.load("fi_single_upos2usas_contextual_none")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = finnish_model(doc)
    expected_output = [
        ['I1/H1', 'K5.2/I1.1'],
        ['Z99'],
        ['S5+'],
        ['PUNCT'],
        ['Z8', 'N5.1+'],
        ['Z99'],
        ['Z99'],
        ['PUNCT'],
        ['A14'],
        ['Z99'],
        ['Z99'],
        ['Z5'],
        ['Z99'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
        assert [(token_index, token_index + 1)] == token._.pymusas_mwe_indexes
