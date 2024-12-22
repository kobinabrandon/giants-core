from loguru import logger 
from dropbox import Dropbox

from general.books import Book
from general.config import general_config


box = Dropbox(general_config.dropbox_access_token)

def upload_to_dropbox(book: Book) -> None:

    remote_file_path = f"/{book.file_name}.pdf"

    try:
        logger.info(f'Checking whether {book.title} has already been uploaded')
        metadata = box.files_get_metadata(path=remote_file_path) 

        if remote_file_path in metadata.values():
            logger.success(f'"{book.title}" is already on Dropbox')

    except Exception as error:
        logger.error(error)
        logger.info(f'File not found. Attempting to upload "{book.title}" to Dropbox')

        with open(book.file_path, "rb") as file:
           box.files_upload(f=file.read(), path=remote_file_path)

        logger.success(f"'{book.title}'uploaded to Dropbox")


def download_from_dropbox(book: Book) -> None:
    metadata, response = box.files_download(f"/{book.file_name}.pdf")

    with open(book.file_path, "wb") as file:
        file.write(response.content)

