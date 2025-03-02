import os 
import asyncio
import shutil
import requests
from tqdm import tqdm
from glob import glob
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

    def extract_texts(self, download_path: str):

        contents: list[str] = glob(download_path + "/**/*", recursive=True) 
        files: list[str] = [object for object in contents if os.path.isfile(object)]
        directories: list[str] = [object for object in contents if object not in files]
        extensions_of_interest: tuple[str, str,str,str] = ("txt", "pdf", "epub", "jpg")

        for file in tqdm(
            iterable=files,
            desc="Extracting files of interest..."
        ):
            file_has_desired_format: bool = file.lower().endswith(extensions_of_interest) 
            file_base_name: str = os.path.basename(file)
            if file_has_desired_format and not Path(download_path + f"/{file_base_name}").exists():
                shutil.move(file, download_path)

        # Clean up directories 
        for directory in tqdm(
            iterable=directories,
            desc="Deleting directories that contained the extracted files..."
        ): 
            if Path(directory).exists():
                shutil.rmtree(directory)


class Author:
    def __init__(self, name: str, books: list[Book] | None = None, batches: list[Batch] | None = None) -> None:
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
            torrent.download(file_path=str(file_path))
            torrent.extract_texts(download_path=str(file_path))

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
        paths_to_create: list[Path] = [AUTHOR_DIR] + [
            Path.joinpath(AUTHOR_DIR, path) for path in ["raw", "chroma_memory", "text_embeddings"]
        ] 

        for path in paths_to_create:
            if not Path(path).exists():
                os.mkdir(path=path)

