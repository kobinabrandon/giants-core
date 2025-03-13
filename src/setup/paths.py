import os 
from pathlib import Path 


PARENT_DIR = Path("__file__").parent.resolve()
DATA_DIR = PARENT_DIR.joinpath("data")
IMAGES_DIR = PARENT_DIR.joinpath("images") 

OCR_OUTPUTS = PARENT_DIR.joinpath("OCR")
OCR_IMAGES = OCR_OUTPUTS.joinpath("images")
PDFS_AFTER_OCR = OCR_OUTPUTS.joinpath("pdf")
TXT_AFTER_OCR = OCR_OUTPUTS.joinpath("txt") 

CHROMA_DIR = PARENT_DIR.joinpath("./chroma")
ARCHIVE_DIR = DATA_DIR.joinpath("archive.json") 
IMAGES_IN_DOWNLOADS = IMAGES_DIR.joinpath("images_in_downloads")


def make_fundamental_paths():

    paths_to_create: list[Path] = [
        IMAGES_DIR, 
        DATA_DIR, 
        CHROMA_DIR,
        OCR_OUTPUTS, 
        OCR_IMAGES, 
        PDFS_AFTER_OCR, 
        TXT_AFTER_OCR,
        IMAGES_IN_DOWNLOADS, 
    ]

    for path in paths_to_create:
        if not Path(path).exists():
            os.mkdir(path)

