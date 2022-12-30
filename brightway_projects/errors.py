class BWException(BaseException):
    """Base class for exceptions in Brightway"""

    pass


class NoActiveProject(BWException):
    """Current project is None"""

    pass
