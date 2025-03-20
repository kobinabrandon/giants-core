import os
import json
import asyncio
import shutil
import requests
from glob import glob
from pathlib import Path

from tqdm import tqdm
from loguru import logger
from torrentp import TorrentDownloader

from src.data_preparation.scraper import scrape_page
from src.setup.paths import CHROMA_DIR, DATA_DIR, OCR_IMAGES, IMAGES_IN_DOWNLOADS, make_fundamental_paths


def find_raw_data_for_author(author_name: str) -> Path:
    from src.authors import prepare_sources
    return [author.path_to_raw_data for author in prepare_sources() if author_name == author.name][0]


class ViaScraper:
    def __init__(
        self, 
        title: str, 
        url: str, 
        is_interview: bool = False
    ) -> None:
        self.url: str = url
        self.title: str = title
        self.is_interview: bool = is_interview
        self.file_name: str = f"{self.title}.txt"

    def download(self, author_name: str) -> None:

        destination_path: Path = find_raw_data_for_author(author_name=author_name)
        file_path: Path = destination_path.joinpath(f"{self.file_name}")
            
        if not Path(file_path).exists():
            logger.warning(f'Attempting to scrape "{self.title}"')
            text: str = scrape_page(url=self.url)
            _ = Path(file_path).write_text(text)


class ViaHTTP:
    def __init__(
        self, 
        title: str, 
        url: str | None, 
        format: str = "pdf",
        needs_ocr: bool = False, 
        start_page: int | None = None, 
        end_page: int | None = None
    ) -> None:

        self.title: str = title
        self.format: str = format
        self.url: str | None = url 
        self.needs_ocr: bool = needs_ocr
        self.start_page: int | None = start_page
        self.end_page: int | None = end_page
        self.file_name: str = title.lower().replace(" ", "_") 
        make_fundamental_paths()
         
    def get_place_of_extension(self) -> int:
        return 5 if (".epub" in self.file_name or ".mobi" in self.file_name) else 4

    def get_file_extension(self) -> str:
        extension_place: int = self.get_place_of_extension()
        return self.file_name[-extension_place:] 

    def download(self, file_path: str) -> None:
        assert self.url != None
        if not Path(file_path).exists():
            logger.warning(f'Downloading "{self.title}"...')
            try:
                response = requests.get(url=self.url)
                if response.status_code == 200:
                    with open(file_path, mode="wb") as file:
                        _ = file.write(response.content)

                    logger.success(f'Downloaded "{self.title}"')
               
            except Exception as error:
                logger.error(f"Unable to download {self.title}. Error: {error}")
    

class ViaTorrent:
    def __init__(self, magnet: str) -> None:
        self.magnet: str = magnet 

    def download(self, file_path: str):
        torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
        asyncio.run(torrent.start_download())
       
    def extract_files(self, download_path: str, author_name: str) -> None:

        contents: list[str] = glob(download_path + "/**/*", recursive=True) 
        files: list[str] = [object for object in contents if os.path.isfile(object)]
        directories: list[str] = [object for object in contents if object not in files]
        text_extensions: tuple[str, str, str, str, str] = ("txt", "pdf", "epub", "mobi", "azw3")
        image_extensions: tuple[str, str] = ("jpg", "png")

        paths_of_downloaded_files: list[str] = []
        paths_of_downloaded_images: list[str] = []
        author_image_dir: Path = IMAGES_IN_DOWNLOADS.joinpath(author_name)

        for file in tqdm(
            iterable=files,
            desc="Extracting files of interest..."
        ):
            file_base_name: str = os.path.basename(file)
            file_is_text: bool = file.lower().endswith(text_extensions) 
            file_is_image: bool = file.lower().endswith(image_extensions) 

            if file_is_text: 
                if not Path(download_path).joinpath(file_base_name).exists():
                    shutil.move(file, download_path)

                paths_of_downloaded_files.append(
                    str(Path(download_path + f"/{file_base_name}"))
                )

            elif file_is_image: 
                if not Path(author_image_dir.joinpath(f"{file_base_name}")).exists():
                    shutil.move(file, author_image_dir)

                paths_of_downloaded_images.append(
                    str(author_image_dir.joinpath(f"{file_base_name}"))
                )
        
        self.log_downloaded_files(
            author_name=author_name, 
            paths_of_downloaded_files=paths_of_downloaded_files,
            paths_of_downloaded_images=paths_of_downloaded_images
        )

        self.remove_book_directories(directories=directories)

    @staticmethod
    def remove_book_directories(directories: list[str]) -> None:

        for directory in tqdm(
            iterable=directories,
            desc="Deleting directories that contained the extracted files..."
        ): 
            if Path(directory).exists():
                shutil.rmtree(directory)

    def log_downloaded_files(
        self, 
        author_name: str, 
        paths_of_downloaded_files: list[str],
        paths_of_downloaded_images: list[str]
    ) -> None:

        author_path: Path = find_raw_data_for_author(author_name=author_name).parent
        author_image_dir: Path = IMAGES_IN_DOWNLOADS.joinpath(author_name)

        object_types_and_paths: dict[Path, list[str]] = {
            author_path.joinpath("downloaded_files.json"): paths_of_downloaded_files,
            author_image_dir.joinpath("downloaded_images.json"): paths_of_downloaded_images 
        }

        for path, logs in object_types_and_paths.items(): 

            if Path(path).exists():
                os.remove(path)

            with open(path, mode="w") as file:
                json.dump(logs, file)


