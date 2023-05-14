"""Helper classes for bw_projects."""
from pathlib import Path
from typing import Dict

from .config import Configuration
from .model import SQLITE_DATABASE, Project


class DatabaseHelper:
    """Helper class for database operations."""

    @staticmethod
    def init_db(database_name: str) -> None:
        """Initializes the database."""
        SQLITE_DATABASE.init(database_name)
        SQLITE_DATABASE.create_tables([Project])

    @staticmethod
    def create_project(name: str, attributes: Dict) -> Project:
        """Creates a project with the given name."""
        return Project.create(name=name, attributes=attributes)

    @staticmethod
    def delete_project(name: str) -> None:
        """Deletes the project with the given name."""
        Project.delete().where(Project.name == name).execute()

    @staticmethod
    def get_project(name: str) -> Project:
        """Returns the project with the given name."""
        return Project.get(Project.name == name)

    @staticmethod
    def get_projects() -> list[Project]:
        """Returns a list of all projects."""
        return Project.select()

    @staticmethod
    def get_projects_count() -> int:
        """Returns the number of projects."""
        return Project.select().count()

    @staticmethod
    def project_exists(name: str) -> bool:
        """Checks if a project with the given name exists."""
        return Project.select().where(Project.name == name).count() > 0


class FileHelper:
    """Helper class for file operations."""

    def __init__(
        self, dir_base: str, output_dir_name: str, config: Configuration
    ) -> None:
        if dir_base is None:
            self.dir_base = config.dir_base
            self.dir_logs = config.dir_logs
        else:
            self.dir_base = Path(dir_base)
            self.dir_logs = self.dir_base / config.dir_relative_logs

        if output_dir_name is None:
            self.output_dir = config.output_dir
        else:
            self.output_dir = Path(output_dir_name)

        self.dirs_relative_logs = config.dir_relative_logs
        self.dirs_basic = config.dirs_basic

        self.dir_base.mkdir(parents=True, exist_ok=True)
        self.dir_logs.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _get_dir_name(self, name: str) -> Path:
        return self.dir_base / name

    def create_project_directory(self, name: str, exists_ok: bool) -> str:
        """Creates a directory for the given project."""
        project_dir = self._get_dir_name(name)
        project_dir.mkdir(parents=True, exist_ok=exists_ok)
        for dir_basic in self.dirs_basic:
            full_dir_basic = project_dir / dir_basic
            full_dir_basic.mkdir(parents=True, exist_ok=exists_ok)
        dir_logs = project_dir / self.dirs_relative_logs
        dir_logs.mkdir(parents=True, exist_ok=exists_ok)
        return project_dir

    def delete_project_directory(self, name: str) -> None:
        """Deletes the directory for the given project."""
        project_dir = self._get_dir_name(name)
        for dir_basic in self.dirs_basic:
            full_dir_basic = project_dir / dir_basic
            full_dir_basic.rmdir()
        dir_logs = project_dir / self.dirs_relative_logs
        dir_logs.rmdir()
        project_dir.rmdir()
