"""
Provides code that uses spacy to perform sentence segmentation.
"""
from spacy.tokens import Doc
from spacy.lang.en import English

from src.setup.config import config

    
def segment_with_spacy(doc_file: Doc) -> list[str]:
    sentences = [sentence.text for sentence in doc_file.sents]
    return sentences  


def add_spacy_pipeline_component(text: str, component_name: str = "sentencizer") -> Doc:

    nlp = English()
    nlp.max_length = config.spacy_max_length
    _ = nlp.add_pipe(factory_name=component_name)
    doc_file = nlp(text=text)
    return doc_file


def get_tokens_with_spacy(doc_file: Doc) -> list[str]:
    return [token.text for token in doc_file if not token.is_space]

