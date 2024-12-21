import requests
from pathlib import Path
from loguru import logger

from dropbox import Dropbox
from dropbox.files import WriteMode

from general.config import general_config
from general.paths import set_paths, make_data_directories


class Book:
    def __init__(self, url: str, title: str, file_name: str) -> None:
        self.url: str = url 
        self.title: str = title
        self.file_name: str = file_name

        self.file_path: Path =  self.__get_file_path__() / f"{file_name}.pdf"
        self.non_core_pages: tuple[int, int] = self.__find_non_core_pages__()
        self.dropbox_connector = DropboxTransfers(book=self)
    
    def __get_file_path__(self):
        return set_paths(from_scratch=False, general=True)["raw_data"]

    def download(self):
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
                self.dropbox_connector.download()
        
        self.dropbox_connector.upload()

    def __find_non_core_pages__(self) -> tuple[int, int]: 
        
        book_and_non_core_pages = {
            "neo_colonialism": (4, 201),
            "africa_must_unite": (5, 236),
            "dark_days": (7, 162)
        }
        
        assert self.file_name in book_and_non_core_pages.keys()
        return book_and_non_core_pages[self.file_name]


class DropboxTransfers:
    def __init__(self, book: Book) -> None:
        self.book = book
        self.connector = Dropbox(general_config.dropbox_access_token)
        self.remote_file_path = f"/{book.file_name}.pdf"

    def upload(self) -> bool | None:
        try:
            logger.info(f'Checking whether {self.book.title} has already been uploaded')
            metadata = self.connector.files_get_metadata(path=self.remote_file_path)
            breakpoint()
            if self.remote_file_path in metadata.values():
                return True

        except Exception as error:
            logger.error(error)
            logger.info(f'File not found. Attempting to upload "{self.book.title}" to Dropbox')

            with open(self.book.file_path, "rb") as file:
                self.connector.files_upload(
                    f=file.read(), 
                    path=self.remote_file_path
                )

            logger.success(f"{self.book.title} uploaded")

    def download(self):
        metadata, response = self.connector.files_download(self.remote_file_path)

        breakpoint()

        with open(self.book.file_path, "wb") as file:
            file.write(response.content)

    
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

