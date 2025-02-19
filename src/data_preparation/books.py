import requests

from pathlib import Path
from loguru import logger

from src.setup.paths import set_paths

class Book:
    """
    Attributes: 
        url: 
        title: 
        core_pages: a range of integers representing the page numbers of all the core pages of the book. 
        file_path: 
    """
    def __init__(self, url: str, title: str, core_pages: range | None = None) -> None:
        self.url: str = url 
        self.title: str = title
        self.core_pages: range | None = core_pages
        
        self.file_name: str = title.lower().replace(" ", "_") 
        self.file_path: Path =  self.__get_file_path__() / f"{self.file_name}.pdf"
    
    def download(self) -> None:
        
        if not Path(self.file_path).exists():
            logger.warning(f'Unable to find "{self.title}" on disk -> Downloading it now...')
            try:
                response = requests.get(url=self.url)

                if response.status_code == 200:
                    with open(self.file_path, mode="wb") as file:
                        _ = file.write(response.content)

                    logger.success(f'Downloaded "{self.title}"')
               
            except Exception as error:
                logger.error(error)
                logger.error(f"Unable to download {self.title}.")
        
    @staticmethod
    def __get_file_path__() -> Path:
        return set_paths()["raw_data"]




