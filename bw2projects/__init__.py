__all__ = ["config", "projects", "__versions__", "ProjectDataset"]

from .version import version as __version__

from .configuration import config
from .project import projects, ProjectDataset
from .meta import Preferences

preferences = Preferences(projects.dir)
config.metadata.extend(preferences)

config.p = preferences
