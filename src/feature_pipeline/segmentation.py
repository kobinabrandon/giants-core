"""
Provides code that uses spacy to perform sentence segmentation.
"""


from spacy.lang.en import English
from spacy.tokens import Doc, Span


def segment_with_spacy(text: list[str], doc_file: Doc) -> list[Span]:
    sentences = [sentence.text for sentence in doc_file.sents]
    return sentences  

def add_spacy_pipeline_component(text: list[str], component_name: str) -> Doc:

    nlp = English()
    nlp.add_pipe(factory_name=component_name)
    doc_file = nlp(text=text)
    return doc_file


def get_tokens_with_spacy(text: list[str], doc_file: Doc) -> list[str]:
    return [token.text for token in doc_file if not token.is_space]
