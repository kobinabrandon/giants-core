import asyncio
import requests
from pathlib import Path
from loguru import logger
from torrentp import TorrentDownloader

from src.setup.paths import get_author_dir


class Book:
    def __init__(
        self, 
        title: str, 
        url: str | None, 
        torrent: bool = False,
        needs_ocr: bool = False, 
        magnet: str | None = None,
        start_page: int | None = None, 
        end_page: int | None = None
    ) -> None:

        self.title: str = title
        self.url: str | None = url 
        self.author: str | None = None
        self.needs_ocr: bool = needs_ocr
        self.magnet: str | None = magnet 
        self.torrent: bool | None = torrent
        self.start_page: int | None = start_page
        self.end_page: int | None = end_page
        self.file_name: str = title.lower().replace(" ", "_") 
    
    def get_save_path(self, author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        raw_data_path = Path.joinpath(author_path, "raw")
        return Path.joinpath(raw_data_path/ f"{self.file_name}.pdf") 

    def download(self, file_path: str) -> None:
        
        if not self.torrent and self.url != None:
            if not Path(file_path).exists():
                logger.warning(f'Unable to find "{self.title}" on disk -> Downloading it now...')
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

    def download(self, file_path: str):
        torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
        asyncio.run(torrent.start_download())
           
    @staticmethod
    def get_save_path(author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        return Path.joinpath(author_path, "raw")


class Author:
    def __init__(self, name: str, books: list[Book] | None = None, batch: Batch | None = None) -> None:
        self.name: str = name
        self.books: list[Book] | None = books
        self.batch: Batch | None = batch 

    def download_individually(self) -> None:
        assert self.books != None
        for book in self.books:
            file_path = book.get_save_path(author_name=self.name)
            book.download(file_path=str(file_path))

    def download_batch(self) -> None:
        assert self.batch != None
        file_path = self.batch.get_save_path(author_name=self.name)
        self.batch.download(file_path=str(file_path))

    def download_books(self) -> None:

        if (self.books != None) and (self.batch != None):
            self.download_individually()
            self.download_batch()

        elif self.books != None:
            self.download_individually()

        elif self.batch != None:
            self.download_batch()

