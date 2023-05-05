"""Core functionalities for bw_projects."""
from collections.abc import Iterable
from typing import Dict

from peewee import DoesNotExist

from .config import Configuration
from .errors import ProjectExistsError
from .helpers import DatabaseHelper, FileHelper
from .model import Project


class ProjectsManager(Iterable):
    """Manages projects."""

    def __init__(
        self,
        dir_base: str,
        database_name: str = "projects.db",
        max_repr_len: int = 25,
        config: Configuration = Configuration(),
    ) -> None:
        self.file_helper = FileHelper(dir_base, config)
        self._max_repr_len = max_repr_len
        self._active_project: Project = None
        DatabaseHelper.init_db(self.file_helper.dir_base / database_name)

    def __iter__(self):
        for project in DatabaseHelper.get_projects():
            yield project

    def __contains__(self, name: str) -> bool:
        return DatabaseHelper.project_exists(name)

    def __len__(self) -> int:
        return DatabaseHelper.get_projects_count()

    def __repr__(self) -> str:
        projects = sorted([project.name for project in self])[: self._max_repr_len]
        projects_fmt = "".join([f"\n\t{project}" for project in projects])
        repr_str = (
            f"bw_projects manager with {len(self)} projects, including:{projects_fmt}"
        )
        if len(self) > self._max_repr_len:
            repr_str += (
                "\n\t...\nTo get full list of projects, use `list(ProjectsManager)`."
            )
        return repr_str

    @property
    def active_project(self) -> Project:
        """Returns the active project."""
        return self._active_project

    def activate_project(self, name: str) -> None:
        """Activates the project with the given name."""
        self._active_project = DatabaseHelper.get_project(name)

    def create_project(
        self,
        name: str = None,
        attributes: Dict = None,
        exists_ok: bool = False,
        activate: bool = False,
    ) -> Project:
        """Creates a project with the given name."""
        if attributes is None:
            attributes = {}

        if not DatabaseHelper.project_exists(name):
            self.file_helper.create_project_directory(name, exists_ok)
            project = DatabaseHelper.create_project(name, attributes)
        else:
            if not exists_ok:
                raise ProjectExistsError
            project = DatabaseHelper.get_project(name)

        if activate:
            self.activate_project(name)
        return project

    def delete_project(
        self, name: str, not_exist_ok: bool = True, delete_dir: bool = True
    ) -> None:
        """Deletes the project with the given name."""
        if not DatabaseHelper.project_exists(name):
            if not not_exist_ok:
                raise DoesNotExist
            return

        DatabaseHelper.delete_project(name)
        if delete_dir:
            self.file_helper.delete_project_directory(name)
        if self._active_project.name == name:
            self._active_project = None
