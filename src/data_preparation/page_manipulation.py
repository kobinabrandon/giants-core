import os
import copy
from tqdm import tqdm
from pypdf import PdfReader, PdfWriter
from src.data_preparation.sourcing import Book


def make_single_page_layouts(books: list[Book], right_shift: int = 50) -> None:

    for book in books:
        with open(book.file_path, "rb") as opened_book:

            reader = PdfReader(book.file_path)
            writer = PdfWriter()

            for page in tqdm(
                iterable=reader.pages,
                desc=f'Rendering "{book.title}" in single page form'
            ):
                new_page = copy.copy(page)
                for split in ["left", "right"]:

                    if split == "left":
                        new_page.mediabox.upper_left = (page.mediabox.left, page.mediabox.top) 
                        new_page.mediabox.upper_right = ((page.mediabox.right / 2) + right_shift, page.mediabox.top) 
                    else:
                        new_page.mediabox.upper_left = (page.mediabox.right / right_shift, page.mediabox.top) 
                        new_page.mediabox.upper_right = (page.mediabox.right, page.mediabox.top) 
                    
                    # new_page.mediabox.lower_right = (page.mediabox.right, page.mediabox.bottom) 
                    # new_page.mediabox.lower_left = (page.mediabox.left, page.mediabox.bottom) 
                    
                    writer.add_page(new_page)

        with open(book.file_path, "wb") as new_book:
            os.remove(book.file_path)
            writer.write(book.file_path)


