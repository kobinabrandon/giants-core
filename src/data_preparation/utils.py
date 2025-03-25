from src.authors import prepare_sources
from src.data_preparation.sourcing import Author


def get_file_extension(file_name_or_path: str) -> str:
    extension_place: int = get_place_of_extension(file_name_or_path=file_name_or_path)
    return file_name_or_path[-extension_place:] 

def get_file_name_without_extension(file_name_or_path: str) -> str:
    extension_place: int = get_place_of_extension(file_name_or_path=file_name_or_path)
    return file_name_or_path[:len(file_name_or_path)-extension_place]

def get_place_of_extension(file_name_or_path: str) -> int:
    is_epub_or_mobi: bool = file_name_or_path.endswith(".epub") or file_name_or_path.endswith(".mobi")
    is_pdf_or_txt: bool = file_name_or_path.endswith(".pdf") or file_name_or_path.endswith(".txt") 

    if is_epub_or_mobi:
        return 5
    else: 
        assert is_pdf_or_txt, f"{file_name_or_path} is neither a .mobi, .epub, .txt nor .pdf file. Unable to return the location of the extension"
        return 4

def get_author(nickname: str) -> Author | None:

    matching_authors: list[Author] = [author for author in prepare_sources() if nickname in author.name.lower()]

    if len(matching_authors) == 0:
        raise Exception(f"The nickname {nickname} doesn't correspond to any existing author")
    elif len(matching_authors) == 1:
        # logger.warning(f"Querying {matching_authors[0].name}'s vector database")
        return matching_authors[0]
    else:
        raise Exception(f"The nickname {nickname} correponds to {len(matching_authors)} authors. Pick a better nickname!")



