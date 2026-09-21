from __future__ import annotations

import re
import uuid

_KIND_RE = re.compile(r"[^a-z0-9_]+")


def new_id(kind: str) -> str:
    """Return a stable, opaque local identifier with a readable type prefix."""
    prefix = _KIND_RE.sub("_", kind.strip().lower()).strip("_") or "item"
    return f"{prefix}_{uuid.uuid4().hex}"
