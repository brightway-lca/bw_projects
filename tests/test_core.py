"""Test cases for the __core__ module."""
from pathlib import Path
from typing import Dict, Tuple

import pytest
from peewee import DoesNotExist

from bw_projects.core import ProjectsManager
from bw_projects.errors import ProjectExistsError
from bw_projects.helpers import DatabaseHelper


@pytest.fixture(name="base_dirs")
def _base_dirs(tmpdir) -> Tuple[str, str]:
    """Returns a dictionary with base directories."""
    return (
        tmpdir.mkdir("data"),
        tmpdir.mkdir("logs"),
    )


@pytest.fixture(name="projects_manager")
def _projects_manager(base_dirs) -> ProjectsManager:
    """Returns a ProjectsManager instance."""
    return ProjectsManager(base_dirs[0], base_dirs[1])


def test_itr_projects(projects_manager: ProjectsManager) -> None:
    """Tests iterating over projects."""
    assert not list(projects_manager)  # No projects created yet.

    projects = ["foo", "bar", "baz"]
    for project in projects:
        projects_manager.create_project(project)
    assert [project.name for project in projects_manager] == projects


def test_contains_project(projects_manager: ProjectsManager) -> None:
    """Tests if projects_manager contains a project."""
    assert "foo" not in projects_manager  # No projects created yet.

    projects_manager.create_project("foo")
    assert "foo" in projects_manager


def test_repr(projects_manager: ProjectsManager) -> None:
    """Tests representation of projects_manager."""
    assert (
        repr(projects_manager) == "bw_projects manager with 0 projects, including:"
    )  # No projects created yet.

    projects = ["foo", "bar", "baz"]
    for project in projects:
        projects_manager.create_project(project)
    assert (
        repr(projects_manager)
        == "bw_projects manager with 3 projects, including:\n\tbar\n\tbaz\n\tfoo"
    )

    projects_manager.max_repr_len = 2
    assert repr(projects_manager) == (
        "bw_projects manager with 3 projects, including:\n\tbar\n\tbaz\n\t...\n"
        "To get full list of projects, use `list(ProjectsManager)`."
    )


def test_base_dirs(base_dirs) -> None:
    """Tests base directories."""
    project_name = "foo"
    projects_manager = ProjectsManager(base_dirs[0], base_dirs[1])
    projects_manager.create_project(project_name, activate=True)
    assert projects_manager.data_dir == base_dirs[0] / project_name
    assert projects_manager.logs_dir == base_dirs[1] / project_name
    assert projects_manager.output_dir == Path.home()


def test_activate_project_does_not_exist(projects_manager: ProjectsManager) -> None:
    """Tests activating non-existent project."""
    with pytest.raises(DoesNotExist):
        projects_manager.activate_project("foo")


def test_create_project_not_existing_no_activate(
    projects_manager: ProjectsManager,
) -> None:
    """Tests creating non-existent project without activating."""
    project_name = "foo"
    projects_manager.create_project(project_name)
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None


def test_create_project_not_existing_activate_with_callbacks(base_dirs, capsys) -> None:
    """Tests creating non-existent project with activating and callbacks."""

    def callback_activate_project(
        manager: ProjectsManager, name: str, attributes: Dict[str, str], dir_path: str
    ):
        print(
            f"Manager with {len(manager)} projects activated project {name} "
            f"with {attributes} and {dir_path}."
        )

    def callback_create_project(
        manager: ProjectsManager, name: str, attributes: Dict[str, str], dir_path: str
    ):
        print(
            f"Manager with {len(manager)} projects created project {name} "
            f"with {attributes} and {dir_path}."
        )

    data_dir = base_dirs[0]
    logs_dir = base_dirs[1]
    project_name = "foo"
    project_attributes = {"bar": "baz"}
    dir_path = data_dir.join(project_name)
    callback_activate_project_out = (
        f"Manager with 1 projects activated project foo with {project_attributes} "
        f"and {dir_path}."
    )
    callback_create_project_out = (
        f"Manager with 1 projects created project foo with {project_attributes} "
        f"and {dir_path}."
    )
    projects_manager = ProjectsManager(
        data_dir,
        logs_dir,
        callbacks_activate_project=[callback_activate_project],
        callbacks_create_project=[callback_create_project],
    )
    clean_project_name = projects_manager.get_clean_directory_name(project_name)
    projects_manager.create_project(
        project_name, attributes=project_attributes, activate=True
    )
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project.name == clean_project_name
    assert projects_manager.active_project.attributes == project_attributes
    assert projects_manager.active_project.dir_data == data_dir / clean_project_name
    assert projects_manager.active_project.dir_logs == logs_dir / clean_project_name
    assert data_dir.join(project_name).check(dir=True)
    assert logs_dir.join(project_name).check(dir=True)

    out, _ = capsys.readouterr()
    assert out == f"{callback_activate_project_out}\n{callback_create_project_out}\n"


def test_create_project_existing_not_okay_no_activate(
    projects_manager: ProjectsManager,
) -> None:
    """Tests creating existent project but existing is not okay."""
    project_name = "foo"
    projects_manager.create_project(project_name)
    with pytest.raises(ProjectExistsError):
        projects_manager.create_project(project_name)


