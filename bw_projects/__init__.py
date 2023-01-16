"""bw_projects."""
from bw_projects.utils import get_version_tuple
from bw_projects.configuration import config
from bw_projects.project import projects, ProjectDataset
from bw_projects.sqlite import SubstitutableDatabase

__all__ = (
    "__version__",
    # Add functions and variables you want exposed in `bw_projects.`
    # namespace here
    "config",
    "projects",
    "ProjectDataset",
    "SubstitutableDatabase",
)

__version__ = get_version_tuple()
