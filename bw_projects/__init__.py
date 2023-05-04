"""bw_projects."""
import importlib.metadata
from typing import Union

from bw_projects.project import ProjectDataset, projects
from bw_projects.sqlite import SubstitutableDatabase

__all__ = (
    "__version__",
    "projects",
    "ProjectDataset",
    "SubstitutableDatabase",
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
