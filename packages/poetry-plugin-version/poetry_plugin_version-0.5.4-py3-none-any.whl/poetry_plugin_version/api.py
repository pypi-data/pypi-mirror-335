from __future__ import annotations

from poetry.core.masonry.api import (
    build_editable,
    build_sdist,
    build_wheel,
    get_requires_for_build_editable,
    get_requires_for_build_sdist,
    get_requires_for_build_wheel,
    prepare_metadata_for_build_editable,
    prepare_metadata_for_build_wheel,
)

from . import patch

patch.activate()

__all__ = (
    "build_sdist",
    "build_wheel",
    "get_requires_for_build_sdist",
    "get_requires_for_build_wheel",
    "prepare_metadata_for_build_wheel",
    "build_editable",
    "get_requires_for_build_editable",
    "prepare_metadata_for_build_editable",
)
