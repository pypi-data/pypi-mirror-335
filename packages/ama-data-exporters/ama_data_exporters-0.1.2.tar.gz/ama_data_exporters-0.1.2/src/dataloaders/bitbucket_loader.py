from typing import List

from .base_loader import BaseLoader
from src.datatypes import Document

class BitbucketLoader(BaseLoader):
    def __init__(self):
        super().__init__()

    def get_documents_metadata(self, modified_after=None, **kwargs) -> List[Document]:
        """Get metadata for documents without loading them"""
        raise NotImplementedError
    
    def lazy_load_documents(self, docs_metadata: List[Document], **kwargs) -> List[Document]:
        """Lazy Load Documents"""
        raise NotImplementedError
