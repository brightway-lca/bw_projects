import os
import tempfile
from pathlib import Path

import pytest

from bw_projects import config, ProjectDataset
from bw_projects.errors import NoActiveProject
from bw_projects.project import ProjectManager


###
### Basic setup
###


def test_project_directories(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    assert "foo" in project.dir.name
    for dirname in project._basic_directories:
        assert os.path.isdir(os.path.join(project.dir, dirname))


def test_from_env_var():
    dirpath = tempfile.mkdtemp()
    os.environ["BRIGHTWAY_DIR"] = dirpath
    project = ProjectManager()
    base, logs = project._get_base_directories()
    assert base.name in dirpath
    assert os.path.isdir(base)
    assert os.path.isdir(logs)
    del os.environ["BRIGHTWAY_DIR"]


def test_default_directories_raise_exception(tmpdir):
    project = ProjectManager(tmpdir)
    with pytest.raises(NoActiveProject):
        project.dir
    with pytest.raises(NoActiveProject):
        project.logs_dir


def test_directories(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    assert os.path.isdir(project.dir)
    assert os.path.isdir(project.logs_dir)


def test_repeatedly_set_name_same_value(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.set_current("foo")
    project.set_current("foo")
    assert len(project) == 1
    assert "foo" in project


@pytest.mark.skipif(config._windows, reason="Windows doesn't allow fun")
def test_funny_project_names(tmpdir):
    project = ProjectManager(tmpdir)
    NAMES = [
        "Powerلُلُصّبُلُلصّبُررً ॣ ॣh ॣ ॣ冗",
        "Roses are [0;31mred[0m, violets are [0;34mblue. Hope you enjoy terminal hue",
        "True",
        "None",
        "1.0/0.0",
        "0xabad1dea",
        "!@#$%^&*()`~",
        "<>?:'{}|_+",
        r",./;'[]\-=",
        "Ω≈ç√∫˜µ≤≥÷",
        "田中さんにあげて下さい",
        "｀ｨ(´∀｀∩",
        "👾 🙇 💁 🙅 🙆 🙋 🙎 🙍 ",
        "הָיְתָהtestالصفحات التّحول",
        "　",
    ]
    error_found = False
    for name in NAMES:
        try:
            project.set_current(name)
            assert [x for x in os.listdir(project.dir)]
            print("This is OK:", name)
        except:
            print("This is not OK:", name)
            error_found = True
    if error_found:
        raise ValueError("Oops")


def test_default_request_directory_raises_exception(tmpdir):
    project = ProjectManager(tmpdir)
    with pytest.raises(NoActiveProject):
        project.request_directory("foo")


def test_request_directory(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("New Project")
    project.request_directory("foo")
    assert "foo" in os.listdir(project.dir)


###
### Project deletion
###


def test_delete_default_raises_exception(tmpdir):
    project = ProjectManager(tmpdir)
    with pytest.raises(NoActiveProject):
        project.delete_project()


def test_delete_current_project_with_name(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.delete_project("foo")
    assert project.current != "foo"
    assert "foo" not in project


def test_delete_project_remove_directory(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    foo_dir = project.dir
    project.set_current("bar")
    project.delete_project("foo", delete_dir=True)
    assert not os.path.isdir(foo_dir)
    assert "foo" not in project
    assert project.current == "bar"


def test_delete_project_keep_directory(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    foo_dir = project.dir
    project.set_current("bar")
    project.delete_project("foo")
    assert os.path.isdir(foo_dir)
    assert "foo" not in project
    assert project.current == "bar"


def test_delete_project_with_name(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.set_current("bar")
    project.delete_project("foo")
    assert "foo" not in project
    assert project.current == "bar"


def test_delete_last_project(tmpdir):
    project = ProjectManager(tmpdir)
    assert len(project) == 0
    project.set_current("foo")
    assert len(project) == 1
    project.delete_project()
    assert project.current is None


def test_delete_current_project_no_name(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.delete_project()
    assert "foo" not in project
    assert project.current != "foo"


###
### Set project
###


def test_error_outdated_set_project(tmpdir):
    project = ProjectManager(tmpdir)
    assert project.current is None
    with pytest.raises(AttributeError):
        project.current = "Foo"


def test_set_project_creates_new_project(tmpdir):
    project = ProjectManager(tmpdir)
    other_num = len(project)
    project.set_current("foo")
    assert len(project) == other_num + 1


def test_set_project(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    assert project.current == "foo"


###
### Test magic methods
###


def test_representation(tmpdir):
    project = ProjectManager(tmpdir)
    assert repr(project)
    assert str(project)


def test_default_is_None(tmpdir):
    project = ProjectManager(tmpdir)
    assert project.current is None


def test_contains(tmpdir):
    project = ProjectManager(tmpdir)
    assert project.current is None
    project.set_current("foo")
    assert "foo" in project


def test_len(tmpdir):
    project = ProjectManager(tmpdir)
    assert len(project) == 0
    project.set_current("foo")
    assert len(project) == 1


def test_iterating_over_projects_no_error(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.set_current("bar")
    project.set_current("baz")
    for x in project:
        project.set_current(x.name)
        assert x.name == project.current


###
### Copy project
###


def test_copy_without_project_raises_exception(tmpdir):
    project = ProjectManager(tmpdir)
    with pytest.raises(NoActiveProject):
        project.copy_project("another one")


def test_copy_project_switch_current(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    assert project.current == "foo"
    project.copy_project("another one")
    assert project.current == "another one"


def test_copy_project_no_switch(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("foo")
    project.copy_project("another one", switch=False)
    assert project.current == "foo"
    assert "another one" in project


# TODO: purge delete directories


###
### Project attributes
###
def test_project_attributes(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("test-pr", test=True, tmp=True)
    dataset = ProjectDataset.get(ProjectDataset.name == "test-pr")
    assert dataset
    assert dataset.attributes
    assert dataset.attributes["test"]
    assert dataset.attributes["tmp"]


def test_project_attributes_default(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("default")
    dataset = ProjectDataset.get(ProjectDataset.name == "default")
    assert dataset.attributes == {}


def test_project_attributes_copy_empty(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("default")
    project.copy_project("default-copy", switch=False)
    dataset = ProjectDataset.get(ProjectDataset.name == "default-copy")
    assert dataset.attributes == {}


def test_project_attributes_copy_with_values(tmpdir):
    project = ProjectManager(tmpdir)
    project.set_current("test-pr", test=False, tmp=True, projects=[])
    project.copy_project("test-pr-copy")
    dataset = ProjectDataset.get(ProjectDataset.name == "test-pr-copy")
    assert dataset
    assert dataset.attributes
    assert dataset.attributes["test"] is False
    assert len(dataset.attributes["projects"]) == 0
    assert dataset.attributes["tmp"]
