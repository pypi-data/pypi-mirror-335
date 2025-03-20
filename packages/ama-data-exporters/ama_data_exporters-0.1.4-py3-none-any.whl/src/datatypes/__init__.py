from __future__ import annotations
from datetime import datetime
import pytz
import typing as t
import uuid

from dataclasses import dataclass, field

tz = pytz.timezone("Europe/Berlin")

@dataclass
class DocumentChunk:
    order_index: int
    content: str
    document_id: uuid.UUID
    document_type: str
    document_extension: str
    document_origin: str
    document_title: str
    document_source_id: str
    document_source_space: str
    document_source_link: t.Optional[str] = None
    document_source_last_modified: t.Optional[str] = None
    document_source_labels: t.Optional[t.List[str]] = field(default_factory=list)
    document_metadata: t.Optional[t.Dict[str, str]] = field(default_factory=dict)
    document_summary: t.Optional[str] = ""
    created_at: t.Optional[str] = field(default_factory=lambda: str(datetime.now(tz).isoformat()))
    id: t.Optional[uuid.UUID] = field(default_factory=lambda: str(uuid.uuid4()))
    document_cluster: t.Optional[str] = ""
    

@dataclass
class Document:
    content: str
    type: str
    extension: str
    origin: str
    title: str
    source_id: str
    source_space: str
    source_link: t.Optional[str] = None
    source_download_link: t.Optional[str] = None
    source_last_modified: t.Optional[str] = None
    source_labels: t.Optional[t.List[str]] = field(default_factory=list)
    metadata: t.Optional[t.Dict[str, str]] = field(default_factory=dict)
    summary: t.Optional[str] = ""
    created_at: t.Optional[str] = field(default_factory=lambda: str(datetime.now(tz).isoformat()))
    id: t.Optional[uuid.UUID] = field(default_factory=lambda: str(uuid.uuid4()))
    cluster: t.Optional[str] = ""
