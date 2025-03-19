from __future__ import annotations

import functools
from types import ModuleType
from typing import TYPE_CHECKING, Any, Callable

from .states import (
    _get_and_apply_version,
    _get_pyproject_path_from_poetry,
    _state,
)

if TYPE_CHECKING:
    from poetry.core.factory import Factory
    from poetry.core.poetry import Poetry


def _patch_poetry_create(factory_mod: ModuleType) -> None:
    from poetry.core.constraints.version import Version as PoetryVersion

    original_poetry_create: Callable[..., Poetry] = factory_mod.Factory.create_poetry

    @functools.wraps(original_poetry_create)
    def alt_poetry_create(cls: Factory, *args: Any, **kwargs: Any) -> Poetry:
        instance: Poetry = original_poetry_create(cls, *args, **kwargs)

        if not _state.cli_mode:
            name = _get_and_apply_version(
                pyproject_path=_get_pyproject_path_from_poetry(instance.pyproject),
            )
            if name and (version := _state.projects[name].version):
                instance._package._version = PoetryVersion.parse(version)
                instance._package._pretty_version = version  # type:ignore

        return instance

    factory_mod.Factory.create_poetry = alt_poetry_create


def _apply_patches() -> None:
    if not _state.patched_core_poetry_create:
        from poetry.core import factory as factory_mod

        _patch_poetry_create(factory_mod)
        _state.patched_core_poetry_create = True


def activate() -> None:
    _apply_patches()
