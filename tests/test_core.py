"""Test cases for the __core__ module."""
import pytest
from peewee import DoesNotExist

from bw_projects.core import ProjectsManager
from bw_projects.errors import ProjectExistsError
from bw_projects.helpers import DatabaseHelper


def test_itr_projects(tmpdir) -> None:
    """Tests iterating over projects."""
    projects_manager = ProjectsManager(tmpdir)
    assert not list(projects_manager)  # No projects created yet.

    projects = ["foo", "bar", "baz"]
    for project in projects:
        projects_manager.create_project(project)
    assert [project.name for project in projects_manager] == projects


def test_contains_project(tmpdir) -> None:
    """Tests if projects_manager contains a project."""
    projects_manager = ProjectsManager(tmpdir)
    assert "foo" not in projects_manager  # No projects created yet.

    projects_manager.create_project("foo")
    assert "foo" in projects_manager


def test_activate_project_does_not_exist(tmpdir) -> None:
    """Tests activating non-existent project."""
    with pytest.raises(DoesNotExist):
        ProjectsManager(tmpdir).activate_project("foo")


def test_create_project_not_existing_no_activate(tmpdir) -> None:
    """Tests creating non-existent project without activating."""
    project_name = "foo"
    projects_manager = ProjectsManager(tmpdir)
    projects_manager.create_project(project_name)
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None


def test_create_project_not_existing_activate(tmpdir) -> None:
    """Tests creating non-existent project with activating."""
    project_name = "foo"
    project_attributes = {"bar": "baz"}
    projects_manager = ProjectsManager(tmpdir)
    projects_manager.create_project(
        project_name, attributes=project_attributes, activate=True
    )
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project.name == project_name
    assert projects_manager.active_project.attributes == project_attributes


def test_create_project_existing_not_okay_no_activate(tmpdir) -> None:
    """Tests creating existent project but existing is not okay."""
    project_name = "foo"
    projects_manager = ProjectsManager(tmpdir)
    projects_manager.create_project(project_name)
    with pytest.raises(ProjectExistsError):
        projects_manager.create_project(project_name)


def test_create_project_existing_okay_no_activate(tmpdir) -> None:
    """Tests creating existent project but existing is okay without activating."""
    project_name = "foo"
    projects_manager = ProjectsManager(tmpdir)
    projects_manager.create_project(project_name)
    projects_manager.create_project(project_name, exists_ok=True)
    assert DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None


def test_delete_project_does_not_exist_not_exist_not_okay(tmpdir) -> None:
    """Tests deleting non-existent project but not existing is not okay."""
    with pytest.raises(DoesNotExist):
        ProjectsManager(tmpdir).delete_project("foo", not_exist_ok=False)


def test_delete_project_does_not_exist_not_exist_okay(tmpdir) -> None:
    """Tests deleting non-existent project but not existing is okay."""
    project_name = "foo"
    ProjectsManager(tmpdir).delete_project(project_name)
    assert not DatabaseHelper.project_exists(project_name)


def test_delete_project_existing_and_active(tmpdir) -> None:
    """Tests deleting existent and active project."""
    project_name = "foo"
    projects_manager = ProjectsManager(tmpdir)
    projects_manager.create_project(project_name, activate=True)
    projects_manager.delete_project(project_name)
    assert not DatabaseHelper.project_exists(project_name)
    assert projects_manager.active_project is None
