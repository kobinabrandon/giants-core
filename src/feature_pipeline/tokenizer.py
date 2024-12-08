from pathlib import Path
import sentencepiece as sp

from src.setup.config import config 
from src.feature_pipeline.reading import merge_books  
from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days
from src.feature_pipeline.segmentation import add_spacy_pipeline_component, segment_with_spacy 


def train_tokenizer(sentences: list[str]) -> str:
    
    model_name = "sp_model"

    sp.SentencePieceTrainer.Train(
       sentence_iterator = iter(sentences),
       model_prefix=model_name,
       pad_id=config.pad_id,
       unk_id=config.unk_id,
       bos_id=config.bos_id,
       eos_id=config.eos_id,
       vocab_size=config.vocab_size
    )
    
    return model_name


def view_tokens(text: str, model_name: str) -> list[str]:
    processor: sp.SentencePieceProcessor = sp.SentencePieceProcessor(f"{model_name}.model")
    return processor.Encode(text, out_type=str)


if __name__ == "__main__":
    merged_text = merge_books(books=[neo_colonialism, africa_unite, dark_days])
    doc_file_for_all_books = add_spacy_pipeline_component(text=merged_text)    
    all_sentences = segment_with_spacy(doc_file=doc_file_for_all_books) 
    tokenizer_path = train_tokenizer(sentences=all_sentences)
    
    vector = view_tokens(text=merged_text, model_path=tokenizer_path)
    breakpoint()
