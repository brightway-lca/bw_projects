"""bw_projects."""
import importlib.metadata
from typing import Union

from .config import Configuration
from .core import ProjectsManager
from .errors import BWProjectsException, ProjectExistsError
from .model import Project

__all__ = (
    "__version__",
    "BWProjectsException",
    "Configuration",
    "Project",
    "ProjectExistsError",
    "ProjectsManager",
)


def get_version_tuple() -> tuple:
    """Returns version as (major, minor, micro)."""

    def as_integer(version: str) -> Union[int, str]:
        """Tries parsing version else returns as is."""
        try:
            return int(version)
        except ValueError:  # pragma: no cover
            return version  # pragma: no cover

    return tuple(
        as_integer(v)
        for v in importlib.metadata.version("bw_projects").strip().split(".")
    )


__version__ = get_version_tuple()
