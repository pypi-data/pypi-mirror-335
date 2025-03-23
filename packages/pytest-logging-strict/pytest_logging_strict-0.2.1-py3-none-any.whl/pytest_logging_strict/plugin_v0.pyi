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
class LSConfigStash:
    logging_strict_config_yaml_path: Path

    @classmethod
    def from_serialized(cls, serialized: str | Path) -> Self: ...
    def remove(self) -> None: ...
    def serialized(self) -> str: ...

stash_key: dict[str, pytest.StashKey[LSConfigStash]]

class LoggingStrictv0XdistControllerPlugin:
    def pytest_configure_node(self, node: WorkerController) -> None: ...

def _configure(config: pytest.Config) -> None: ...

class LoggingStrictv0ControllerPlugin:
    def pytest_unconfigure(self, config: pytest.Config) -> None: ...
