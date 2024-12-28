"""
Contains code for embedding chunks of text into selected vector databases.
"""
import time 
from pathlib import Path
from loguru import logger 
from argparse import ArgumentParser 

from langchain_core.documents import Document
from langchain_chroma.vectorstores import Chroma
from pinecone import Index, Pinecone, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

from src.config import config
from src.reading import read_books
from src.chunking import split_documents 

from general.paths import set_paths
from general.books import Book, neo_colonialism, dark_days, africa_unite
    

def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=config.embedding_model_name)


class ChromaAPI:
    def __init__(self) -> None:
        self.persist_directory: Path = set_paths(from_scratch=False, general=False)["chroma"]
        self.books: list[Book] = [neo_colonialism, dark_days, africa_unite]

        self.store: Chroma = Chroma(
            collection_name="nkrumah",
            persist_directory=str(self.persist_directory),
            embedding_function=get_embedding_model()
        ) 

    def add_documents(self, chunk: bool) -> list[str]:
        documents: list[Document] = read_books(books=self.books)         

        if chunk:
            chunks = split_documents(documents=documents)
            ids = self.store.add_documents(documents=chunks)
        else:
            ids = self.store.add_documents(documents=documents)

        logger.success(f"Successfully embedded the {'chunks of' if chunk else ''} text and saved the results to ChromaDB.")
        return ids


class PineconeAPI:
    """
    Allows for the creation and accessing of Pinecone indices.

    Attributes: 
        api_key: the Pinecone API key
        multi_index: whether we want to create an index for each book, or a single one for all the books.
        store: an instance of the Pinecone class
        books: a list of the books that we want Pinecone indices for. 

        index_names: the names of the indices that we want to create or access. It is determined by the 
                     value of the multi_index attribute.
    """
    def __init__(self, multi_index: bool = False, api_key: str = config.pinecone_api_key) -> None:
        self.api_key: str = api_key 
        self.multi_index: bool = multi_index 
        self.store: Pinecone =  Pinecone(api=api_key)
        self.books: list[Book] = [neo_colonialism, dark_days, africa_unite]

        # Pinecone does not allow underscores in index names 
        self.index_names: list[str] = ["nkrumah"] if not self.multi_index else [book.file_name.replace("_", "-") for book in self.books]         

    def start_indexing(
        self,
        cloud: str = "aws", 
        region: str = "us-east-1", 
        metric: str = "cosine",
        dimension: int = 768 
        ) -> None: 
        """
        Create the desired Pinecone indices if they have not already been made. 

        Args:
            cloud: the cloud platform that is to be used. Defaults to AWS, as the free tier of Pinecone only supports AWS
            region: The AWS region we want to use. The free tier only supports the "us-east-1" region.
            metric: the similarity metric that we intend to use. Defaults to cosine similarity.
            dimension: The dimension of the index (or indices) that we will be creating.
        """
        spec = ServerlessSpec(cloud=cloud, region=region)
        
        try:
            existing_indexes = [
                index["name"] for index in self.store.list_indexes()
            ]

            for name in self.index_names:

                if name not in existing_indexes:
                    logger.info(f"Creating a pinecone index called {name}")
                    self.store.create_index(name=name, dimension=dimension, metric=metric, spec=spec)
                else:
                    logger.warning(f"There is already an index called {name}")

                # Wait till the index is ready
                while not self.store.describe_index(name=name).status["ready"]:
                    time.sleep(1)

        except Exception as error:
            logger.error(error)

    def get_index(self, book_file_name: str | None) -> Index:
        """
        Return an index object associated with a specific book, or with all books (for the single-index setup)
        If the index associated with a specific book is intended, provide the book's file name. Otherwise, the
        book's file_name should be None. 
        
        Args:
            book_file_name: the file_name attribute of the book in question (only when the multi_index attribute
                            is true). 

        Returns:
           Index: the index object of the desired index. 

        Raises:
            Exception: raised when a book's file name is not provided even though the multi_index approach has 
                       been specified.
        """
        if self.multi_index and isinstance(book_file_name, str):
            name =  book_file_name.replace("_", "-")
            return self.store.Index(name=name)

        elif self.multi_index and book_file_name == None:
            raise Exception("You must specify a book if you're dealing with a mult-index setup")
        
        else: 
            return self.store.Index(name="nkrumah")

    def push_vectors(self) -> None:
        """
        Make embeddings of the chunks of text, and push them to Pinecone.
        """
        embedding_model = get_embedding_model()
        index_names_and_their_books = {index_name: book for index_name, book in zip(self.index_names, self.books)}

        for index_name in index_names_and_their_books.keys():
            book = index_names_and_their_books[index_name]
            documents = read_books(books=[book])
            chunks = split_documents_into_chunks(documents=documents)

            logger.info(f'Pushing chunks of text and their embeddings from "{book.title}"')
            _ = PineconeVectorStore.from_texts(index_name=index_name, texts=chunks, embedding=embedding_model)


if __name__ == "__main__": 
    parser = ArgumentParser()
    _ = parser.add_argument("--pinecone", action="store_true")
    _ = parser.add_argument("--chroma", action="store_true")
    _ = parser.add_argument("--chunk", action="store_true")
    _ = parser.add_argument("--multi_index", action="store_true")
    args = parser.parse_args()
   
    if args.pinecone:
        api = PineconeAPI(multi_index=args.multi_index)
        api.start_indexing()
        _ = api.push_vectors() 

    else:
        api = ChromaAPI()
        ids = api.add_documents(chunk=args.chunk)

