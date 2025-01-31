import chromadb
from langchain_huggingface import HuggingFaceEmbeddings 

from src.generation.appendix import get_context
from src.indexing.embeddings import ChromaAPI
from src.indexing.embeddings import get_embedding_model
from src.setup.paths import make_data_directories, set_paths


class EmbeddingBased:
    def __init__(self, vector_db_name: str, collection_name: str = "chat_memory") -> None:
        make_data_directories()

        self.vector_db_name: str = vector_db_name.lower()
        self.collection_name: str = collection_name
        self.embedding_model: HuggingFaceEmbeddings = get_embedding_model()

        # self.client = self.add_chroma_db() 
        # self.collection = self.client.get_or_create_collection(name=collection_name)

    # def add_chroma_db(self): 
    #     assert ("chroma" == self.vector_db_name) or ("pinecone" == self.vector_db_name); "Chroma and Pinecone are the only supported vector DBs." 
    #     memory_path = set_paths()["chroma_memory"]
    #     return chromadb.PersistentClient(path=str(memory_path))
    #
    def store_interaction(self, user_message: str, bot_response: list[str] | str) -> None:

        text = f"User: {user_message} | Bot: {bot_response}"
        chroma = ChromaAPI(is_memory=True)
        chroma.embed_memory(text=text)

    def retrieve_interaction(self, query: str) -> str:
        return get_context(question=query, is_memory=True)
       

# I have built an application that allows the user to learn about an important historical figure (H.E. Dr Kwame Nkrumah). The LLM uses context from his written works to enhance its answers, in a process known as Retrieval Augmented Generation (RAG)
