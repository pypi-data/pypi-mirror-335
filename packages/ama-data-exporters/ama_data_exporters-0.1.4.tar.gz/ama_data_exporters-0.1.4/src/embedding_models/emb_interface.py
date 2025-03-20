from abc import ABC, abstractmethod

class EmbeddingInterface(ABC):
    @property
    @abstractmethod
    def dimension(self):
        """Returns dimension of the embedding model"""
        raise NotImplementedError
    
    @property
    @abstractmethod
    def name(self):
        """Returns name of the embedding model"""
        raise NotImplementedError

    @abstractmethod
    def get_embeddings(self, **kwargs):
        """Returns vector embeddings"""
        raise NotImplementedError
