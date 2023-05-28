"""Core functionalities for bw_projects."""
from collections.abc import Iterable
from typing import Callable, Dict, List, NoReturn

from peewee import DoesNotExist
from slugify import slugify

from .config import Configuration
from .errors import ProjectExistsError
from .helpers import DatabaseHelper, FileHelper
from .model import Project


class ProjectsManager(Iterable):
    """Manages projects."""

    def __init__(
        self,
        dir_base_data: str = None,
        dir_base_logs: str = None,
        database_name: str = "projects.db",
        output_dir_name: str = None,
        max_repr_len: int = 25,
        config: Configuration = Configuration(),
        callbacks_activate_project: List[
            Callable[["ProjectsManager", str, Dict[str, str], str], NoReturn]
        ] = None,
        callbacks_create_project: List[
            Callable[["ProjectsManager", str, Dict[str, str], str], NoReturn]
        ] = None,
        callbacks_delete_project: List[
            Callable[["ProjectsManager", str, Dict[str, str], str], NoReturn]
        ] = None,
        callbacks_copy_project: List[
            Callable[["ProjectsManager", str, Dict[str, str], str], NoReturn]
        ] = None,
    ) -> None:
        if callbacks_activate_project is None:
            callbacks_activate_project = []
        if callbacks_create_project is None:
            callbacks_create_project = []
        if callbacks_delete_project is None:
            callbacks_delete_project = []
        if callbacks_copy_project is None:
            callbacks_copy_project = []

        self.file_helper = FileHelper(
            dir_base_data, dir_base_logs, output_dir_name, config
        )
        self.max_repr_len = max_repr_len
        self.callbacks_activate_project = callbacks_activate_project
        self.callbacks_create_project = callbacks_create_project
        self.callbacks_delete_project = callbacks_delete_project
        self.callbacks_copy_project = callbacks_copy_project
        self._active_project: Project = None
        DatabaseHelper.init_db(self.file_helper.dir_base_data / database_name)

    def __iter__(self):
        for project in DatabaseHelper.get_projects():
            yield project

    def __contains__(self, name: str) -> bool:
        return DatabaseHelper.project_exists(name)

    def __len__(self) -> int:
        return DatabaseHelper.get_projects_count()

    def __repr__(self) -> str:
        projects = sorted([project.name for project in self])[: self.max_repr_len]
        projects_fmt = "".join([f"\n\t{project}" for project in projects])
        repr_str = (
            f"bw_projects manager with {len(self)} projects, including:{projects_fmt}"
        )
        if len(self) > self.max_repr_len:
            repr_str += (
                "\n\t...\nTo get full list of projects, use `list(ProjectsManager)`."
            )
        return repr_str

    @staticmethod
    def get_clean_project_name(name: str) -> str:
        """Changes project name to a file-friendly name."""
        return slugify(name)

    @property
    def data_dir(self) -> str:
        """Returns the data directory for active project."""
        return self.file_helper.dir_base_data / self.active_project.name

    @property
    def logs_dir(self) -> str:
        """Returns the logs directory for active project."""
        return self.file_helper.dir_base_logs / self.active_project.name

    @property
    def output_dir(self) -> str:
        """Returns the output directory for active project."""
        return self.file_helper.dir_output

    @property
    def active_project(self) -> Project:
        """Returns the active project."""
        return self._active_project

    def activate_project(self, name: str) -> None:
        """Activates the project with the given name."""
        project_name = ProjectsManager.get_clean_project_name(name)
        self._active_project = DatabaseHelper.get_project(project_name)
        for callback in self.callbacks_activate_project:
            callback(
                self,
                project_name,
                self._active_project.attributes,
                self._active_project.dir_data,
            )

    def create_project(
        self,
        name: str = None,
        attributes: Dict = None,
        exist_ok: bool = False,
        activate: bool = False,
    ) -> Project:
        """Creates a project with the given name."""
        if attributes is None:
            attributes = {}

        project_name = ProjectsManager.get_clean_project_name(name)
        if not DatabaseHelper.project_exists(project_name):
            data_path, logs_path = self.file_helper.create_project_directory(
                project_name, exist_ok
            )
            project = DatabaseHelper.create_project(
                project_name, data_path, logs_path, attributes
            )
        else:
            if not exist_ok:
                raise ProjectExistsError(project_name)
            project = DatabaseHelper.get_project(project_name)

        if activate:
            self.activate_project(project_name)
        for callback in self.callbacks_create_project:
            callback(self, project_name, project.attributes, project.dir_data)
        return project

    def delete_project(
        self, name: str, not_exist_ok: bool = False, delete_dir: bool = True
    ) -> None:
        """Deletes the project with the given name."""
        project_name = ProjectsManager.get_clean_project_name(name)
        if not DatabaseHelper.project_exists(project_name):
            if not not_exist_ok:
                raise DoesNotExist
            return
        project = DatabaseHelper.get_project(project_name)
        DatabaseHelper.delete_project(project_name)
        if delete_dir:
            self.file_helper.delete_project_directory(project_name)
        if self._active_project.name == project_name:
            self._active_project = None
        for callback in self.callbacks_delete_project:
            callback(self, project_name, project.attributes, project.dir_data)

    def copy_project(
        self, new_name: str, dirs_exist_ok: bool = False, switch: bool = True
    ) -> Project:
        """Copy current project to a new project named ``new_name``.
        If ``switch``, switches to new project. Defaults to ``True``."""

        project_name = ProjectsManager.get_clean_project_name(new_name)
        if project_name in self:
            raise ProjectExistsError(project_name)

        data_path, logs_path = self.file_helper.copy_project_directory(
            self.active_project.name, project_name, dirs_exist_ok
        )
        project = DatabaseHelper.copy_project(
            self.active_project.name, project_name, data_path, logs_path
        )
        if switch:
            self.activate_project(project_name)

        for callback in self.callbacks_copy_project:
            callback(self, project_name, project.attributes, project.dir_data)
        return project
