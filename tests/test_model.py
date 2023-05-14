"""Test cases for the __model__ module."""
import pytest

from bw_projects.model import Project


def test_project_lt() -> None:
    """Tests __lt__ method of Project model."""
    project_1 = Project(name="foo")
    project_2 = Project(name="bar")
    assert project_1 > project_2


def test_project_attributes_dumps() -> None:
    """Tests _attributes_dumps not accepting non-dictionary objects."""
    project_1 = Project(name="foo")
    with pytest.raises(TypeError):
        project_1.attributes = 3
        project_1.save()
