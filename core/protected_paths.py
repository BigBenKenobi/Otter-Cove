"""Filesystem-only protection for Otter Cove's active persistence targets.

Export writers use this module before creating a destination directory or a
temporary sibling file.  Callers supply the paths they own (SQLite, sidecars, or
QSettings), keeping the policy reusable by non-Qt services and theme logic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


class ProtectedTargetError(ValueError):
    """Identify an export destination that aliases active application storage."""


def validate_export_target(path: str | Path, protected_paths: Iterable[str | Path]) -> Path:
    """Return a normalized safe target or reject a protected path before mutation.

    ``resolve(strict=False)`` collapses relative paths and symlinked parents even
    when a requested sidecar does not exist.  For existing files, ``samefile``
    additionally catches hard links, which have different normalized names but
    share the active store's inode.  No directory is created by this validation.
    """

    target = Path(path).expanduser().resolve(strict=False)
    protected = [Path(candidate).expanduser().resolve(strict=False) for candidate in protected_paths]
    for candidate in protected:
        if target == candidate:
            raise ProtectedTargetError(f"Export destination is protected active application storage: {target}")
        if target.exists() and candidate.exists():
            try:
                if os.path.samefile(target, candidate):
                    raise ProtectedTargetError(
                        f"Export destination aliases protected active application storage: {target}"
                    )
            except OSError:
                # Identity probing can fail for an inaccessible target; the writer
                # will report that filesystem failure without creating a bypass.
                continue
    return target
