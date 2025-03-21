from __future__ import annotations

import ast
import contextlib
from pathlib import Path
from typing import Any, cast

from poetry.core.utils.helpers import module_name

with contextlib.suppress(ImportError):
    from poetry.console.commands.build import BuildHandler

    _origin_requires_isolated_build = BuildHandler._requires_isolated_build

    def _requires_isolated_build(self: BuildHandler) -> bool:
        if not _origin_requires_isolated_build(self):
            return False
        # patch poetry to avoid using isolated_builder for this plugin
        return not any(
            dep.name.replace("_", "-") == "poetry-plugin-version"
            for dep in self.poetry.build_system_dependencies
        )

    BuildHandler._requires_isolated_build = _requires_isolated_build  # type:ignore


def get_version_from_file(init_path: Path) -> str | None:
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for el in tree.body:
        if isinstance(el, ast.Assign) and len(el.targets) == 1:
            target = el.targets[0]
            if isinstance(target, ast.Name) and target.id == "__version__":
                if isinstance(value_node := el.value, ast.Constant):
                    version = value_node.value
                elif isinstance(value_node, ast.Str):
                    version = value_node.s
                else:  # pragma: nocover
                    # This is actually covered by tests, but can't be
                    # reported by Coverage
                    # Ref: https://github.com/nedbat/coveragepy/issues/198
                    continue
                return cast(str, version)
    return None


def find_version_file(package_name: str, filename: str, pyproject_path: Path) -> Path:
    init_path = Path(package_name) / filename
    if init_path.is_file():
        return init_path
    abs_init_path = pyproject_path.parent / init_path
    if abs_init_path.is_file():
        return abs_init_path
    src_init = Path("src") / init_path
    if src_init.is_file():
        return src_init
    abs_src_init = pyproject_path.parent / "src" / init_path
    if abs_src_init.is_file():
        return abs_src_init
    raise FileNotFoundError(
        f"{filename} file not found at {abs_init_path} cannot extract dynamic version"
    )


def parse_package_name(
    name: str, poetry_config: dict[str, Any], pyproject_data: dict[str, Any]
) -> str:
    if (packages := poetry_config.get("packages")) or (
        packages := pyproject_data.get("project", {}).get("packages", [])
    ):
        if len(packages) > 1:
            raise ValueError(
                "More than one package set, cannot extract dynamic version"
            )
        package_name = cast(str, packages[0]["include"])
    else:
        package_name = module_name(name)
    return package_name
