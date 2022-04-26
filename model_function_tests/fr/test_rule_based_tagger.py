import spacy
from spacy.tokens import Doc
from spacy.vocab import Vocab


def test_this() -> None:
    french_model = spacy.load("fr_single_UPOS_contextual")
    doc = Doc(Vocab(), words=["hello"], spaces=[True])
    tokens = french_model(doc)
    assert tokens[0]._.pymusas_tags == ['Z99']
