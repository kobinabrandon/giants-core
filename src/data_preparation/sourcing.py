import os
import json
import asyncio
import shutil
import requests
from tqdm import tqdm
from glob import glob
from pathlib import Path
from loguru import logger

from torrentp import TorrentDownloader
from src.setup.paths import CHROMA_DIR, IMAGES_DIR, get_author_dir, make_fundamental_paths


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
        self.author: str | None = None
        self.needs_ocr: bool = needs_ocr
        self.start_page: int | None = start_page
        self.end_page: int | None = end_page
        self.file_name: str = title.lower().replace(" ", "_") 
        make_fundamental_paths()
    
    def get_save_path(self, author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        raw_data_path = Path.joinpath(author_path, "raw")
        return Path.joinpath(raw_data_path, f"{self.file_name}.pdf") 

    def download(self, file_path: str) -> None:
        
        assert self.url != None
        if not Path(file_path).exists():
            logger.warning(f'Unable to find "{self.title}" on disk -> Downloading...')
            try:
                response = requests.get(url=self.url)
                if response.status_code == 200:
                    with open(file_path, mode="wb") as file:
                        _ = file.write(response.content)

                    logger.success(f'Downloaded "{self.title}"')
               
            except Exception as error:
                logger.error(f"Unable to download {self.title}.")
          

class ViaTorrent:
    def __init__(self, magnet: str) -> None:
        self.magnet: str = magnet 

    def download(self, file_path: str):
        torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
        asyncio.run(torrent.start_download())
       
    @staticmethod
    def get_destination_path(author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        return Path.joinpath(author_path, "raw")

    def extract_files(self, download_path: str, author_name: str) -> None:

        contents: list[str] = glob(download_path + "/**/*", recursive=True) 
        files: list[str] = [object for object in contents if os.path.isfile(object)]
        directories: list[str] = [object for object in contents if object not in files]
        text_extensions: tuple[str, str, str, str, str] = ("txt", "pdf", "epub", "mobi", "azw3")
        image_extensions: tuple[str, str] = ("jpg", "png")

        paths_of_downloaded_files: list[str] = []
        paths_of_downloaded_images: list[str] = []
        author_image_dir: Path = IMAGES_DIR.joinpath(author_name)

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

        author_path: Path = get_author_dir(author_name=author_name)
        author_image_dir: Path = IMAGES_DIR.joinpath(author_name)

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
        books_via_torrent: list[ViaTorrent] | None = None
    ) -> None:
        self.name: str = name
        self.books_via_http: list[ViaHTTP] | None = books_via_http 
        self.books_via_torrent: list[ViaTorrent] | None = books_via_torrent 

    def download_via_http(self) -> None: 
        assert self.books_via_http != None
        self.make_paths()

        book_paths: list[str] = []
        for book in self.books_via_http:
            file_path = book.get_save_path(author_name=self.name)
            book.download(file_path=str(file_path))
            book_paths.append(str(file_path))

    def must_torrent(self, torrent: ViaTorrent) -> bool:

        file_path = torrent.get_destination_path(author_name=self.name)
        contents = glob(str(file_path) + "/**/*", recursive=True) 
        files_only = [object for object in contents if os.path.isfile(object)]

        author_path: Path = get_author_dir(author_name=self.name)
        log_path: Path = author_path.joinpath("downloaded_files.json")

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

    def leech(self, torrent: ViaTorrent):
        file_path = torrent.get_destination_path(author_name=self.name)
        torrent.download(file_path=str(file_path))
        torrent.extract_files(download_path=str(file_path), author_name=self.name)

    def download_via_torrents(self) -> None:
        assert self.books_via_torrent != None
        self.make_paths()
        
        for torrent in self.books_via_torrent:
            if self.must_torrent(torrent=torrent):
                self.leech(torrent=torrent)

    def download_books(self) -> None:

        if (self.books_via_http != None) and (self.books_via_torrent != None):
            self.download_via_http()
            self.download_via_torrents()

        elif self.books_via_http != None:
            _ = self.download_via_http()

        elif self.books_via_torrent != None:
            self.download_via_torrents()

    def make_paths(self):

        AUTHOR_DIR: Path = get_author_dir(author_name=self.name) 

        paths_to_create: list[Path] = [
            AUTHOR_DIR,
            IMAGES_DIR.joinpath(self.name),
            Path.joinpath(AUTHOR_DIR, "raw"), 
            Path.joinpath(CHROMA_DIR, self.name), 
        ] 

        for path in paths_to_create:
            if not Path(path).exists():
                os.mkdir(path=path)

