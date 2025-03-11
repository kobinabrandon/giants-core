import os
from pathlib import Path

from tqdm import tqdm
from loguru import logger 
from PIL.Image import Image
from pdf2image import convert_from_path

from src.setup.paths import OCR_IMAGES 
from src.authors import prepare_sources
from src.data_preparation.sourcing import get_destination_path


def extract_images_for_ocr(format: str = "JPEG") -> None:
    
    for author in tqdm(
        iterable=prepare_sources(),
        desc="Getting the scanned pages of the texts that require OCR"
    ):
        if author.books_via_http != None: 
            author_path: Path = get_destination_path(author_name=author.name)
            author_ocr_path: Path = OCR_IMAGES.joinpath(author.name) 

            if not author_ocr_path.exists():
                os.mkdir(author_ocr_path)

            for book in author.books_via_http:
                if book.needs_ocr:
                    book_ocr_path: Path = author_ocr_path.joinpath(book.file_name)
                    book_file_path: Path = author_path.joinpath(f"{book.file_name}" + ".pdf")

                    if not book_ocr_path.exists():
                        os.mkdir(book_ocr_path)

                    book_images: list[Image] = convert_from_path(pdf_path=book_file_path)

                    for i, image in enumerate(book_images):
                        image_path: Path = book_ocr_path.joinpath(f"Page {i+1}.jpg")

                        if not image_path.exists():
                            if (book.start_page != None) and (book.end_page != None):
                                if (i >= book.start_page) or (i <= book.end_page):
                                    image.save(image_path, format=format)
                            else:
                                image.save(image_path, format=format)



