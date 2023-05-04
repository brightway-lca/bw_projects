import os
import shutil
from collections.abc import Iterable
from pathlib import Path

import appdirs
from peewee import DoesNotExist, Model, TextField
from playhouse.sqlite_ext import JSONField
from slugify import slugify

from bw_projects.errors import NoActiveProjectError
from bw_projects.sqlite import SubstitutableDatabase


class ProjectDataset(Model):
    name = TextField(index=True, unique=True)
    attributes = JSONField()


class ProjectManager(Iterable):
    _basic_directories = (
        "backups",
        "intermediate",
        "lci",
        "processed",
    )

    def __init__(self, folder: str = None):
        self._base_data_dir, self._base_logs_dir = self._get_base_directories(folder)
        self._create_base_directories()
        self.db = SubstitutableDatabase(
            f"{self._base_data_dir}/projects.db", [ProjectDataset]
        )
        self._project_name = None

    def __iter__(self):
        for project_ds in ProjectDataset.select():
            yield project_ds

    def __contains__(self, name: str) -> bool:
        return ProjectDataset.select().where(ProjectDataset.name == name).count() > 0

    def __len__(self) -> int:
        return ProjectDataset.select().count()

    def __repr__(self) -> str:
        if len(self) > 20:
            return (
                "Brightway2 projects manager with {} objects, including:"
                "{}\nUse `sorted(projects)` to get full list, "
                "`projects.report()` to get\n\ta report on all projects."
            ).format(
                len(self),
                "".join(
                    ["\n\t{}".format(x) for x in sorted([x.name for x in self])[:10]]
                ),
            )
        else:
            return (
                "Brightway2 projects manager with {} objects:{}"
                "\nUse `projects.report()` to get a report on all projects."
            ).format(
                len(self),
                "".join(["\n\t{}".format(x) for x in sorted([x.name for x in self])]),
            )

    # ---- Internal functions for managing projects
    def _get_base_directories(self, folder: str = None) -> tuple[Path, Path]:
        if folder:
            envvar = folder
        elif os.getenv("BRIGHTWAY_DIR"):
            envvar = os.getenv("BRIGHTWAY_DIR")
        else:
            label = "Brightway3"
            data_dir = Path(appdirs.user_data_dir(label, "pylca"))
            logs_dir = Path(appdirs.user_log_dir(label, "pylca"))
            return data_dir, logs_dir
        os.makedirs(envvar, exist_ok=True)
        logs_dir = f"{envvar}/logs"
        os.makedirs(logs_dir, exist_ok=True)
        return envvar, logs_dir

    def _create_base_directories(self) -> None:
        os.makedirs(self._base_data_dir, exist_ok=True)
        os.makedirs(self._base_logs_dir, exist_ok=True)

    @property
    def current(self) -> str:
        return self._project_name

    def set_current(self, name, **kwargs) -> None:
        self._project_name = str(name)

        # Need to allow writes when creating a new project
        # for new metadata stores
        self.create_project(name, **kwargs)

    # Public API
    @property
    def dir(self) -> Path:
        if self.current:
            return Path(self._base_data_dir) / slugify(self.current)
        else:
            raise NoActiveProjectError

    @property
    def logs_dir(self) -> Path:
        if self.current:
            return Path(self._base_logs_dir) / slugify(self.current)
        else:
            raise NoActiveProjectError

    @property
    def output_dir(self) -> Path:
        """Get directory for output files.

        Uses environment variable ``BRIGHTWAY_OUTPUT_DIR``;
        ``preferences['output_dir']``; or directory ``output``
        in current project.

        Returns output directory path.

        """
        ep = os.getenv("BRIGHTWAY_OUTPUT_DIR")
        if ep and os.path.exists(ep):
            return ep
        return self.request_directory("output")

    def create_project(self, name: str = None, **kwargs) -> None:
        name = name or self.current

        try:
            self.dataset = ProjectDataset.get(ProjectDataset.name == name)
        except DoesNotExist:
            self.dataset = ProjectDataset.create(attributes=kwargs, name=name)
        os.makedirs(self.dir, exist_ok=True)
        for dir_name in self._basic_directories:
            os.makedirs(self.dir / dir_name, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)

    def request_directory(self, name: str) -> Path:
        """Return the absolute path to the subdirectory ``dirname``,
        creating it if necessary.

        Returns ``False`` if directory can't be created."""
        fp = self.dir / str(name)
        os.makedirs(fp, exist_ok=True)
        if not fp.is_dir():
            return False
        return fp

    def delete_project(self, name: str = None, delete_dir: bool = False) -> str:
        """Delete project ``name``, or the current project.

        ``name`` is the project to delete. If ``name`` is not provided,
        delete the current project.

        By default, the underlying project directory is not deleted;
        only the project name is removed from the list of active projects.
        If ``delete_dir`` is ``True``, then also delete the project directory.

        If deleting the current project, this function sets the current directory
        to ``default`` if it exists, or to a random project.

        Returns the current project."""
        if self._project_name is None:
            raise NoActiveProjectError

        victim = name or self.current
        if victim not in self:
            raise ValueError("{} is not a project".format(victim))

        ProjectDataset.delete().where(ProjectDataset.name == victim).execute()

        if delete_dir:
            dir_path = self._base_data_dir / slugify(victim)
            assert dir_path.is_dir(), "Can't find project directory"
            shutil.rmtree(dir_path)

        if name is None or name == self.current:
            try:
                self.set_current(next(iter(self)).name)
            except StopIteration:
                self._project_name = None
        return self.current

    def purge_deleted_directories(self) -> int:
        """Delete project directories for projects which are no longer registered.

        Returns number of directories deleted."""
        registered = {slugify(obj.name) for obj in self}
        bad_directories = [
            self._base_data_dir / dirname
            for dirname in os.listdir(self._base_data_dir)
            if (self._base_data_dir / dirname).is_dir() and dirname not in registered
        ]

        for fp in bad_directories:
            shutil.rmtree(fp)

        return len(bad_directories)


projects = ProjectManager()
