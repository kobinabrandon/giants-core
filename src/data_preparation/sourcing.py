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


class Book:
    def __init__(
        self, 
        title: str, 
        url: str | None, 
        format: str = "pdf",
        torrent: bool = False,
        needs_ocr: bool = False, 
        magnet: str | None = None,
        start_page: int | None = None, 
        end_page: int | None = None
    ) -> None:

        self.title: str = title
        self.format: str = format
        self.url: str | None = url 
        self.author: str | None = None
        self.needs_ocr: bool = needs_ocr
        self.magnet: str | None = magnet 
        self.torrent: bool | None = torrent
        self.start_page: int | None = start_page
        self.end_page: int | None = end_page
        self.file_name: str = title.lower().replace(" ", "_") 

        make_fundamental_paths()
    
    def get_save_path(self, author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        raw_data_path = Path.joinpath(author_path, "raw")
        return Path.joinpath(raw_data_path/ f"{self.file_name}.pdf") 

    def download(self, file_path: str) -> None:
        
        if not self.torrent and self.url != None:
            if not Path(file_path).exists():
                logger.warning(f'Unable to find "{self.title}" on disk -> Downloading...')
                try:
                    response = requests.get(url=self.url)

                    if response.status_code == 200:
                        with open(file_path, mode="wb") as file:
                            _ = file.write(response.content)

                        logger.success(f'Downloaded "{self.title}"')
                   
                except Exception as error:
                    logger.error(error)
                    logger.error(f"Unable to download {self.title}.")
        else:
            torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
            asyncio.run(torrent.start_download())
            logger.success(f'Downloaded "{self.title}"')
           

class Batch:
    def __init__(self, magnet: str) -> None:
        self.magnet: str = magnet 

    def download(self, file_path: str, author_name: str):

        downloaded_files: list[str] = self.find_downloaded_files(author_name)
        breakpoint()
        exist: list[str] = []

        for file in downloaded_files:
            if Path(file).exists():
                exist.append(file)

        if len(downloaded_files) != 0 and len(exist) == len(downloaded_files):
            logger.success(f"All of the files associated with {author_name} already exist")
        else:
            logger.warning(f"Some of {author_name}'s files are missing.")
            torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
            asyncio.run(torrent.start_download())
           
    @staticmethod
    def get_save_path(author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        return Path.joinpath(author_path, "raw")

    def extract_files(self, download_path: str, author_name: str) -> None:

        contents: list[str] = glob(download_path + "/**/*", recursive=True) 
        files: list[str] = [object for object in contents if os.path.isfile(object)]
        directories: list[str] = [object for object in contents if object not in files]
        text_extensions: tuple[str, str, str] = ("txt", "pdf", "epub")
        image_extensions: tuple[str, str] = ("jpg", "png")

        author_image_dir: Path = IMAGES_DIR.joinpath(author_name)
        paths_of_downloaded_files: list[str] = []

        for file in tqdm(
            iterable=files,
            desc="Extracting files of interest..."
        ):
            file_base_name: str = os.path.basename(file)
            file_is_text: bool = file.lower().endswith(text_extensions) 
            file_is_image: bool = file.lower().endswith(image_extensions) 

            if file_is_text and not Path(download_path + f"/{file_base_name}").exists():
                shutil.move(file, download_path)
                paths_of_downloaded_files.append(
                    str(Path(download_path + f"/{file_base_name}"))
                )

            elif file_is_image and not Path(author_image_dir.joinpath(f"{file_base_name}")).exists():
                shutil.move(file, author_image_dir)
                paths_of_downloaded_files.append(
                    str(author_image_dir.joinpath(f"/{file_base_name}"))
                )
        
        self.log_downloaded_files(author_name=author_name, paths_of_downloaded_files=paths_of_downloaded_files)
        self.remove_book_directories(directories=directories)

    @staticmethod
    def remove_book_directories(directories: list[str]) -> None:

        for directory in tqdm(
            iterable=directories,
            desc="Deleting directories that contained the extracted files..."
        ): 
            if Path(directory).exists():
                shutil.rmtree(directory)

    def log_downloaded_files(self, author_name: str, paths_of_downloaded_files: list[str]) -> None:
        author_path: Path = get_author_dir(author_name=author_name)
        log_path: Path = author_path.joinpath("downloaded_files.json")

        with open(log_path, mode="w") as file:
            json.dump(paths_of_downloaded_files, file)

    def find_downloaded_files(self, author_name: str) -> list[str]: 
        author_path: Path = get_author_dir(author_name=author_name)
        log_path: Path = author_path.joinpath("downloaded_files.json")
        
        if not Path(log_path).exists():
            paths: list[str] = []
        else:
            with open(log_path, mode="r", encoding="utf-8") as file:
                paths: list[str] = json.load(file)
            
        return paths


class Author:
    def __init__(
        self, 
        name: str, 
        books: list[Book] | None = None, 
        batches: list[Batch] | None = None
    ) -> None:
        self.name: str = name
        self.books: list[Book] | None = books
        self.batches: list[Batch] | None = batches 

    def download_individually(self) -> None:
        assert self.books != None
        self.make_paths()

        for book in self.books:
            file_path = book.get_save_path(author_name=self.name)
            book.download(file_path=str(file_path))

    def download_batch(self) -> None:
        assert self.batches != None
        self.make_paths()
        
        for torrent in self.batches:
            file_path = torrent.get_save_path(author_name=self.name)
            torrent.download(file_path=str(file_path), author_name=self.name)
            torrent.extract_files(download_path=str(file_path), author_name=self.name)

    def download_books(self) -> None:

        if (self.books != None) and (self.batches != None):
            self.download_individually()
            self.download_batch()

        elif self.books != None:
            self.download_individually()

        elif self.batches != None:
            self.download_batch()

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

