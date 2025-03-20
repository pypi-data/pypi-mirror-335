from pathlib import Path
from typing import List, Iterator, Optional
import uuid
import datetime
import pytz
from tqdm import tqdm
from markitdown import MarkItDown
from .base_loader import BaseLoader
from src.datatypes import Document

class DirectoryLoader(BaseLoader):
    def __init__(self, directory: str, include_extensions: Optional[List[str]] = [".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt"], exclude_paths: Optional[List[str]] = []):
        """
        Initializes the DirectoryLoader with the given parameters.
        
        directory: Path to the directory containing documents.
        include_extensions: List of file extensions to load (default:[".pdf", ".docx", ".pptx", ".xlsx", ".md", ".txt"]).
        exclude_paths: List of glob patterns to exclude specific files or directories (default: []).
        """
        super().__init__()
        self.directory = Path(directory).resolve()
        self.include_extensions = include_extensions
        self.exclude_paths = exclude_paths
        self.md_converter = MarkItDown()
    
    def get_documents_metadata(self, modified_after: Optional[str] = None, **kwargs) -> List[Document]:
        """
        Retrieves metadata for documents without loading full content.
        
        modified_after: Timestamp (ISO 8601) to filter recently modified files.
        Returns a list of Document metadata objects.
        """
        documents = []
        valid_files = list(self._get_valid_files())
        
        berlin_tz = pytz.timezone("Europe/Berlin")
        modified_after_dt = None
        if modified_after:
            modified_after_dt = datetime.datetime.fromisoformat(modified_after).astimezone(berlin_tz)
        
        for file in tqdm(valid_files, desc="Retrieving document metadata"):
            stat = file.stat()
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime, tz=berlin_tz).isoformat()
            
            if modified_after_dt and datetime.datetime.fromtimestamp(stat.st_mtime, tz=berlin_tz) < modified_after_dt:
                continue
            
            documents.append(Document(
                content="",  # Content will be loaded lazily
                type="Document",  # Type Document for pdf, docx, pptx txt, xlsx 
                extension=file.suffix,
                origin=str(self.directory),  # Ensure origin is the directory
                title=file.stem,
                source_id=str(uuid.uuid4()),
                source_space=str(file.parent),
                source_last_modified=modified_time,  # Now in ISO 8601 format
                source_download_link=str(file.resolve()),  # Save file path
            ))
        return documents
    
    def lazy_load_documents(self, docs_metadata: List[Document], **kwargs) -> Iterator[Document]:
        """
        Lazily loads documents and converts content to markdown.
        
        docs_metadata: List of document metadata to load content for.
        Returns an iterator of fully loaded Document objects.
        """
        for doc in tqdm(docs_metadata, desc="Loading documents"):
            file_path = Path(doc.source_download_link)
            markdown_content = self._convert_to_markdown(file_path)
            if markdown_content:
                doc.content = markdown_content
                yield doc
    
    def _get_valid_files(self) -> List[Path]:
        """
        Retrieves valid files from the directory while applying exclusions.
        """
        all_files = list(self.directory.rglob("*"))
        valid_files = []
        for file in all_files:
            if not file.is_file():
                continue
            if file.suffix.lower() not in self.include_extensions:
                continue
            if any(file.match(pattern) for pattern in self.exclude_paths):
                continue
            valid_files.append(file)
        return valid_files
    
    def _convert_to_markdown(self, file_path: Path) -> Optional[str]:
        """
        Converts a file's content to markdown based on its extension.
        """
        try:
            if file_path.suffix.lower() in [".txt", ".md"]:
                return file_path.read_text(encoding="utf-8")  # Read as plain text
            elif file_path.suffix.lower() in self.include_extensions:
                result = self.md_converter.convert(str(file_path))  # Convert other formats
                return result.text_content
        except Exception as e:
            print(f"Failed to convert {file_path}: {e}")
        return None
