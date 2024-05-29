from sentence_transformers import SentenceTransformer
from langchain.embeddings.base import Embeddings


class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_query(self, query: str):
        return self.model.encode(query, convert_to_tensor=True).tolist()

    def embed_documents(self, documents: list):
        return self.model.encode(documents, convert_to_tensor=True).tolist()
