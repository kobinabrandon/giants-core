import sentencepiece as sp

from config import config 
from segmentation import segment_into_sentences

from general.reading import read_pdf, merge_books
from general.books import neo_colonialism, africa_unite, dark_days


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
    all_sentences = segment_into_sentences(text=merged_text) 
    tokenizer_path = train_tokenizer(sentences=all_sentences)
    