def test_create_project_slugify_same_name(projects_manager: ProjectsManager) -> None:
    """Tests creating new project but slugify produces name of existing project."""
    projects_manager.create_project("Компьютер")
    with pytest.raises(ProjectExistsError):
        projects_manager.create_project("kompiuter")


def test_create_project_existing_okay_no_activate(
    projects_manager: ProjectsManager,
) -> None:
    """Tests creating existent project but existing is okay without activating."""
    project_name = "foo"
    projects_manager.create_project(project_name)
    projects_manager.create_project(project_name, exist_ok=True)
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None


def test_delete_project_does_not_exist_not_exist_not_okay(
    projects_manager: ProjectsManager,
) -> None:
    """Tests deleting non-existent project but not existing is not okay."""
    with pytest.raises(DoesNotExist):
        projects_manager.delete_project("foo", not_exist_ok=False)


def test_delete_project_does_not_exist_not_exist_okay(
    projects_manager: ProjectsManager,
) -> None:
    """Tests deleting non-existent project but not existing is okay."""
    project_name = "foo"
    projects_manager.delete_project(project_name, not_exist_ok=True)
    assert not DatabaseHelper.project_exists(project_name)


def test_delete_project_existing_and_active_with_callbacks(base_dirs, capsys) -> None:
    """Tests deleting existent and active project with callbacks."""

    def callback_delete_project(
        manager: ProjectsManager, name: str, attributes: Dict[str, str], dir_path: str
    ):
        print(
            f"Manager with {len(manager)} projects deleted project {name} "
            f"with {attributes} and {dir_path}."
        )

    data_dir = base_dirs[0]
    logs_dir = base_dirs[1]
    project_name = "foo"
    dir_path = data_dir.join(project_name)
    callback_delete_project_out = (
        f"Manager with 0 projects deleted project foo with {{}} and {dir_path}."
    )
    projects_manager = ProjectsManager(
        data_dir, logs_dir, callbacks_delete_project=[callback_delete_project]
    )
    projects_manager.create_project(project_name, activate=True)
    projects_manager.delete_project(project_name)
    assert not DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None
    assert data_dir.join(project_name).check(dir=False)
    assert logs_dir.join(project_name).check(dir=False)

    out, _ = capsys.readouterr()
    assert out == f"{callback_delete_project_out}\n"


def test_delete_project_existing_and_active_without_deleting(base_dirs) -> None:
    """Tests deleting existent and active project with no directory deleting."""
    project_name = "foo"
    data_dir = base_dirs[0]
    logs_dir = base_dirs[1]
    projects_manager = ProjectsManager(data_dir, logs_dir)
    projects_manager.create_project(project_name, activate=True)
    projects_manager.delete_project(project_name, delete_dir=False)
    assert not DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None
    assert data_dir.join(project_name).check(dir=True)
    assert logs_dir.join(project_name).check(dir=True)


def test_copy_project_not_existing_dirs_exist_ok_and_switch_with_callbacks(
    base_dirs, capsys
) -> None:
    """Tests copying existent and active project with callbacks."""

    def callback_copy_project(
        manager: ProjectsManager, name: str, attributes: Dict[str, str], dir_path: str
    ):
        print(
            f"Manager with {len(manager)} projects copied project {name} "
            f"with {attributes} and {dir_path}."
        )

    data_dir = base_dirs[0]
    logs_dir = base_dirs[1]
    project_name = "foo"
    new_project_name = "bar"
    project_attributes = {"baz": "qux"}
    new_dir_path = data_dir.join(new_project_name)
    callback_copy_project_out = (
        f"Manager with 2 projects copied project {new_project_name} with "
        f"{project_attributes} and {new_dir_path}."
    )
    projects_manager = ProjectsManager(
        data_dir, logs_dir, callbacks_copy_project=[callback_copy_project]
    )
    projects_manager.create_project(
        project_name, attributes=project_attributes, activate=True
    )
    projects_manager.copy_project(new_project_name, dirs_exist_ok=True, switch=True)
    assert DatabaseHelper.project_exists(project_name)
    assert DatabaseHelper.project_exists(new_project_name)
    assert projects_manager.active_project.name == new_project_name
    assert projects_manager.active_project.attributes == project_attributes
    assert projects_manager.active_project.dir_data == new_dir_path
    assert projects_manager.active_project.dir_logs == logs_dir / new_project_name
    assert data_dir.join(project_name).check(dir=True)
    assert data_dir.join(new_project_name).check(dir=True)
    assert logs_dir.join(project_name).check(dir=True)
    assert logs_dir.join(new_project_name).check(dir=True)

    out, _ = capsys.readouterr()
    assert out == f"{callback_copy_project_out}\n"


def test_copy_project_existing_dirs_exist_ok_and_switch(
    projects_manager: ProjectsManager,
) -> None:
    """Tests copying existent and active project with no directory deleting."""
    project_name = "foo"
    projects_manager.create_project(project_name, activate=True)
    with pytest.raises(ProjectExistsError):
        projects_manager.copy_project(
            project_name,
            dirs_exist_ok=True,
            switch=True,
        )


def test_request_directory(projects_manager: ProjectsManager) -> None:
    """Tests requesting a directory."""
    dirname = "bar"
    project_name = "foo"
    projects_manager.create_project(project_name, activate=True)
    assert (
        projects_manager.request_directory(dirname)
        == projects_manager.data_dir / dirname
    )
