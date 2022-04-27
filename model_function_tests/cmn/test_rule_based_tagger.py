import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


TEST_TOKENS = ['銀行', '是', '吸收', '公众', '存款', '。']
TEST_POS = ['NOUN', 'VERB', 'VERB', 'NOUN', 'NOUN', 'PUNCT']
TEST_SPACES = [True] * len(TEST_TOKENS)


def test_single_UPOS_contextual() -> None:
    chinese_model = spacy.load("cmn_single_upos2usas_contextual")
    doc = Doc(Vocab(), words=TEST_TOKENS, spaces=TEST_SPACES, pos=TEST_POS)
    output = chinese_model(doc)
    expected_output = [
        ['Z99'],
        ['A3', 'Z5'],
        ['A1.1.1', 'T1.3+', 'X2.3+', 'X5.2+', 'C1', 'M2', 'A9+', 'X5.1+', 'I1.2', 'O4.2+', 'X2.1', 'K5.1', 'I3.1/A9+', 'S5+', 'N5', 'O4.1', 'A2.1/O1.2', 'A6.1+/A2.1'],
        ['A10+', 'G3/S7.1+/S2mf', 'B3/H1', 'N5+', 'A4.2-', 'S5+', 'S5+c'],
        ['I1.1', 'O1.1', 'S7.1-/A2.1'],
        ['PUNCT']
    ]

    assert len(expected_output) == len(output)
    for token_index, token in enumerate(output):
        assert expected_output[token_index] == token._.pymusas_tags
