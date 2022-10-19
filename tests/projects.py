import os
import tempfile
from pathlib import Path

import pytest

from bw_projects import config, projects, ProjectDataset
from bw_projects.tests import bw2test

###
### Basic setup
###


@bw2test
def test_project_directories():
    projects.set_current("foo")
    assert "foo" in projects.dir.name
    for dirname in projects._basic_directories:
        assert os.path.isdir(os.path.join(projects.dir, dirname))


@bw2test
def test_from_env_var():
    dirpath = tempfile.mkdtemp()
    os.environ["BRIGHTWAY2_DIR"] = dirpath
    base, logs = projects._get_base_directories()
    assert base.name in dirpath
    assert os.path.isdir(base)
    assert os.path.isdir(logs)
    del os.environ["BRIGHTWAY2_DIR"]


@bw2test
def test_invalid_env_var():
    os.environ["BRIGHTWAY2_DIR"] = "nothing special"
    with pytest.raises(OSError):
        projects._get_base_directories()
    del os.environ["BRIGHTWAY2_DIR"]


@bw2test
def test_invalid_output_env_dir():
    os.environ["BRIGHTWAY2_OUTPUT_DIR"] = "nothing special"
    assert str(projects.dir) in str(projects.output_dir)
    del os.environ["BRIGHTWAY2_OUTPUT_DIR"]


@bw2test
def test_output_env_dir():
    assert Path(os.getcwd()) != projects.output_dir
    os.environ["BRIGHTWAY2_OUTPUT_DIR"] = os.getcwd()
    assert Path(os.getcwd()) == projects.output_dir
    del os.environ["BRIGHTWAY2_OUTPUT_DIR"]


@bw2test
def test_directories():
    assert os.path.isdir(projects.dir)
    assert os.path.isdir(projects.logs_dir)


@bw2test
def test_repeatedly_set_name_same_value():
    projects.set_current("foo")
    projects.set_current("foo")
    projects.set_current("foo")
    assert len(projects) == 3
    assert "foo" in projects


@pytest.mark.skipif(config._windows, reason="Windows doesn't allow fun")
@bw2test
def test_funny_project_names():
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
            projects.set_current(name)
            assert [x for x in os.listdir(projects.dir)]
            print("This is OK:", name)
        except:
            print("This is not OK:", name)
            error_found = True
    if error_found:
        raise ValueError("Oops")


@bw2test
def test_request_directory():
    projects.request_directory("foo")
    assert "foo" in os.listdir(projects.dir)


###
### Project deletion
###


@bw2test
def test_delete_current_project_with_name():
    projects.set_current("foo")
    projects.delete_project("foo")
    assert projects.current != "foo"
    assert "foo" not in projects


@bw2test
def test_delete_project_remove_directory():
    projects.set_current("foo")
    foo_dir = projects.dir
    projects.set_current("bar")
    projects.delete_project("foo", delete_dir=True)
    assert not os.path.isdir(foo_dir)
    assert "foo" not in projects
    assert projects.current == "bar"


@bw2test
def test_delete_project_keep_directory():
    projects.set_current("foo")
    foo_dir = projects.dir
    projects.set_current("bar")
    projects.delete_project("foo")
    assert os.path.isdir(foo_dir)
    assert "foo" not in projects
    assert projects.current == "bar"


@bw2test
def test_delete_project():
    projects.set_current("foo")
    projects.set_current("bar")
    projects.delete_project("foo")
    assert "foo" not in projects
    assert projects.current == "bar"


@bw2test
def test_delete_last_project():
    assert len(projects) == 2
    with pytest.raises(ValueError):
        projects.delete_project()
        projects.delete_project()


@bw2test
def test_delete_current_project_no_name():
    projects.set_current("foo")
    projects.delete_project()
    assert "foo" not in projects
    assert projects.current != "foo"


###
### Set project
###


@bw2test
def test_error_outdated_set_project():
    assert projects.current
    with pytest.raises(AttributeError):
        projects.current = "Foo"


@bw2test
def test_set_project_creates_new_project():
    other_num = len(projects)
    projects.set_current("foo")
    assert len(projects) == other_num + 1


@bw2test
def test_set_project():
    projects.set_current("foo")
    assert projects.current == "foo"


@bw2test
def test_set_project_default_writable():
    pass


@bw2test
def test_set_project_writable_even_if_writable_false():
    pass


@bw2test
def test_set_readonly_project():
    projects.set_current("foo")
    assert not projects.read_only
    projects.set_current("foo", writable=False)
    assert projects.read_only


@bw2test
def test_set_readonly_project_first_time():
    projects.set_current("foo", writable=False)
    assert projects.read_only


###
### Test magic methods
###


@bw2test
def test_representation():
    assert repr(projects)
    assert str(projects)


@bw2test
def test_contains():
    assert "default" in projects
    projects.set_current("foo")
    assert "foo" in projects


@bw2test
def test_len():
    assert len(projects) == 2
    projects.set_current("foo")
    assert len(projects) == 3


@bw2test
def test_iterating_over_projects_no_error():
    projects.set_current("foo")
    projects.set_current("bar")
    projects.set_current("baz")
    for x in projects:
        projects.set_current(x.name)


###
### Copy project
###


@bw2test
def test_copy_project_switch_current():
    projects.copy_project("another one")
    assert projects.current == "another one"


# TODO: purge delete directories
