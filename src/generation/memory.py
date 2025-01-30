import uuid
import chromadb
from langchain_huggingface import HuggingFaceEmbeddings 

from src.indexing.embeddings import get_embedding_model
from src.setup.paths import make_data_directories, set_paths


class EmbeddingBased:
    def __init__(self, vector_db_name: str, collection_name: str = "chat_memory") -> None:
        make_data_directories()

        self.client = self.add_chroma_db() 
        self.collection_name: str = collection_name
        self.vector_db_name: str = vector_db_name.lower()
        self.embedding_model: HuggingFaceEmbeddings = get_embedding_model()
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_chroma_db(self): 
        assert "chroma" in self.vector_db_name 
        memory_path = set_paths()["chroma_memory"]
        return chromadb.PersistentClient(path=str(memory_path))

    def store_interaction(self, user_message: str, bot_response: str) -> None:

        text = f"User: {user_message} | Bot: {bot_response}"
        embedding = self.embedding_model.encode(text).tolist()
        self.collection.add(
            ids=str(uuid.uuid4()),
            embeddings=[embedding],
            metadatas=[{"text": text}]
        )

    def retrieve_interaction(self, query: str, top_k: int):

        query_vector = self,embedding_model.encode(query).tolist()
        result_of_query = self.collection.query(query_embeddings=[query_vector], n_results=top_k)
        
        return [
            doc["text"] for doc in result_of_query["metatdatas"][0]
        ]
