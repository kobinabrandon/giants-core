import time 
from loguru import logger 
from argparse import ArgumentParser, BooleanOptionalAction

from pinecone import  Pinecone, ServerlessSpec

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

from config import config
from chunking import split_text_into_chunks 
from general.books import Book, neo_colonialism, dark_days, africa_unite
    

class PineconeAPI:
    def __init__(self, multi_index: bool = False, api_key: str = config.pinecone_api_key) -> None:
        self.api_key = api_key 
        self.multi_index = multi_index 
        self.pc =  Pinecone(api=api_key)
        self.books = [neo_colonialism, dark_days, africa_unite]

        # Pinecone does not allow underscores in index names 
        self.index_names = ["nkrumah"] if not self.multi_index else [book.file_name.replace("_", "-") for book in self.books]         

    @staticmethod
    def choose_embedding_model() -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(model_name=config.sentence_transformer_name)

    def start_indexing(
        self,
        cloud: str = "aws", 
        region: str = "us-east-1", 
        metric: str = "cosine",
        dimension: int = config.vector_dim
        ) -> None: 
        """
        The free tier of Pinecone only comes with AWS, and only the "us-east-1" region
        """
        spec = ServerlessSpec(cloud=cloud, region=region)
        
        try:
            existing_indexes = [
                index["name"] for index in self.pc.list_indexes()
            ]

            for name in self.index_names:

                if name not in existing_indexes:
                    logger.info(f"Creating a pinecone index called {name} and pushing data to it")
                    self.pc.create_index(name=name, dimension=dimension, metric=metric, spec=spec)
                else:
                    logger.warning(f"There is already an index called {name}")

                # Wait till the index is ready
                while not self.pc.describe_index(name=name).status["ready"]:
                    time.sleep(1)

        except Exception as error:
            logger.error(error)
       
    def push_vectors(self) -> None:

        embedding_model = self.choose_embedding_model()
        index_names_and_their_books = {index_name: book for index_name, book in zip(self.index_names, self.books)}

        for index_name in index_names_and_their_books.keys():
            
            book = index_names_and_their_books[index_name]
            chunks = split_text_into_chunks(books=[book])
            
            logger.info(f'Pushing chunks of text and their embeddings from "{book.title}"')
            _ = PineconeVectorStore.from_texts(index_name=index_name, texts=chunks, embedding=embedding_model)


if __name__ == "__main__": 

    parser = ArgumentParser()
    _ = parser.add_argument("--multi_index", action="store_true")
    args = parser.parse_args()
    
    api = PineconeAPI(multi_index=args.multi_index)
    api.start_indexing()
    _ = api.push_vectors() 

