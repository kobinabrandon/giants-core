import torch
from argparse import ArgumentParser
from sentence_transformers import SentenceTransformer

from src.config import config
from src.indexing import PineconeAPI


def query_embeddings(query: str, multi_index: bool, book_file_name: str | None, top_k: int) -> list[dict]:
   
    api = PineconeAPI(multi_index=multi_index)
    index = api.get_index(book_file_name=book_file_name)

    device = "gpu" if torch.cuda.is_available() else "cpu"
    model = SentenceTransformer(config.sentence_transformer_name, device=device)

    query_vector = model.encode(query).tolist()
    xc = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    
    return xc["matches"]


if __name__ == "__main__":

    parser = ArgumentParser()
    _ = parser.add_argument("--multi_index", action="store_true")
    _ = parser.add_argument("-o", "--book_file_name", nargs="?")
    _ = parser.add_argument("--top_k", type=int)
    args = parser.parse_args()    

    results = query_embeddings(
            query="What happened on the way to China?", 
            multi_index=args.multi_index, 
            book_file_name=args.book_file_name,
            top_k=args.top_k
    )

    breakpoint()
