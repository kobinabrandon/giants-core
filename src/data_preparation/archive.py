import json
from loguru import logger 

from src.authors import prepare_sources
from src.setup.paths import AUTHORS_FILE_DIR
from src.setup.types import BookArchive, BatchArchive 
from src.data_preparation.sourcing import Book, Batch, Author


class Archiver:
    def __init__(self, author: Author):
        self.author: Author = author

    def archive_books(self, books: list[Book]) -> BookArchive:
        book_archive: BookArchive = {}
        for book in books:
            book_archive[self.author.name] =  []
            book_details: dict[str, str | bool | int | None] = {
                "title": book.title,
                "url": book.url,
                "needs_ocr": book.needs_ocr,
                "start_page": book.start_page, 
                "end_page": book.end_page, 
                "file_name": book.file_name
            }

            book_archive[self.author.name].append(book_details)

        return book_archive

    def archive_batches(self, batches: list[Batch]) -> BatchArchive: 
        batch_archive: BatchArchive = [] 
        for batch in batches:
            batch_archive.append({
                f"magnet #{batches.index(batch)}": batch.magnet
            })

        return batch_archive


def make_archive(authors: list[Author]):
    full_archive: list[BookArchive | BatchArchive] = [] 
    for author in authors:
        archiver = Archiver(author=author)

        if (author.books != None) and (author.batches == None):
            author_archive: BookArchive = archiver.archive_books(books=author.books)
            
        elif (author.books == None) and (author.batches != None):
            author_archive: BatchArchive = archiver.archive_batches(batches=author.batches)

        elif (author.books != None) and (author.batches != None):
            author_archive: BookArchive = archiver.archive_books(books=author.books)
            batch_archive: BatchArchive = archiver.archive_batches(batches=author.batches)
            author_archive[author.name].append(batch_archive)

        else:
            author_archive: BookArchive = {}
            author_archive[author.name] = []

        full_archive.append(author_archive)

    with open(AUTHORS_FILE_DIR, mode="w") as file:
        json.dump(full_archive, file)
        
    logger.success("Archived sources") 


if __name__ == "__main__":
    authors: list[Author] = prepare_sources()
    make_archive(authors=authors)

