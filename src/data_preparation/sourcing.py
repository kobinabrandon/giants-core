import os 
import asyncio
import shutil
import requests
from tqdm import tqdm
from pathlib import Path
from loguru import logger

from torrentp import TorrentDownloader
from src.setup.paths import get_author_dir


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

    def download(self, file_path: str):
        torrent = TorrentDownloader(file_path=self.magnet, save_path=file_path)
        asyncio.run(torrent.start_download())
           
    @staticmethod
    def get_save_path(author_name: str) -> Path:
        author_path: Path = get_author_dir(author_name=author_name) 
        return Path.joinpath(author_path, "raw")

    def extract_texts(self, download_path: str, author_name: str):

        for (root, _, files) in tqdm(
            iterable=os.walk(download_path), 
            desc="Moving files"
        ): 
            breakpoint()
            for file in files:
                if file.lower().endswith("pdf") or file.lower().endswith("epub") or file.lower().endswith("jpg"):
                    file_path: str = os.path.join(root, file)
                    immediate_parent: str = os.path.dirname(file_path)

                    if (immediate_parent != download_path) and not Path(download_path+f"/{file}").exists(): 
                        shutil.move(file_path, download_path)
                        if download_path == os.path.dirname(os.path.dirname(file_path)):
                            shutil.rmtree(immediate_parent)
            
            for dir in os.listdir(root):
                path: str = root+f"/{dir}"
                if os.path.isdir(path):
                     shutil.rmtree(path)
            

class Author:
    def __init__(self, name: str, books: list[Book] | None = None, batches: list[Batch] | None = None) -> None:
        self.name: str = name
        self.books: list[Book] | None = books
        self.batches: list[Batch] | None = batches 

    def download_individually(self) -> None:
        assert self.books != None
        for book in self.books:
            file_path = book.get_save_path(author_name=self.name)
            book.download(file_path=str(file_path))

    def download_batch(self) -> None:
        assert self.batches != None
        for torrent in self.batches:
            file_path = torrent.get_save_path(author_name=self.name)
            torrent.download(file_path=str(file_path))
            torrent.extract_texts(download_path=str(file_path), author_name=self.name)

    def download_books(self) -> None:

        if (self.books != None) and (self.batches != None):
            self.download_individually()
            self.download_batch()

        elif self.books != None:
            self.download_individually()

        elif self.batches != None:
            self.download_batch()

