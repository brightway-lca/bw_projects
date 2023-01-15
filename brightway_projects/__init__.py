"""brightway_projects."""
from brightway_projects.utils import get_version_tuple
from brightway_projects.configuration import config
from brightway_projects.project import projects, ProjectDataset
from brightway_projects.sqlite import SubstitutableDatabase

__all__ = (
    "__version__",
    # Add functions and variables you want exposed in `brightway_projects.`
    # namespace here
    "config",
    "projects",
    "ProjectDataset",
    "SubstitutableDatabase",
)

__version__ = get_version_tuple()
