"""Helper classes for bw_projects."""
import shutil
from pathlib import Path
from typing import Dict, Tuple

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
    def create_project(
        name: str, data_path: str, logs_path: str, attributes: Dict
    ) -> Project:
        """Creates a project with the given name."""
        return Project.create(
            name=name, dir_data=data_path, dir_logs=logs_path, attributes=attributes
        )

    @staticmethod
    def delete_project(name: str) -> None:
        """Deletes the project with the given name."""
        Project.delete().where(Project.name == name).execute()

    @staticmethod
    def copy_project(
        name: str, new_name: str, data_path: str, logs_path: str
    ) -> Project:
        """Copies the project with the given name."""
        project = Project.get(Project.name == name)
        return Project.create(
            name=new_name,
            dir_data=data_path,
            dir_logs=logs_path,
            attributes=project.attributes,
        )

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
        self,
        dir_base_data: str,
        dir_base_logs: str,
        output_dir_name: str,
        config: Configuration,
    ) -> None:
        if dir_base_data is None:
            self.dir_base_data = config.dir_base_data
        else:
            self.dir_base_data = Path(dir_base_data)

        if dir_base_logs is None:
            self.dir_base_logs = config.dir_base_logs
        else:
            self.dir_base_logs = Path(dir_base_logs)

        if output_dir_name is None:
            self.dir_output = config.dir_output
        else:
            self.dir_output = Path(output_dir_name)

        self.dirs_basic = config.dirs_basic

        self.dir_base_data.mkdir(parents=True, exist_ok=True)
        self.dir_base_logs.mkdir(parents=True, exist_ok=True)
        self.dir_output.mkdir(parents=True, exist_ok=True)

    def get_project_data_directory(self, name: str) -> Path:
        """Returns the directory for the given project."""
        return self.dir_base_data / name

    def get_project_logs_directory(self, name: str) -> Path:
        """Returns the directory for the given project."""
        return self.dir_base_logs / name

    def create_project_directory(self, name: str, exist_ok: bool) -> Tuple[str, str]:
        """Creates a directory for the given project."""
        project_data_dir = self.get_project_data_directory(name)
        project_data_dir.mkdir(parents=True, exist_ok=exist_ok)
        for dir_basic in self.dirs_basic:
            full_dir_basic = project_data_dir / dir_basic
            full_dir_basic.mkdir(parents=True, exist_ok=exist_ok)

        project_logs_dir = self.get_project_logs_directory(name)
        project_logs_dir.mkdir(parents=True, exist_ok=exist_ok)

        return project_data_dir, project_logs_dir

    def delete_project_directory(self, name: str) -> None:
        """Deletes the directory for the given project."""
        shutil.rmtree(self.get_project_data_directory(name))
        shutil.rmtree(self.get_project_logs_directory(name))

    def copy_project_directory(
        self, name: str, new_name: str, dirs_exist_ok: bool
    ) -> None:
        """Copies the directory for the given project."""
        new_data_path = self.get_project_data_directory(new_name)
        new_logs_path = self.get_project_logs_directory(new_name)
        shutil.copytree(
            self.get_project_data_directory(name),
            new_data_path,
            dirs_exist_ok=dirs_exist_ok,
        )
        shutil.copytree(
            self.get_project_logs_directory(name),
            new_logs_path,
            dirs_exist_ok=dirs_exist_ok,
        )
        return new_data_path, new_logs_path
