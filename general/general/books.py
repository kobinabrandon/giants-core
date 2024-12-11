import requests
from pathlib import Path
from loguru import logger 

from general.paths import set_paths, make_data_directories


class Book:
    def __init__(self, url: str, title: str, file_name: str) -> None:
        self.url: str = url 
        self.title: str = title
        self.file_name: str = file_name
        self.file_path: Path =  self.__get_file_path__()/ f"{file_name}.pdf"
        self.non_core_pages: tuple[int, int] = self.__find_non_core_pages__()

    def __get_file_path__(self):
        return set_paths(from_scratch=False, general=True)["raw_data"]

    def download(self):
        if Path(self.file_path).exists():
            logger.success(f"'{self.title} is already saved to disk'")
        else:
            logger.warning(f'You do not have "{self.title}" -> Downloading it now...')
            response = requests.get(url=self.url)

            if response.status_code == 200:
                with open(self.file_path, mode="wb") as file:
                    _ = file.write(response.content)
                logger.success(f"Downloaded {self.title}")
            else:
                logger.error(f"Couldn't download {self.title}. Status code: {response.status_code}")

    def __find_non_core_pages__(self) -> tuple[int, int]: 
        
        book_and_non_core_pages = {
            "neo_colonialism": (4, 201),
            "africa_must_unite": (5, 236),
            "dark_days": (7, 162)
        }
        
        assert self.file_name in book_and_non_core_pages.keys()
        return book_and_non_core_pages[self.file_name]

    
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
    url="https://ccaf.africa/books/Africa-Must-Unite-Kwame-Nkrumah.pdf"
)


if __name__ == "__main__":
    make_data_directories(from_scratch=False, general=True)
    for book in [neo_colonialism, dark_days, africa_unite]:
        book.download()

