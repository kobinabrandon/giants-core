import pymupdf

from tqdm import tqdm
from loguru import logger
from pathlib import Path

from general.books import Book 
from general.paths import make_data_directories, set_paths


def read_pdf(book: Book) -> pymupdf.Document:
    logger.info(f"Reading '{book.title}'")
    return pymupdf.open(filename=book.file_path)


def remove_new_line_marker(text: str) -> str:
    return text.replace("\n", " ").strip()


def merge_books(books: list[Book], from_scratch: bool, general: bool) -> str:

    make_data_directories(from_scratch=from_scratch, general=general)  # Just to ensure that the directories are present.
    paths = set_paths(from_scratch=from_scratch, general=general) 
    
    CLEANED_TEXT_DIR = paths["cleaned_text"] 

    if len(books) == 1:
        raw_text_file_name = f"raw_text_{[book.file_name for book in books][0]}.txt"
    else:
        raw_text_file_name = "merged_books.txt"

    file_path: Path = CLEANED_TEXT_DIR / raw_text_file_name

    if Path(file_path).is_file():
       logger.success("The file containing the raw text is already present")
       with open(file_path, mode="r") as text_file:
           return text_file.read()
    else:
       logger.warning("There is no file that contains the raw text -> Generating it")
       book_contents: list[str] = []

       for book in books:
           logger.warning(f"Checking for the presence of {book.title}...")
           book.download(upload=False)
          
           intro_page, end_page = book.non_core_pages  
           document = read_pdf(book=book)    
       
           for page_number, page in tqdm(iterable=enumerate(document), desc=f"Extracting the raw text of {book.title}"):
               
               if page_number in range(intro_page, end_page+1):
                   raw_text: str = page.get_text()
                   cleaned_text: str = remove_new_line_marker(text=raw_text)
                   book_contents.append(cleaned_text) 
       
       if len(books) > 1:
           logger.warning("Merging the books into a single string")
        
       else:
           logger.warning(f'Saving the raw text of {[book.title for book in books][0]}')

       merged_text = " ".join(book_contents)
       with open(file_path, mode="w") as text_file:
           _  = text_file.write(merged_text)
       
       return merged_text

