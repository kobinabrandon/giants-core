import requests
from pathlib import Path

from loguru import logger
from dropbox import Dropbox

from general.config import general_config
from general.paths import set_paths, make_data_directories


class Book:
    def __init__(self, url: str, title: str, file_name: str) -> None:
        self.url: str = url 
        self.title: str = title
        self.file_name: str = file_name

        self.file_path: Path =  self.__get_file_path__() / f"{file_name}.pdf"
        self.non_core_pages: tuple[int, int] = self.__find_non_core_pages__()
    
    def __get_file_path__(self) -> Path:
        return set_paths(from_scratch=False, general=True)["raw_data"]

    def download(self) -> None:
        
        box = DropboxAPI(book=self)
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
                logger.error(f"Unable to download {self.title} from the original source.")
                logger.warning(f'Attempting to download "{self.title}" from Dropbox')
                box.download_from_dropbox() 

        if box.book_on_dropbox():
            box.upload_to_dropbox()

    def __find_non_core_pages__(self) -> tuple[int, int]: 
        
        book_and_non_core_pages = {
            "neo_colonialism": (4, 201),
            "africa_must_unite": (5, 236),
            "dark_days": (7, 162)
        }
        
        assert self.file_name in book_and_non_core_pages.keys()
        return book_and_non_core_pages[self.file_name]


class DropboxAPI:
    def __init__(self, book: Book) -> None:
        self.book: Book = book
        self.remote_file_path: str = f"/{book.file_name}.pdf"
        self.api: Dropbox = Dropbox(general_config.dropbox_access_token)

    def book_on_dropbox(self) -> bool:

        logger.info(f'Checking whether {self.book.title} has already been uploaded')
        metadata = self.api.files_get_metadata(path=self.remote_file_path) 

        if self.remote_file_path in metadata.values():
            logger.warning(f'"{self.book.title}" is already on Dropbox')
            return True
        else:
            logger.warning(f"{self.book.title} is not on Dropbox")
            return False 

    def upload_to_dropbox(self) -> None:

        logger.info(f'Attempting to upload "{self.book.title}" to Dropbox')

        with open(self.book.file_path, "rb") as file:
           self.api.files_upload(f=file.read(), path=self.remote_file_path)

        logger.success(f"'{self.book.title}' successfully uploaded to Dropbox")


    def download_from_dropbox(self) -> None:
        metadata, response = self.api.files_download(f"/{self.book.file_name}.pdf")

        with open(self.book.file_path, "wb") as file:
            file.write(response.content)

        logger.success(f"'{self.book.title}' successfully downloaded from Dropbox")


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
    make_data_directories(from_scratch=False, general=True)
    for book in [neo_colonialism, dark_days, africa_unite]:
        book.download()