class Author:
    def __init__(
        self, 
        name: str, 
        books_via_http: list[ViaHTTP] | None = None, 
        books_via_torrent: list[ViaTorrent] | None = None,
        books_via_scraper: list[ViaScraper] | None = None,
        biographers_and_compilers: list[str] | None = None
    ) -> None:
        self.name: str = name
        self.path_to_data: Path = DATA_DIR.joinpath(name)
        self.path_to_raw_data : Path = self.path_to_data.joinpath("raw")
        self.books_via_http: list[ViaHTTP] | None = books_via_http 
        self.books_via_torrent: list[ViaTorrent] | None = books_via_torrent 
        self.books_via_scraper: list[ViaScraper] | None = books_via_scraper 
        self.biographers_and_compilers: list[str] | None = biographers_and_compilers

        self.file_paths: list[Path] = [
            self.path_to_raw_data.joinpath(file) for file in os.listdir(self.path_to_raw_data) if 
                self.path_to_raw_data.joinpath(file).is_file()  
                # Might seem unecessary if you assume that the directory will only ever contain files, but
                # I'm not willing to assume that.
        ]

    def download_books(self) -> None:

        match (self.books_via_http != None, self.books_via_torrent != None, self.books_via_scraper != None):

            case (True, True, True):
                self.download_via_http()
                self.download_via_scraper()
                self.download_via_torrents()

            case (True, False, False): 
                self.download_via_http()
            case (False, True, False):
                self.download_via_torrents()
            case(False, False, True):
                self.download_via_scraper()

            case(False, True, True):
                self.download_via_torrents()
                self.download_via_scraper()
            case(True, False, True):
                self.download_via_http()
                self.download_via_scraper()
            case (True, True, False): 
                self.download_via_http()
                self.download_via_torrents()

            case (False, False, False):
                raise Exception(f"Across download methods, no information on any books have been provided for {self.name}") 

    def download_via_http(self) -> None: 
        assert self.books_via_http != None
        self.make_paths()

        book_paths: list[str] = []
        for book in self.books_via_http:

            file_path: Path = self.path_to_raw_data.joinpath(f"{book.file_name}.pdf")
            book.download(file_path=str(file_path))
            book_paths.append(str(file_path))

    def download_via_torrents(self) -> None:
        assert self.books_via_torrent != None
        self.make_paths()
        
        for book in self.books_via_torrent:
            if self.must_torrent():
                self.leech(book=book)

    def download_via_scraper(self) -> None:
        assert self.books_via_scraper != None
        self.make_paths()

        for book in self.books_via_scraper:
            book.download(author_name=self.name)

    def must_torrent(self) -> bool:
        contents: list[str] = glob(str(self.path_to_raw_data) + "/**/*", recursive=True) 
        files_only: list[str] = [object for object in contents if os.path.isfile(object)]
        log_path: Path = self.path_to_data.joinpath("downloaded_files.json")

        if not Path(log_path).exists():
            return True
        else:
            with open(log_path, mode="r", encoding="utf-8") as file:
                logged_paths: list[str] = json.load(file)
            
            if (len(files_only) == len(logged_paths)) and len(logged_paths) != 0:
                logger.success(f"All files associated with {self.name} are available")
                return False
            else:
                logger.warning(f"Some of {self.name}'s files are missing.")
                return True

    def leech(self, book: ViaTorrent):
        book.download(file_path=str(self.path_to_raw_data))
        book.extract_files(download_path=str(self.path_to_raw_data), author_name=self.name)

    def make_paths(self):

        paths_to_create: list[Path] = [
            self.path_to_data,
            self.path_to_raw_data,
            OCR_IMAGES.joinpath(self.name),
            CHROMA_DIR.joinpath(self.name), 
            IMAGES_IN_DOWNLOADS.joinpath(self.name)
        ] 

        for path in paths_to_create:
            if not Path(path).exists():
                os.mkdir(path=path)

