from typing import List

from sentence_transformers import SentenceTransformer

from src.embedding_models.emb_interface import EmbeddingInterface

class LocalEmbedding(EmbeddingInterface):
    def __init__(self, name: str, dim: int, **kwargs) -> None:
        """ name should be Sentence-transformer supported
        **kwargs are sentence-transformer model_kwargs
        """
        self._name = name
        self._dim = dim
        self._model = SentenceTransformer(name, model_kwargs={"torch_dtype": "float32", **kwargs})

    @property
    def dimension(self):
        """Returns dimension of the embedding model"""
        return self._dim

    @property
    def name(self):
        """Returns name of the embedding model"""
        return self._name
    
    def get_embeddings(self, input: List[str]):
        """Returns vector embeddings"""
        if not input or len(input)==0:
            raise ValueError("Bad Input!")
        if isinstance(input, str):
            input = [input]
        if not isinstance(input, list):
            raise ValueError(f"Input of type {type(input)} is not supported!")
        
        embeddings = self._model.encode(input)
        return embeddings

if __name__=="__main__":
    inp = ["Hi AMA", "Hi AMA", "Hi AMA", "Hi AMA"]
    emb_model = LocalEmbedding("intfloat/multilingual-e5-large-instruct", dim=1024)
    import time
    a = time.time()
    emb = emb_model.get_embeddings(inp)
    b = time.time()
    print(type(emb), emb.shape, f"{b-a} sec took")
