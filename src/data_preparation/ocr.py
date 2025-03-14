import os
from io import BytesIO
from pathlib import Path

import pdf2image
from tqdm import tqdm
from loguru import logger
from PIL.Image import Image
from pypdf import PdfWriter
from pytesseract import pytesseract 

from src.authors import prepare_sources
from src.data_preparation.sourcing import Author, ViaHTTP
from src.setup.paths import OCR_IMAGES, PDFS_AFTER_OCR, TXT_AFTER_OCR, make_fundamental_paths 


class OCRModule:
    def __init__(self, author: Author, keep_images: bool, image_format: str = "JPEG", output_format: str = "pdf") -> None:
        self.author: Author = author 
        self.keep_images: bool = keep_images
        self.image_format: str = image_format
        self.output_format: str = output_format
        self.path_to_ocr_images: Path = OCR_IMAGES.joinpath(author.name) 
        self.path_to_text_after_ocr: Path = PDFS_AFTER_OCR.joinpath(author.name) if output_format == "pdf" else TXT_AFTER_OCR.joinpath(author.name)

        self.__setup__()
        assert self.output_format in ["txt", "pdf"], "Texts that have undergone OCR can only be output as .text and PDF files" 

    def __setup__(self):
        make_fundamental_paths()
        self.create_ocr_paths_for_author()

    def create_ocr_paths_for_author(self):
        for path in [self.path_to_ocr_images, self.path_to_text_after_ocr]:
            if not Path(path).exists():
                os.mkdir(path)

    def get_path_to_images_from_book(self, book: ViaHTTP) -> Path :
        path_to_ocr_images_of_book: Path = self.path_to_ocr_images.joinpath(book.file_name)
        if not path_to_ocr_images_of_book.exists():
            os.mkdir(path_to_ocr_images_of_book)

        return path_to_ocr_images_of_book 

    def extract_text_from_images(self) -> list[Image] | None:
        if self.author.books_via_http != None:  # At the moment, the only books that are confirmed to need OCR are among those I got through HTTP 
            for book in self.author.books_via_http:

                if book.needs_ocr:
                    logger.warning(f'"{book.title}" by {self.author.name} requires OCR')
                    path_to_ocr_images_of_book: Path = self.get_path_to_images_from_book(book=book) 
                    book_file_path: Path = self.author.path_to_raw_data.joinpath(f"{book.file_name}" + ".pdf")

                    if not path_to_ocr_images_of_book.exists():
                        os.mkdir(path_to_ocr_images_of_book)

                    logger.info("Taking an image of each page")
                    images_from_books: list[Image] = pdf2image.convert_from_path(pdf_path=book_file_path)

                    merger = PdfWriter()
                    full_text = ""

                    for i, image in tqdm(
                        iterable=enumerate(images_from_books),
                        desc="Extracting text from each page..."
                    ):
                        page_image_path: Path = path_to_ocr_images_of_book.joinpath(f"Page {i+1}.jpg")
                        if not page_image_path.exists():
                            if (book.start_page != None) and (book.end_page != None):
                                if (i < book.start_page) or (i > book.end_page):
                                   continue 

                            if self.keep_images:
                                image.save(page_image_path, format=self.image_format)

                            if self.output_format == "pdf":
                                pdf_after_ocr: bytes|str = pytesseract.image_to_pdf_or_hocr(image=image, lang="eng", extension="pdf") 
                                if isinstance(pdf_after_ocr, bytes):
                                    merger.append(BytesIO(pdf_after_ocr)) 
                                else:
                                    raise Exception(f'After OCR, the PDF of "{book.title}" is coming out as a string instead of a bytes object')
                            else: 
                                raw_text_in_image: bytes|str|dict[str, bytes|str] = pytesseract.image_to_string(image=image, lang="eng") 
                                if isinstance(raw_text_in_image, str):
                                    full_text += f"/n/n {raw_text_in_image}"
                                else:
                                    raise Exception(f'After OCR, the string content of of "{book.title}" is coming out as a bytes object or a dictionary')

                    file_extension = ".pdf" if self.output_format == "pdf" else "txt"
                    path_to_write_into: Path = self.path_to_text_after_ocr.joinpath(book.file_name + file_extension)

                    if self.output_format == "pdf":
                        with open(path_to_write_into, mode="wb") as file:
                                _ = merger.write(file)
                    else:
                        with open(path_to_write_into, mode="w") as txt_file:
                            _ = txt_file.write(full_text)

                    logger.success("Saved the processed book as a new PDF")


if __name__ == "__main__":
    for author in prepare_sources():
        module = OCRModule(author=author, keep_images=True)
        _ = module.extract_text_from_images() 

