import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()

IMAGES_DIR = PARENT_DIR.joinpath("images") 
CHROMA_DIR = PARENT_DIR.joinpath("./chroma")

DATA_DIR = PARENT_DIR.joinpath("data")
AUTHORS_FILE_DIR = DATA_DIR.joinpath("authors.json") 
# BOOK_IMAGES_DIR = IMAGES_DIR.joinpath("book_images")


def make_fundamental_paths():

    paths_to_create: list[Path] = [IMAGES_DIR, DATA_DIR, CHROMA_DIR]

    for path in paths_to_create:
        if not Path(path).exists():
            os.mkdir(path)


def get_author_dir(author_name: str) -> Path:
    return Path.joinpath(DATA_DIR, author_name)

