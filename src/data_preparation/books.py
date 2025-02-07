import requests
from pathlib import Path
from loguru import logger

from src.setup.paths import set_paths, make_data_directories


class Book:
    """

    Attributes: 
        url: 
        title: 
        core_pages: a range of integers representing the page numbers of all the core pages of the book. 
        file_name: 
        file_path: 
    """
    def __init__(self, url: str, title: str, file_name: str, core_pages: range) -> None:
        self.url: str = url 
        self.title: str = title
        self.core_pages: range = core_pages
        
        self.file_name: str = file_name
        self.file_path: Path =  self.__get_file_path__() / f"{file_name}.pdf"
    
    def download(self) -> None:
        
        logger.warning(f'Checking for the presence of "{self.title}"')
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
      



def get_books() -> list[Book]: 

    neo_colonialism = Book(
        file_name="neo_colonialism", 
        title="Neo-Colonialism, the Last Stage of imperialism",
        url="https://www.marxists.org/ebooks/nkrumah/nkrumah-neocolonialism.pdf",
        core_pages=range(4, 202)
    )

    dark_days = Book(
        title="Dark Days in Ghana",
        file_name="dark_days",
        url="https://www.marxists.org/subject/africa/nkrumah/1968/dark-days.pdf",
        core_pages=range(7, 163)
    )

    africa_unite = Book(
        title="Africa Must Unite",
        file_name="africa_must_unite",
        url="https://www.marxists.org/subject/africa/nkrumah/1963/africa-must-unite.pdf",
        core_pages=range(5, 237)
    )

    class_struggle = Book(
        title="Class Struggle In Africa",
        file_name="class_struggle_in_africa",
        url="https://ia601208.us.archive.org/22/items/class-struggle-in-africa/Class%20Struggle%20in%20Africa_text.pdf",
        core_pages=range(4, 69)
    )

    handbook = Book(
        title="Handbook of Revolutionary Warefare: A Guide to the Armed Phase of the African Revolution",
        file_name="handbook_of_revolutionary_warfare",
        url="http://www.itsuandi.org/itsui/downloads/Itsui_Materials/handbook-of-revolutionary-warfare-a-guide-to-the-armed-phase-of-the-african-revolution.pdf",
        core_pages=range(2, 71)
    )

    make_data_directories()
    books: list[Book] = [neo_colonialism, dark_days, africa_unite, class_struggle, handbook] 

    for book in books:
        book.download()

    return books 

