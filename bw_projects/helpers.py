"""Helper classes for bw_projects."""
import os
from pathlib import Path
from typing import Dict, Final, List

import platformdirs
from slugify import slugify

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

    APP_NAME: Final[str] = "Brightway3"
    APP_AUTHOR: Final[str] = "pylca"
    DEFAULT_DIR_BASE: Final[Path] = Path(
        platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    )
    DEFAULT_DIR_LOGS: Final[Path] = Path(
        platformdirs.user_log_dir(APP_NAME, APP_AUTHOR)
    )
    DIR_RELATIVE_LOGS: Final[str] = "logs"

    DIRS_BASIC: Final[List[str]] = [
        "backups",
        "intermediate",
        "lci",
        "processed",
    ]

    def __init__(self, dir_base: str) -> None:
        if dir_base is None:
            self.dir_base = self.DEFAULT_DIR_BASE
            self.dir_logs = self.DEFAULT_DIR_LOGS
        else:
            self.dir_base = Path(dir_base)
            self.dir_logs = self.dir_base / self.DIR_RELATIVE_LOGS
        os.makedirs(self.dir_base, exist_ok=True)
        os.makedirs(self.dir_logs, exist_ok=True)

    def _get_dir_name(self, name: str) -> str:
        return self.dir_base / slugify(name)

    def create_project_directory(self, name: str, exists_ok: bool) -> str:
        """Creates a directory for the given project."""
        project_dir = self._get_dir_name(name)
        os.makedirs(project_dir, exist_ok=exists_ok)
        for dir_basic in self.DIRS_BASIC:
            os.makedirs(project_dir / dir_basic, exist_ok=exists_ok)
        os.makedirs(project_dir / self.DIR_RELATIVE_LOGS, exist_ok=exists_ok)
        return project_dir

    def delete_project_directory(self, name: str) -> None:
        """Deletes the directory for the given project."""
        project_dir = self._get_dir_name(name)
        for dir_basic in self.DIRS_BASIC:
            os.rmdir(project_dir / dir_basic)
        os.rmdir(project_dir / self.DIR_RELATIVE_LOGS)
        os.rmdir(project_dir)
