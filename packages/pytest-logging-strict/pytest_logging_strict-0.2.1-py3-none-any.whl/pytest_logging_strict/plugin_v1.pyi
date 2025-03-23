import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

# https://github.com/pytest-dev/pytest-xdist/issues/1121
from xdist.workermanage import WorkerController  # type: ignore

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

@dataclass(frozen=True)  # compat python < 3.10 (kw_only=True)
class RegistryPackageNameStash:
    yaml_package_name: str | None

    @classmethod
    def from_serialized(cls, serialized: Any | None) -> Self: ...
    def serialized(self) -> str | None: ...

@dataclass(frozen=True)  # compat python < 3.10 (kw_only=True)
class RegistryPathStash:
    registry_logging_strict_config_yaml_path: Path | None
    @classmethod
    def from_serialized(cls, serialized: Any | None) -> Self: ...
    def remove(self) -> None: ...
    def serialized(self) -> str | None: ...

stash_key: dict[
    str, pytest.StashKey[RegistryPackageNameStash] | pytest.StashKey[RegistryPathStash]
]

def _is_xdist(config: pytest.Config) -> Any | None: ...
def _xdist_worker(config: pytest.Config) -> dict[str, Any]: ...
def _xdist_workerinput(node: WorkerController | pytest.Config) -> Any: ...

class LoggingStrictXdistControllerPlugin:
    def pytest_configure_node(self, node: WorkerController) -> None: ...

def pytest_configure(config: pytest.Config) -> None: ...

class LoggingStrictControllerPlugin:
    def pytest_unconfigure(self, config: pytest.Config) -> None: ...

def pytest_addoption(parser: pytest.Parser) -> None: ...
