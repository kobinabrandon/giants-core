import requests
from pathlib import Path
from loguru import logger
from paths import RAW_DATA_DIR, make_data_directories
from langchain.document_loaders.pdf import PyPDFDirectoryLoader


class Book:
    def __init__(self, url: str, title: str, file_name: str) -> None:
        self.url = url 
        self.title = title
        self.file_name = file_name
        self.file_path = RAW_DATA_DIR / f"{file_name}.pdf"

    def download(self):
        if Path(self.file_path).exists():
            logger.success(f"'{self.file_name} is already saved to disk'")
        else:
            logger.warning(f'You do not have "{self.title}" -> Downloading it now...')
            response = requests.get(url=self.url)

            if response.status_code == 200:
                with open(self.file_path, mode="wb") as file:
                    _ = file.write(response.content)
                logger.success(f"Downloaded {self.title}")
            else:
                logger.error(f"Couldn't download {self.title}. Status code: {response.status_code}")

    def load(self):
        document_loader = PyPDFDirectoryLoader(self.file_path)


neo_colonialism = Book(
    file_name="neo_colonialism", 
    title="Neo-Colonialism, the Last Stage of imperialism",
    url="https://www.marxists.org/ebooks/nkrumah/nkrumah-neocolonialism.pdf"
)

dark_days = Book(
    title="Dark Days in Ghana",
    file_name="dark_days_in_ghana",
    url="https://www.marxists.org/subject/africa/nkrumah/1968/dark-days.pdf"
)

africa_unite = Book(
    title="Africa Must Unite",
    file_name="africa_must_unite",
    url="https://ccaf.africa/books/Africa-Must-Unite-Kwame-Nkrumah.pdf"
)


if __name__ == "__main__":
    make_data_directories()
    for book in [neo_colonialism, dark_days, africa_unite]:
        book.download()

