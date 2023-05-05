"""Test cases for the __model__ module."""
from bw_projects.model import Project


def test_project_lt() -> None:
    """Tests __lt__ method of Project model."""
    project_1 = Project(name="foo")
    project_2 = Project(name="bar")
    assert project_1 > project_2
