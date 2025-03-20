import requests
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import TextSplitter
from src.embedding_models.emb_interface import EmbeddingInterface

class MultilingualE5(EmbeddingInterface):
    def __init__(self, name: str, dim: int, url: str) -> None:
        self._name = name
        self._dim = dim
        self._url = url

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
        
        res = requests.post(self._url, json={"inputs": input})
        if res.status_code == 200:
            return res.json()
        else:
            print(res.json())
            raise ValueError("Error getting response from embedding model")
        

class LangchainMultilingualE5(Embeddings):
    """
    Embedding model class based on langchain embedding base classes
    Required for evaluation with ragas
    """

    def __init__(self, embedder: MultilingualE5, text_splitter: TextSplitter|None=None) -> None:
        self.embedder = embedder

        self.text_splitter = text_splitter

    def embed_query(self, text: str) -> List[float]:
        """Get the embeddings for a query

        Args:
            text (str): Query 

        Returns:
            list[float]: Embeddings
        """
        return self.embed_documents([text])[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Get the embeddings for a list of strings

        Args:
            texts (list[str]): List of strings which be embedded

        Returns:
            list[list[float]]: Embeddings
        """
        rl : list[list[float]] = []
        for text in texts:
            if self.text_splitter is None:
                rl += self._embed_documents([text])
            else:
                rl += self._embed_documents(self.text_splitter.split_text(text))

        return rl

    def _embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Returns vector embeddings"""
        return self.embedder.get_embeddings(texts)


if __name__=="__main__":
    emb = MultilingualE5("a", 1024, "https://embeddings.esolutions.de/embed")
    print(emb.name)
    chunk1 = "what is deeplearning"
    chunk2 = "what is deeplearning"
    res = emb.get_embeddings([chunk1,  chunk2])
    print(len(res))
    emb1 = res[0]
    emb2 = res[1]