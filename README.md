# bw_projects

[![PyPI](https://img.shields.io/pypi/v/bw_projects.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/bw_projects.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/bw_projects)][pypi status]
[![License](https://img.shields.io/pypi/l/bw_projects)][license]

[![Read the documentation at https://bw_projects.readthedocs.io/](https://img.shields.io/readthedocs/bw_projects/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/brightway-lca/bw_projects/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/bw_projects/branch/main/graph/badge.svg?token=ZVWBCITI4A)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/bw_projects/
[read the docs]: https://bw_projects.readthedocs.io/
[tests]: https://github.com/brightway-lca/bw_projects/actions?workflow=Tests
[codecov]: https://codecov.io/gh/brightway-lca/bw_projects
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

This is a library to manage subdirectories, so that work on a project can be isolated from other projects. It is designed for use with the [Brightway life cycle assessment](https://brightway.dev/) software framework, but has no dependencies on Brightway and can be used independently.

Project metadata is stored in SQLite using the [Peewee ORM](http://docs.peewee-orm.com/en/latest/). The SQLite file is in the `base_directory`, and project data is stored in subdirectories. By default, [platformdirs](https://github.com/platformdirs/platformdirs) is used to create the `base_directory`, though this can be overridden.

## Installation

Via pip or conda (`conda-forge` channel).

Depends on:

* [peewee](http://docs.peewee-orm.com/en/latest/)
* [platformdirs](https://github.com/platformdirs/platformdirs)
* [python_slugify](https://github.com/un33k/python-slugify)

## Usage

### Initializing the ProjectsManager

```python
from bw_projects import ProjectsManager  # This doesn't create anything yet


projects_manager = ProjectsManager()  # This gets default config and initializes directories and database
```

### Overriding defaults

```python
## You can override default directory by providing a base directory in constructor
## You can also override the default database name
from bw_projects import ProjectsManager

projects_manager = ProjectsManager(dir_base_data="<path/to/your/base/directory>", database_name="projects.db")
```

```python
## You can also override configurations of default directory
from bw_projects import Configuration, ProjectsManager

config = Configuration(
 			app_name: str = "Brightway3",
        	app_author: str = "pycla",
		)
projects_manager = ProjectsManager(config=config)
```

### Callbacks

```python
## You can setup callbacks on projects creation, activation and deletion
from bw_projects import ProjectsManager

def callback_activate_project(manager: ProjectsManager, name: str, attributes: Dict[str, str], dir_path: str):
	print(f"Manager with {len(manager)} projects activated project {name} with {attributes} and {dir_path}.")

projects_manager = ProjectsManager(callbacks_activate_project=callback_activate_project)
```

### Project management

| :exclamation:  Project names may be changed when creating projects  |
|---------------------------------------------------------------------|
```python
## Before calling any project-management feature, the project name is slugified
## You can get the new name of the project by running:
project = projects_manager.get_clean_project_name("Компьютер")
project
>> kompiuter
```

```python
## Create a project without activating it:
projects_manager.create_project("<project_name>")
```

```python
## Create a project and activate it:
projects_manager.create_project("<project_name>", activate=True)
```

```python
## Iterate over projects:
for project in projects_manager:
	print(project.name, project.attributes)
```

```python
## Activate a project:
projects_manager.activate("<project_name>")
```

```python
## Delete a project from SQLite database and deleting the directory:
projects_manager.delete_project("<project_name>")
```

```python
## Delete a project from SQLite database without deleting the directory:
projects_manager.delete_project("<project_name>", delete_dir=False)
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide][Contributor Guide].

## License

Distributed under the terms of the [BSD-2-Clause license][License],
_bw_projects_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue][Issue Tracker] along with a detailed description.


<!-- github-only -->

[License]: https://github.com/brightway-lca/bw_projects/blob/main/LICENSE
[Contributor Guide]: https://github.com/brightway-lca/bw_projects/blob/main/CONTRIBUTING.md
[Issue Tracker]: https://github.com/brightway-lca/bw_projects/issues
