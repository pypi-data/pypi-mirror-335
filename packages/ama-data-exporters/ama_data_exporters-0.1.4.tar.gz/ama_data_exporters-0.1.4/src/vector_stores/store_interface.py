from abc import ABC, abstractmethod

class VectorStoreInterface(ABC):
    @property
    @abstractmethod
    def name(self):
        """Returns name of the vector store"""
        raise NotImplementedError

    @abstractmethod
    def upsert(self, **kwargs):
        """Insert/update data into the vector store"""
        raise NotImplementedError
    
    @abstractmethod
    def retrieve(self, **kwargs):
        """Retrieve data from the vector store"""
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, **kwargs):
        """Delete data from the vector store"""
        raise NotImplementedError

    @abstractmethod
    def ann_search(self, k, **kwargs):
        """Search k nearest neighbors"""
        raise NotImplementedError
