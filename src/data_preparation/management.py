import os
import itertools
from pathlib import Path

from loguru import logger

from src.authors import prepare_sources
from src.data_preparation.sourcing import Author


def manage_texts(author: Author) -> None:
    manager = VersionManager(author=author)
    if manager.author.books_via_torrent != None:
        logger.success(f"Determining the final batch of texts to use for {author.name}")
        manager.eliminate_duplicates()
        manager.remove_biographical_works()
        manager.remove_complete_works()


class VersionManager:
    def __init__(self, author: Author, format_to_keep: str = "pdf") -> None:
        self.author: Author = author
        self.format_to_keep: str = format_to_keep
        self.extensions: list[str] = [".pdf", ".epub", ".mobi"]

        self.file_names: list[str] = [
            item for item in os.listdir(self.author.path_to_raw_data) if os.path.isfile(
                Path.joinpath(self.author.path_to_raw_data, item)
            )
        ]        

    def __get_file_path__(self, truncated_name: str, format: str) -> Path:
        return Path.joinpath(self.author.path_to_raw_data, truncated_name + format)

    def get_place_of_extension(self, file_name: str) -> int:
        return 5 if (".epub" in file_name) or (".mobi" in file_name) else 4

    def get_file_extension(self, file_name: str) -> str:
        extension_place: int = self.get_place_of_extension(file_name=file_name)
        return file_name[-extension_place:] 

    def get_file_name_without_extension(self, file_name: str) -> str:
        extension_place: int = self.get_place_of_extension(file_name=file_name)
        return file_name[:len(file_name)-extension_place]

    def collect_file_names_and_extensions(self) -> dict[str, str]:
        file_names_and_extensions: dict[str, str] = {} 
        for file in self.file_names:
            file_names_and_extensions[file] = self.get_file_extension(file) 

        return file_names_and_extensions 
        
    def check_version_of_file_exists(self, truncated_name: str, format: str) -> bool: 
        file_path = self.__get_file_path__(truncated_name=truncated_name, format=format) 
        return file_path.exists()

    def delete_version(self, truncated_name: str, format: str) -> None:
        file_path = self.__get_file_path__(truncated_name=truncated_name, format=format) 
        os.remove(file_path) 

    def delete_by_preference(self, names_without_extensions: list[str]) -> None:

        deprioritised_extensions: list[str] = [extension for extension in self.extensions if extension != self.format_to_keep] 
        for truncated_name in names_without_extensions:
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
                raise Exception(f"Somehow there is no version of {truncated_name} in any format")

    def remove_complete_works(self) -> None:
        texts_that_are_complete_works: list[str] = [file for file in self.file_names if "complete works" in file] 
        text_paths: list[Path] = [self.author.path_to_raw_data.joinpath(text) for text in texts_that_are_complete_works]
        for path in text_paths:
            os.remove(path)

    def eliminate_duplicates(self):

        names_and_extensions: dict[str, str] = self.collect_file_names_and_extensions()
        names_without_extensions: list[str] = [self.get_file_name_without_extension(name) for name in names_and_extensions.keys()]

        for name in names_and_extensions.keys(): 
            truncated_name: str = self.get_file_name_without_extension(name)
            count: int = names_without_extensions.count(truncated_name)
            breakpoint()
            if count == 1:
                logger.success(f'There is no duplicate of "{truncated_name}"')
            else:
                logger.success(f'There are {count} copies of "{truncated_name}"')
                self.delete_by_preference(names_without_extensions=names_without_extensions)

    def remove_biographical_works(self) -> None:
        
        biographers_and_compilers: list[str] | None = self.author.biographers_and_compilers
        
        if biographers_and_compilers != None:
            logger.warning(f"Checking for/removing texts by the biographers of {self.author.name}")
            for file_name, biographer in itertools.product(self.file_names, biographers_and_compilers):
                if biographer in file_name:
                    truncated_name: str = self.get_file_name_without_extension(file_name=file_name)
                    file_extension: str = self.get_file_extension(file_name=file_name)
                    file_path: Path = self.__get_file_path__(truncated_name=truncated_name, format=file_extension)
                    os.remove(file_path)
        else:
            logger.success(f"There are no biographers/compilers for any of the saved texts by {author.name}")


if __name__ == "__main__":
    for author in prepare_sources():
        manage_texts(author=author)
