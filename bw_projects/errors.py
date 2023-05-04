"""Exceptions for bw_projects."""


class BWProjectsException(BaseException):
    """Base class for exceptions in Brightway."""


class ProjectExistsError(BWProjectsException):
    """A project with this name already exists."""
