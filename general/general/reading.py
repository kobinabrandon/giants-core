import pymupdf

from tqdm import tqdm
from loguru import logger
from pathlib import Path

from general.books import Book 
from general.paths import make_data_directories, set_paths


def read_pdf(book: Book) -> pymupdf.Document:
    logger.info(f"Reading '{book.title}'")
    return pymupdf.open(filename=book.file_path)


def get_raw_text(document: pymupdf.Document) -> str:
    return document.get_text()


def remove_new_line_marker(text: str) -> str:
    return text.replace("\n", " ").strip()


def merge_books(books: list[Book], from_scratch: bool, general: bool) -> str:

    make_data_directories(from_scratch=from_scratch, general=general)  # Just to ensure that the directories are present.
    paths = set_paths(from_scratch=from_scratch, general=general) 

    CLEANED_TEXT_DIR = paths["cleaned_text"] 
    file_path: Path = CLEANED_TEXT_DIR / "merged_books.txt"

    if Path(file_path).is_file():
       logger.success("The merged text file containing the text in all the books is already present")
       with open(file_path, mode="r") as text_file:
           return text_file.read()
    else:
       logger.warning("There is no merged text file -> Generating it")
       book_contents: list[str] = []

       for book in books:
           logger.warning(f"Checking for the presence of {book.title}...")
           book.download()
            
           intro_page, end_page = book.non_core_pages  
           document = read_pdf(book=book)    
       
           for page_number, page in tqdm(iterable=enumerate(document), desc=f"Extracting the raw text of {book.title}"):
               
               if page_number in range(intro_page, end_page+1):
                   raw_text: str = page.get_text()
                   cleaned_text: str = remove_new_line_marker(text=raw_text)
                   book_contents.append(cleaned_text) 

       logger.warning("Merging the books into a single string")
       merged_text = " ".join(book_contents)

       with open(file_path, mode="w") as text_file:
           _  = text_file.write(merged_text)
       
       return merged_text




