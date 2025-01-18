import requests
from pathlib import Path
from loguru import logger

from langchain_core.documents import Document 
from langchain_community.document_loaders import PyPDFLoader

from src.cleaning import clean_book
from src.paths import set_paths, make_data_directories


class Book:
    def __init__(self, url: str, title: str, file_name: str) -> None:
        self.url: str = url 
        self.title: str = title

        self.file_name: str = file_name
        self.file_path: Path =  self.__get_file_path__() / f"{file_name}.pdf"
    
    def download(self) -> None:
        
        logger.warning(f'Checking for the presence of "{self.title}"...')
        
        if Path(self.file_path).exists():
            logger.success(f'"{self.title}" is already saved to disk')
        else:
            logger.warning(f'Unable to find "{self.title}" on disk -> Downloading it now...')

            try:
                response = requests.get(url=self.url)

                if response.status_code == 200:
                    with open(self.file_path, mode="wb") as file:
                        _ = file.write(response.content)

                    logger.success(f'Downloaded "{self.title}"')
               
            except Exception as error:
                logger.error(error)
                logger.error(f"Unable to download {self.title}.")
        
    @staticmethod
    def __get_file_path__() -> Path:
        return set_paths()["raw_data"]
      

def read_and_clean_books(books: list[Book]) -> list[Document]:
    """
    Loads each book using Langchain's PDF loader, resulting in a list of instances of Langchain's Document
    class. The function then removes pages that aren't core to the text. It also removes the new line 
    markers that are littered throughout the contents of each page.

    Args:
        books: a list of Books to be read and processed.

    Returns:
        list[Document]: list of Document objects containing the cleaned contents of each page from each book.
    """
    loader_list: list[Document] = []

    for book in books:
        book.download()
        loader = PyPDFLoader(file_path=str(book.file_path))
        documents: list[Document] = loader.load()

        cleaned_documents: list[Document] = clean_book(documents=documents, book_file_name=book.file_name)
        loader_list.extend(cleaned_documents)

    return loader_list 


neo_colonialism = Book(
    file_name="neo_colonialism", 
    title="Neo-Colonialism, the Last Stage of imperialism",
    url="https://www.marxists.org/ebooks/nkrumah/nkrumah-neocolonialism.pdf"
)

dark_days = Book(
    title="Dark Days in Ghana",
    file_name="dark_days",
    url="https://www.marxists.org/subject/africa/nkrumah/1968/dark-days.pdf"
)

africa_unite = Book(
    title="Africa Must Unite",
    file_name="africa_must_unite",
    url="https://www.marxists.org/subject/africa/nkrumah/1963/africa-must-unite.pdf"
)


if __name__ == "__main__":
    make_data_directories()
    for book in [neo_colonialism, dark_days, africa_unite]:
        book.download()

