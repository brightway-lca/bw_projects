"""Exceptions module for bw_projects."""
class BWException(BaseException):
    """Base class for exceptions in Brightway."""


class NoActiveProjectError(BWException):
    """No active project is set."""
