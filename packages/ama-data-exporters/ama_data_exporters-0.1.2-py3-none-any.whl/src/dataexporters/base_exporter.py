from abc import ABC, abstractmethod
from typing import List

from src.dataloaders import BaseLoader
from src.datatypes import Document, DocumentChunk

class BaseExporter(ABC):
    """Interface for Data Exporter.
    """

    @abstractmethod
    def get_text_embedding(self, content: str, **kwargs):
        """Get embedding for the content"""
        raise NotImplementedError
    
    @abstractmethod
    def sync_data(self, docs_metadata: List[Document], **kwargs):
        """Remove all documents that are not accessible with 
        current user permissions
        """
        raise NotImplementedError

    @abstractmethod
    def remove_chunks(self, docs_metadata: List[DocumentChunk], **kwargs):
        """Remove chunks from vector store
        """
        raise NotImplementedError
    
    @abstractmethod
    def insert_chunks(self, docs_metadata: List[DocumentChunk], **kwargs):
        """Insert chunks into vector store
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_document_summary(self, doc: Document, **kwargs) -> Document:
        """Get summary of the document
        """
        raise NotImplementedError

    @abstractmethod
    def process_documents(self, docs: List[Document], **kwargs):
        """Process documents
        """
        raise NotImplementedError

    @abstractmethod
    async def process_single_dataloaders(self, dataloader: BaseLoader, **kwargs):
        """Process a single dataloaders
        """
        raise NotImplementedError

    async def process_dataloaders(self, dataloaders: List[BaseLoader], **kwargs):
        """Process dataloaders
        """
        raise NotImplementedError
