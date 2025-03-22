"""
Contains code that cleans the raw text in the documents of a given book
"""
from pathlib import Path
from loguru import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from src.data_preparation.sourcing import Author
from src.data_processing.reading import TextParser 
from src.data_preparation.management import VersionManager, get_file_extension


class Cleaner:
    def __init__(self, author: Author):
        self.author: Author = author

    def get_file_name(self, file_path: Path) -> str:
        manager = VersionManager(author=self.author)
        matching_file_name: list[str] = [file_name for file_name in manager.file_names if file_name in str(file_path)]
        assert len(matching_file_name) == 1, f"There is more than one file called {matching_file_name} in {self.author.path_to_raw_data}"
        # This assert statement is temporary, and will be replaced by the code that eliminates duplicates (once it works the way I want) 
        return matching_file_name[0]

    def get_core_pages(self, file_name: str) -> range | None:
        if self.author.books_via_http:
            for book in self.author.books_via_http:
                if (file_name in book.file_name) and (book.start_page and book.end_page):
                    return range(book.start_page, book.end_page)
        else:
            logger.warning(f"{self.author.name} has no texts that contain have specified start and end pages")

    def execute(self) -> list[Document] | None:

        logger.info(f"Cleaning the texts by {self.author.name}")

        author_documents: list[Document] = []
        for file_path in self.author.file_paths:
            file_name: str = self.get_file_name(file_path=file_path)
            extension = get_file_extension(file_name=file_name)

            try:
                core_pages: bool | range | None = look_up_core_pages(author=self.author, file_name=file_name, target="values") 
            except Exception as error:
                raise(error)

            if extension == ".pdf": 
                assert isinstance(core_pages, range) or (core_pages == None)
                documents = self.clean_pdf(file_path=file_path, core_pages=core_pages)
                author_documents.extend(documents)

            elif (extension == ".epub") or (extension == ".mobi"): 
                documents = self.clean_epub_or_mobi(extension=extension)
                author_documents.extend(documents)

            elif (extension == ".txt"):
                with open(file_path, mode="r") as txt_file:
                    raw_text: str = txt_file.read()
                    
                documents = [Document(page_content=raw_text)] 
                documents = self.perform_cleaning(documents)
                author_documents.extend(documents)

            else:
                raise NotImplementedError(f"Cleaning halted at {file_path}. No cleaning process implemented for {extension} files")

        return author_documents

    def clean_pdf(self, file_path: Path, core_pages: range | None) -> list[Document]:

        loader = PyPDFLoader(file_path=file_path)
        pages: list[Document] = loader.load()

        if core_pages:
            pages: list[Document] = self.remove_non_core_pages(documents=pages, core_pages=core_pages) 

        return self.perform_cleaning(documents=pages)

    def clean_epub_or_mobi(self, extension: str) -> list[Document]:

        documents: list[Document] = []
        assert extension in [".epub", ".mobi"]
        parser = TextParser(author=self.author, extension=extension)
        
        if parser.has_files():
            file: list[Path] = parser.get_files()
            text: str = parser.parse(path=str(file))
            document = Document(page_content=text)
            documents.append(document)

        return self.perform_cleaning(documents=documents) 

    def perform_cleaning(self, documents: list[Document]) -> list[Document]: 

        documents_without_new_lines: list[Document] = self.remove_new_line_markers(documents=documents)
        
        for document in documents_without_new_lines:
            document.page_content = self.fix_known_spelling_issues(text=document.page_content)

        return documents_without_new_lines 

    @staticmethod
    def remove_non_core_pages(documents: list[Document], core_pages: range) -> list[Document]:
        """
        Scan all the Document objects in a given book, and remove those that come from most pages that are not core
        to the book in question.

        Args:
            documents: list of Document objects representing the information of each page of a given book
            book: the book whose text we are cleaning

        Returns:
           list[Document]: list of Document objects that contain the information of the core pages of the book. 
        """
        for document in documents:
            metadata: dict[str, str | int] = document.metadata
            if metadata["page"] not in core_pages: 
                documents.remove(document)

        return documents 

    def fix_known_spelling_issues(self, text: str) -> str:
        """
        Replace a target string with a preferred one.

        Args:
            text: the text to be searched for the target string

        Returns:
           str: the string following all the changes. 
        """
        if "kwame nkrumah" == self.author.name.lower(): # Because Nkrumah is currently the only person for whom I have identified such issues. 
            target_strings_and_replacements = {
                r"\xad": "", 
                "19 66": "1966",
                "I 966": "1966",
                "Cl.A": "C.I.A",
                r"\'coup\'": "coup",
                "fkunkeys": "flunkeys" 
            }

            for target_string in target_strings_and_replacements.keys():
                replacement = target_strings_and_replacements[target_string]
                text = text.replace(target_string, replacement)

        return text 


    @staticmethod
    def remove_new_line_markers(documents: list[Document]) -> list[Document]:
        """
        Look at the text contained in each Document object, remove the new line markers inside these texts, and 
        put those cleaner texts back into that Document object.
        
        Args:
            documents: Document objects whose text is to be cleaned up a bit. 

        Returns:
            list[Document]: the list of all the Document objects with cleaner text. 
        """
        for document in documents:
            raw_text = document.page_content
            document.page_content = raw_text.replace("\n", " ").strip()

        return documents


def look_up_core_pages(author: Author, file_name: str, target: str) -> bool | range | None:

    assert target in ["presence", "values"], f'The "target" argument is can only be "presence" or "values"'

    if author.books_via_http != None:
        for book in author.books_via_http:
            file_found: bool = (file_name in book.file_name)
            start_page_specified: bool = book.start_page != None  
            end_page_specified: bool = book.end_page != None  

            match (file_found, start_page_specified, end_page_specified):
                case (True, True, True):
                    return True if target == "presence" else range(book.start_page, book.end_page) 

                case (True, False, False):
                    logger.warning(f'"{file_name}" isn\'t equipped with any information on the core pages')
                    if target == "presence":
                        return False 
                    else:
                        logger.error(f"We don't have any specified start and end pages for {book.file_name}")
                        return None

                case (True, True, False) | (True, False, True):
                    raise Exception(f'"{file_name}" somehow has partial core page specifications.')
                case (False, True, True) | (False, False, False) | (False, False, True) | (False, True, False):
                    continue
    else:
        logger.warning(f'There are no books by "{author.name}" that provide any information on the core pages.')
        return False if target == "presence" else None

