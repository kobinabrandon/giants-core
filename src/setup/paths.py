import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()

IMAGES_DIR = PARENT_DIR.joinpath("images") 
OCR_IMAGES = IMAGES_DIR.joinpath("ocr")
IMAGES_IN_DOWNLOADS = IMAGES_DIR.joinpath("images_in_downloads")

DATA_DIR = PARENT_DIR.joinpath("data")
CHROMA_DIR = PARENT_DIR.joinpath("./chroma")
AUTHORS_FILE_DIR = DATA_DIR.joinpath("archive.json") 


def make_fundamental_paths():

    paths_to_create: list[Path] = [IMAGES_DIR, DATA_DIR, OCR_IMAGES, IMAGES_IN_DOWNLOADS, CHROMA_DIR]

    for path in paths_to_create:
        if not Path(path).exists():
            os.mkdir(path)


def get_author_dir(author_name: str) -> Path:
    return Path.joinpath(DATA_DIR, author_name)

