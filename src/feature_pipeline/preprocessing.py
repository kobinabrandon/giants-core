from argparse import ArgumentParser, BooleanOptionalAction

from src.feature_pipeline.data_extraction import neo_colonialism, africa_unite, dark_days, Book
from src.feature_pipeline.reading import read_pdf, scan_pages_for_details
from src.feature_pipeline.chunking import perform_sentence_chunking
from src.setup.paths import make_data_directories, PAGE_DETAILS_WITH_SPACY, PAGE_DETAILS_WITHOUT_SPACY 


def process_book(book: Book, use_spacy: bool, describe: bool):

    save_path = PAGE_DETAILS_WITH_SPACY if use_spacy else PAGE_DETAILS_WITHOUT_SPACY

    document = read_pdf(book=book)

    details_of_all_pages = scan_pages_for_details(
        book=book,
        document=document, 
        save_path=save_path,
        use_spacy=use_spacy, 
        describe=describe
    )

    _ = perform_sentence_chunking(
        book=book, 
        details_of_all_pages=details_of_all_pages,
        examine_chunk_details=True
    )


if __name__ == "__main__":
    make_data_directories()

    parser = ArgumentParser()
    _ = parser.add_argument("--use_spacy", action=BooleanOptionalAction)
    _ = parser.add_argument("--describe", action=BooleanOptionalAction)

    args = parser.parse_args()
    for book in [neo_colonialism, africa_unite, dark_days]:
        process_book(book=book, use_spacy=args.use_spacy, describe=args.describe)
