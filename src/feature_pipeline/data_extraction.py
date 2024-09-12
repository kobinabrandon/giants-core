"""
Contains code that downloads selected books by His Excellency Osagyefo Dr Kwame Nkrumah
"""
import os 
import requests 
from loguru import logger 
from tqdm.auto import tqdm 

from src.setup.paths import RAW_DATA_DIR, make_fundamental_paths


class Book:
    def __init__(self, title: str, file_name: str, url: str) -> None:
        self.url = url
        self.title = title
        self.file_name = file_name  
        self.file_path = RAW_DATA_DIR/f"{file_name}.pdf"

    def download(self) -> None:
        """
        Download the text in question if it isn't already present

        Args:
            title (str): _description_
        """
        if not os.path.exists(path=self.file_path):
            logger.warning(f"You don't have {self.title}. Downloading it now...")
            response = requests.get(url=self.url)

            if response.status_code == 200:
                with open(self.file_path, mode="wb") as file:
                    file.write(response.content)
                logger.success(f"Downloaded {self.title}")
            else:
                logger.error(f"Couldn't download {self.title}. Status code: {response.status_code}")
        else:
            logger.success(f"You already have {self.title}!")


neo_colonialism = Book(
    file_name="neo_colonialism", 
    title="Neo-Colonialism, the Last Stage of imperialism",
    url="https://www.marxists.org/ebooks/nkrumah/nkrumah-neocolonialism.pdf"
)

dark_days = Book(
    title="Dark Days in Ghana",
    file_name="dark_days_in_ghana",
    url="https://www.marxists.org/subject/africa/nkrumah/1968/dark-days.pdf"
)

africa_unite = Book(
    title="Africa Must Unite",
    file_name="africa_must_unite",
    url="https://ccaf.africa/books/Africa-Must-Unite-Kwame-Nkrumah.pdf"
)


if __name__ == "__main__":

    make_fundamental_paths()

    for book in [neo_colonialism, dark_days, africa_unite]:
        book.download()
