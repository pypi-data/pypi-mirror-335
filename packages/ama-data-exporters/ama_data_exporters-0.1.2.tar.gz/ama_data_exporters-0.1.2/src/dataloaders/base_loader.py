from abc import ABC, abstractmethod
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.datatypes import Document, DocumentChunk

class BaseLoader(ABC):
    """Interface for Document Loader.

    Implementations should implement the lazy-loading method using generators
    to avoid loading all Documents into memory at once.
    """

    @abstractmethod
    def get_documents_metadata(self, modified_after=None, **kwargs) -> List[Document]:
        """Get metadata for documents without loading them"""
        raise NotImplementedError
    
    def load_documents(self, docs_metadata: List[Document], **kwargs) -> List[Document]:
        """Load Documents"""
        return list(self.lazy_load_documents(docs_metadata))
    
    @abstractmethod
    def lazy_load_documents(self, docs_metadata: List[Document], **kwargs) -> List[Document]:
        """Lazy Load Documents"""
        raise NotImplementedError

    def make_chunks(self, docs: List[Document], **kwargs) -> List[DocumentChunk]:
        """Make Chunks. Default Chunking Strategy"""
        content_chunks = []
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=0,
            length_function=len,
            add_start_index=False,
            strip_whitespace=True,
        )

        for document in docs:
            if type(document) is Document and document.type == "Document":
                doc_id = document.id
                doc_type = document.type
                doc_ext = document.extension
                doc_title = document.title
                doc_metadata = document.metadata
                doc_summary = document.summary
                source_labels = document.source_labels
                source_last_modified = document.source_last_modified
                source_link = document.source_link
                source_id = document.source_id
                source_origin = document.origin
                source_space = document.source_space
                print(f"Going to create chunks of the following {source_origin} document:"
                      f" id={source_id}, title={doc_title}, lastModified={source_last_modified}")

                chunks = text_splitter.split_text(document.content)
                for idx, chunk in enumerate(chunks):
                    # Add title in first chunks
                    if idx == 0:
                        chunk = doc_title + "\n" + chunk
                    content_chunks.append(
                        DocumentChunk(order_index=idx,
                                content=chunk,
                                document_id=doc_id,
                                document_type=doc_type,
                                document_extension=doc_ext,
                                document_origin=source_origin,
                                document_title=doc_title,
                                document_cluster="",
                                document_source_id=source_id,
                                document_source_space=source_space,
                                document_source_link=source_link,
                                document_source_last_modified=source_last_modified,
                                document_source_labels=source_labels,
                                document_metadata=doc_metadata,
                                document_summary=doc_summary)
                    )

        return content_chunks