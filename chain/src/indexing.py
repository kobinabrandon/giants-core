import time 
from loguru import logger 
from argparse import ArgumentParser, BooleanOptionalAction

from pinecone import Index, Pinecone, ServerlessSpec

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

from config import config
from chunking import split_text_into_chunks 
from general.books import Book, neo_colonialism, dark_days, africa_unite

    
def choose_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=config.sentence_transformer_name)


class PineconeAPI:
    def __init__(self, books: list[Book], single_index: bool = False, api_key: str = config.pinecone_api_key) -> None:
        self.api_key = api_key 
        self.books = books
        self.single_index = single_index
        self.index_names = ["nkrumah"] if self.single_index else [book.file_name for book in self.books]         
        self.pc =  Pinecone(api=api_key)
    
    def create_index(
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
        
        for name in 
            logger.info(f"Creating a pinecone index called {name} and pushing data to it")
            self.pc.create_index(name=name, dimension=dimension, metric=metric, spec=spec)
        
            # Wait till the index is ready
            while not self.pc.describe_index(name=name).status["ready"]:
                time.sleep(1)

    def get_index(self) -> Index:
       
        existing_indexes = [
            index["name"] for index in self.pc.list_indexes()
        ]
        
        for name in self.index_names:

            if name not in existing_indexes:
                self.create_index()
          
       
    @staticmethod
    def push_vectors(chunks_of_text: list[str], embedding_model: HuggingFaceEmbeddings, index_name: str = config.pinecone_index) -> PineconeVectorStore:
        return PineconeVectorStore.from_texts(texts=chunks_of_text, embedding=embedding_model, index_name=index_name)
        
  
if __name__ == "__main__": 
    parser = ArgumentParser()
    _ = parser.add_argument("books", nargs="+", type=str)
    _ = parser.add_argument("single_index", action="store_true")
    args = parser.parse_args()
    
    chunks_of_text = split_text_into_chunks(books=args.books)
    embedding_model = choose_embedding_model()

    api = PineconeAPI(single_index=args.single_index, books=args.books)
    _ = api.get_index()
    _ = api.push_vectors(chunks_of_text=chunks_of_text, embedding_model=embedding_model) 
     
