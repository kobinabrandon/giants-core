import os
import itertools
from pathlib import Path

from loguru import logger

from src.authors import prepare_sources
from src.data_preparation.sourcing import Author
from src.data_preparation.utils import get_file_extension, get_file_name_without_extension


class VersionManager:
    def __init__(self, author: Author) -> None:
        self.author: Author = author
        self.extensions: list[str] = [".pdf", ".epub", ".mobi"]

        self.file_names: list[str] = [
            item for item in os.listdir(self.author.path_to_raw_data) if 
                Path.joinpath(self.author.path_to_raw_data, item).is_file()
        ]        

    def __get_file_path__(self, truncated_name: str, format: str) -> Path:
        return Path.joinpath(self.author.path_to_raw_data, truncated_name + format)

    def collect_file_names_and_extensions(self) -> dict[str, str]:
        file_names_and_extensions: dict[str, str] = {} 
        for file_name in self.file_names:
            file_names_and_extensions[file_name] = get_file_extension(file_name_or_path=file_name) 

        return file_names_and_extensions 
        
    def check_version_of_file_exists(self, truncated_name: str, format: str) -> bool: 
        file_path = self.__get_file_path__(truncated_name=truncated_name, format=format) 
        return file_path.exists()

    def delete_version(self, truncated_name: str, format: str) -> None:
        file_path = self.__get_file_path__(truncated_name=truncated_name, format=format) 
        os.remove(file_path) 

    def delete_by_preference(self, file_names_without_extensions: list[str], format_to_keep: str = "pdf") -> None:

        deprioritised_extensions: list[str] = [extension for extension in self.extensions if extension != format_to_keep] 
        for truncated_name in file_names_without_extensions:
            pdf_exists: bool = self.check_version_of_file_exists(truncated_name=truncated_name, format=".pdf")
            epub_exists: bool = self.check_version_of_file_exists(truncated_name=truncated_name, format=".epub")
            mobi_exists: bool = self.check_version_of_file_exists(truncated_name=truncated_name, format=".mobi")

            if pdf_exists:
                for extension in deprioritised_extensions:
                    try:
                        self.delete_version(truncated_name=truncated_name, format=extension) 
                    except Exception as error:
                        logger.error(error)

            elif epub_exists and mobi_exists:
                self.delete_version(truncated_name=truncated_name, format=".mobi") 
            elif epub_exists and not mobi_exists:
                logger.success(f"Only the epub version of {truncated_name} exists.")
            elif not epub_exists and mobi_exists:
                logger.success(f"Only the mobi version of {truncated_name} exists.")
            else:
                logger.warning(f"Somehow there is no version of {truncated_name} in any format")

    def remove_complete_works(self) -> None:
        texts_that_are_complete_works: list[str] = [file for file in self.file_names if "complete works" in file] 
        text_paths: list[Path] = [self.author.path_to_raw_data.joinpath(text) for text in texts_that_are_complete_works]
        for path in text_paths:
            os.remove(path)

    def eliminate_duplicates(self):

        file_names_and_extensions: dict[str, str] = self.collect_file_names_and_extensions()

        file_names_without_extensions: list[str] = [
            get_file_name_without_extension(name) for name in file_names_and_extensions.keys()
        ]

        for name in file_names_and_extensions.keys(): 
            truncated_name: str = get_file_name_without_extension(name)
            count: int = file_names_without_extensions.count(truncated_name)
            if count == 1:
                logger.success(f'There is no duplicate of "{truncated_name}"')
            else:
                logger.success(f'There are {count} copies of "{truncated_name}"')
                self.delete_by_preference(file_names_without_extensions=file_names_without_extensions)

    def remove_biographical_works(self) -> None:
        
        biographers_and_compilers: list[str] | None = self.author.biographers_and_compilers
        
        if biographers_and_compilers != None:
            logger.warning(f"Checking for/removing texts by the biographers of {self.author.name}")
            for file_name, biographer in itertools.product(self.file_names, biographers_and_compilers):
                if biographer in file_name:
                    truncated_name: str = get_file_name_without_extension(file_name_or_path=file_name)
                    file_extension: str = get_file_extension(file_name_or_path=file_name)
                    file_path: Path = self.__get_file_path__(truncated_name=truncated_name, format=file_extension)
                    os.remove(file_path)
        else:
            logger.success(f"There are no biographers/compilers for any of the saved texts by {author.name}")


if __name__ == "__main__":
    for author in prepare_sources():
        manager = VersionManager(author=author)
        if manager.author.books_via_torrent != None:
            logger.success(f"Determining the final batch of texts to use for {author.name}")
            manager.eliminate_duplicates()
            manager.remove_biographical_works()
            manager.remove_complete_works()

