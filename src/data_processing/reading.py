import os
import mobi
import ebooklib
from pathlib import Path
from ebooklib import epub
from bs4 import BeautifulSoup

from src.authors import prepare_sources
from src.data_preparation.sourcing import Author


class Parser:
    def __init__(self, author: Author, extension: str) -> None:
        self.author: Author = author
        self.extension: str = extension 
        assert self.extension in [".epub", ".mobi"]

    def get_files(self) -> list[Path]:
        return [
            self.author.path_to_raw_data.joinpath(file) 
            for file in os.listdir(self.author.path_to_raw_data) if file.endswith(self.extension)
        ]

    def has_files(self) -> bool:
        files: list[Path] = self.get_files() 
        return False if len(files) == 0 else True 

    def parse(self, path: str) -> str:

        if self.extension == ".mobi":
            _ , metadata = mobi.extract(infile=path) 
            with open(metadata, mode="r", encoding="utf-8") as file:
                return file.read()

        else: 
            raw_text = ""
            book: epub.EpubBook = epub.read_epub(name=path)
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    raw_text += soup.get_text() + "\n"

            return raw_text


# if __name__ == "__main__":
#     for author in prepare_sources():
#         parser = Parser(author=author, extension=".epub")
#         if parser.has_files():
#             file = parser.get_files()[0]
#             breakpoint()
#             text = parser.parse(path=str(file))
#             print(text)
        # file_path: Path = destination_path.joinpath(f"{self.file_name}")
