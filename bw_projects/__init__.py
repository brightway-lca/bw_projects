"""bw_projects."""
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

__version__ = "2.1.0"
