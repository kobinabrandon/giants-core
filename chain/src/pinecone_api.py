import time 
from loguru import logger 

from pinecone import Pinecone, ServerlessSpec

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone.vectorstores import PineconeVectorStore

from config import config
from chunking import split_text_into_chunks

from general.books import neo_colonialism, dark_days, africa_unite

    
def choose_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=config.sentence_transformer_name)


class PineconeAPI:
    def __init__(self, api_key: str = config.pinecone_api_key) -> None:
        self.api_key = api_key 
        self.pc =  Pinecone(api=api_key)

    def create_index(
        self,
        cloud: str = "aws", 
        region: str = "us-east-1", 
        metric: str = "cosine",
        name: str = config.pinecone_index,
        dimension: int = config.vector_dim
        ) -> None: 
        """
        The free tier of Pinecone only comes with AWS, and only the "us-east-1" region
        """
        spec = ServerlessSpec(cloud=cloud, region=region)
        self.pc.create_index(name=name, dimension=dimension, metric=metric, spec=spec)
            
        while not self.pc.describe_index(name=name).status["ready"]:
            time.sleep(1)

    def get_index(self, name: str):
        
        existing_indexes = [
            index["name"] for index in self.pc.list_indexes()
        ]
        
        if name not in existing_indexes:

            try:
                self.create_index(name=name)
                index = self.pc.Index(name)
                return index

            except Exception as error:
                logger.error(error)

        else:
            return self.pc.Index(name=name) 
    
    @staticmethod
    def push_vectors(chunks_of_text: list[str], embedding_model: HuggingFaceEmbeddings, index_name: str = config.pinecone_index) -> PineconeVectorStore:
        return PineconeVectorStore.from_texts(texts=chunks_of_text, embedding=embedding_model, index_name=index_name)
        
  
if __name__ == "__main__": 

    books = [neo_colonialism, dark_days, africa_unite]
    chunks_of_text = split_text_into_chunks(books=books)
    embedding_model = choose_embedding_model()

    api = PineconeAPI()
    _ = api.push_vectors(chunks_of_text=chunks_of_text, embedding_model=embedding_model) 
     
