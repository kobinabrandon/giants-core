import os
from pathlib import Path
from loguru import logger 

from src.authors import prepare_sources
from src.data_preparation.sourcing import Author


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
                breakpoint()
                self.delete_by_preference(names_without_extensions=names_without_extensions)

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

            # pattern = rf"/\raw\/([^\/]+)\.{escape(extension)}$" 
            # match: Match[str] | None = search(pattern, path)
            # if match:
            #     pass
            #


if __name__ == "__main__":
    for author in prepare_sources():
        selector = VersionManager(author=author)
        if author.books_via_torrent != None:
            logger.warning(f"Text selection required for the works of {author.name}")
            selector.eliminate_duplicates()
        else:
            logger.success(f"No text selection required for the works of {author.name}")

