import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()
CHROMA_DIR = PARENT_DIR / "./chroma"

DATA_DIR = PARENT_DIR / "data"
AUTHORS_FILE_DIR = DATA_DIR / "authors.json"


def make_data_directories(author_name: str) -> None: 

    AUTHOR_DIR: Path = get_author_dir(author_name=author_name) 
    paths_to_create: list[Path] = [AUTHOR_DIR] + [
        Path.joinpath(AUTHOR_DIR, path) for path in ["raw", "chroma_memory", "text_embeddings"]
    ] 

    for path in paths_to_create:
        if not Path(path).exists():
            os.mkdir(path=path)


def get_author_dir(author_name: str) -> Path:
    return Path.joinpath(DATA_DIR, author_name)

