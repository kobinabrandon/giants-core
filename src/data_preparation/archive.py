import json 
from loguru import logger

from src.authors import prepare_sources
from src.setup.paths import ARCHIVE_DIR 
from src.data_preparation.sourcing import ViaHTTP, ViaTorrent, ViaScraper, Author
from src.setup.types import HTTPArchive, TorrentArchive, ScrapedArchive, AuthorArchive 


class AuthorArchiver:
    def __init__(self, author: Author):
        self.author: Author = author

    def archive_http_downloads(self, books: list[ViaHTTP] | None) -> HTTPArchive:
        assert books != None
        book_archive: HTTPArchive = {}
        for book in books:
            book_archive[self.author.name] =  []
            book_details: dict[str, str | bool | int | None] = {
                "title": book.title,
                "url": book.url,
                "format": book.format,
                "needs_ocr": book.needs_ocr,
                "start_page": book.start_page, 
                "end_page": book.end_page, 
            }

            book_archive[self.author.name].append(book_details)

        return book_archive

    def archive_torrent_downloads(self, books: list[ViaTorrent] | None) -> TorrentArchive: 
        assert books != None
        torrent_archive: TorrentArchive = [] 
        for batch in books:
            torrent_archive.append({
                f"magnet #{books.index(batch)}": batch.magnet,
                "biographers_and_compilers": self.author.biographers_and_compilers
            })

        return torrent_archive

    def archive_scraped_details(self, books: list[ViaScraper] | None) -> ScrapedArchive: 
        assert books != None
        archive: ScrapedArchive = {} 
        for book in books:
            archive[self.author.name] =  []
            book_details: dict[str, str] = {"title": book.title, "url": book.url}
            archive[self.author.name].append(book_details)

        return archive

    def construct_archive(
        self, 
        books_from_http: list[ViaHTTP] | None, 
        books_from_torrent: list[ViaTorrent] | None, 
        books_from_scraper: list[ViaScraper] | None 
        ) -> AuthorArchive:

        match (books_from_http!= None, books_from_torrent != None, books_from_scraper != None):
            case (True, True, True):
                return (
                        self.archive_http_downloads(books=books_from_http), 
                        self.archive_torrent_downloads(books=books_from_torrent), 
                        self.archive_scraped_details(books=books_from_scraper)
                )

            case (True, False, False): 
                return self.archive_http_downloads(books=books_from_http)
            case (False, True, False):
                return self.archive_torrent_downloads(books=books_from_torrent)
            case(False, False, True):
                return self.archive_scraped_details(books=books_from_scraper)
            case(False, True, True):
                return self.archive_http_downloads(books=books_from_http), self.archive_scraped_details(books=books_from_scraper)
            case(True, False, True):
                return self.archive_http_downloads(books=books_from_http), self.archive_scraped_details(books=books_from_scraper)
            case (True, True, False): 
                return self.archive_http_downloads(books=books_from_http), self.archive_torrent_downloads(books=books_from_torrent)
            case (False, False, False):
                logger.warning(f"No book metadata have been provided for {self.author.name} (regardless of source)")


def make_final_archive(authors: list[Author]):
    final_archive: list[AuthorArchive] = [] 
    for author in authors:
        books_from_http: list[ViaHTTP] | None = author.books_via_http 
        books_from_torrent: list[ViaTorrent] | None = author.books_via_torrent
        books_from_scraper: list[ViaScraper] | None = author.books_via_scraper

        archiver = AuthorArchiver(author=author)
        author_archive: AuthorArchive = archiver.construct_archive(
            books_from_http=books_from_http, 
            books_from_torrent=books_from_torrent, 
            books_from_scraper=books_from_scraper
        ) 

        final_archive.append(author_archive)

    with open(ARCHIVE_DIR, mode="w") as file:
        json.dump(final_archive, file)
        
    logger.success("Archived sources") 


if __name__ == "__main__":
    authors: list[Author] = prepare_sources()
    make_final_archive(authors=authors)

