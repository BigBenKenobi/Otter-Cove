from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SessionRecord:
    id: str
    title: str
    created_at: str
    updated_at: str
    archived: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageRecord:
    id: str
    session_id: str
    role: str
    content: str
    created_at: str
    ordinal: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelRecord:
    id: str
    name: str
    provider: str
    endpoint: str
    enabled: bool
    created_at: str
    updated_at: str
    config: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentRecord:
    id: str
    title: str
    content: str
    mime_type: str
    path: str | None
    source: str
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BrainItemRecord:
    id: str
    kind: str
    title: str
    content: str
    enabled: bool
    confidence: float
    created_at: str
    updated_at: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class NoteRecord:
    id: str
    title: str
    body: str
    archived: bool
    pinned: bool
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskRecord:
    id: str
    title: str
    description: str
    status: str
    due_at: str | None
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GalleryItemRecord:
    id: str
    path: str
    kind: str
    favourite: bool
    created_at: str
    updated_at: str
    metadata: dict[str, Any] = field(default_factory=dict)
